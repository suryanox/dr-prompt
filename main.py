from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import re
import json

app = FastAPI()
client = OpenAI()


class PromptRequest(BaseModel):
    system_prompt: str


def clarity_score(text: str) -> dict:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    words = text.split()

    vague_words = {"some", "maybe", "try", "generally", "usually", "often", "sometimes",
                   "might", "could", "probably", "perhaps", "fairly", "quite", "rather",
                   "somewhat", "mostly", "largely", "various", "certain", "appropriate"}

    vague_found = [w for w in words if w.lower().strip(".,!?") in vague_words]
    avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    passive_matches = re.findall(r'\b(is|are|was|were|be|been|being)\s+\w+ed\b', text)

    penalty = len(vague_found) * 3 + len(passive_matches) * 2 + max(0, avg_sentence_length - 20) * 1.5
    score = max(0, min(100, round(100 - penalty)))

    return {
        "score": score,
        "avg_sentence_length": round(avg_sentence_length, 1),
        "vague_words_found": list(set(vague_found)),
        "passive_voice_count": len(passive_matches),
    }


def redundancy_score(text: str) -> dict:
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text.strip()) if len(s.split()) > 3]

    def to_set(s):
        return set(re.sub(r'[^\w\s]', '', s.lower()).split())

    redundant_pairs = []
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            a, b = to_set(sentences[i]), to_set(sentences[j])
            if not a or not b:
                continue
            overlap = len(a & b) / len(a | b)
            if overlap > 0.6:
                redundant_pairs.append({
                    "sentence_1": sentences[i],
                    "sentence_2": sentences[j],
                    "similarity": round(overlap, 2)
                })

    redundancy_pct = round(len(redundant_pairs) / max(len(sentences), 1) * 100)
    score = max(0, min(100, 100 - redundancy_pct * 2))

    return {
        "score": score,
        "redundant_pairs": redundant_pairs,
        "redundancy_percent": redundancy_pct,
    }


def llm_analysis(system_prompt: str) -> dict:
    analysis_prompt = f"""Analyze this system prompt and return ONLY a valid JSON object with exactly this structure:

{{
  "contradictions": [
    {{"sentence_1": "...", "sentence_2": "...", "reason": "..."}}
  ],
  "ambiguous_phrases": [
    {{"phrase": "...", "reason": "...", "suggestion": "..."}}
  ],
  "coverage_gaps": [
    {{"gap": "...", "example": "..."}}
  ],
  "one_line_summary": "..."
}}

Rules:
- contradictions: pairs of instructions that conflict with each other
- ambiguous_phrases: phrases that could be interpreted in multiple ways
- coverage_gaps: user situations or inputs this prompt does NOT handle but should
- one_line_summary: one sentence describing what this prompt is trying to do
- Return empty arrays if nothing found
- Return ONLY the JSON, no markdown, no explanation

System prompt to analyze:
\"\"\"{system_prompt}\"\"\""""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": analysis_prompt}],
        temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r'^```json|^```|```$', '', raw, flags=re.MULTILINE).strip()

    return json.loads(raw)


def compute_overall_score(clarity: dict, redundancy: dict, llm: dict) -> int:
    contradiction_penalty = len(llm.get("contradictions", [])) * 10
    ambiguity_penalty = len(llm.get("ambiguous_phrases", [])) * 5
    gap_penalty = len(llm.get("coverage_gaps", [])) * 5

    base = (clarity["score"] * 0.4 + redundancy["score"] * 0.3 + 70 * 0.3)
    final = max(0, min(100, round(base - contradiction_penalty - ambiguity_penalty - gap_penalty)))
    return final


@app.post("/analyze")
def analyze(request: PromptRequest):
    if not request.system_prompt.strip():
        raise HTTPException(status_code=400, detail="system_prompt cannot be empty")

    try:
        clarity = clarity_score(request.system_prompt)
        redundancy = redundancy_score(request.system_prompt)
        llm = llm_analysis(request.system_prompt)
        overall = compute_overall_score(clarity, redundancy, llm)

        return {
            "overall_score": overall,
            "summary": llm.get("one_line_summary", ""),
            "clarity": clarity,
            "redundancy": redundancy,
            "contradictions": llm.get("contradictions", []),
            "ambiguous_phrases": llm.get("ambiguous_phrases", []),
            "coverage_gaps": llm.get("coverage_gaps", []),
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="Failed to parse LLM response as JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
