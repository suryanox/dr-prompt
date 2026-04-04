from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import re

app = FastAPI(title="DrPrompt", description="A doctor for your system prompts.")
client = OpenAI()

nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

HEDGE_PATTERNS = [
    r"\btry to\b", r"\bfeel free to\b", r"\bas needed\b", r"\bwhere relevant\b",
    r"\bwhere appropriate\b", r"\bif possible\b", r"\bwhen possible\b",
    r"\bin some cases\b", r"\bin certain situations\b", r"\bgenerally speaking\b",
    r"\bfor the most part\b", r"\bto some extent\b", r"\bif applicable\b",
    r"\bmore or less\b", r"\bkind of\b", r"\bsort of\b", r"\ba bit\b",
]

WEAK_MODALS = re.compile(
    r"\b(might|could|may|perhaps|probably|possibly|sometimes|often|usually|"
    r"generally|mostly|largely|fairly|quite|rather|somewhat|various|certain)\b",
    re.IGNORECASE,
)


class PromptRequest(BaseModel):
    system_prompt: str


class RedundantPair(BaseModel):
    sentence_1: str
    sentence_2: str
    similarity: float


class Contradiction(BaseModel):
    sentence_1: str
    sentence_2: str
    reason: str


class AmbiguousPhrase(BaseModel):
    phrase: str
    reason: str
    suggestion: str


class CoverageGap(BaseModel):
    gap: str
    example: str


class ClarityReport(BaseModel):
    score: int
    avg_sentence_length: float
    hedge_phrases_found: list[str]
    weak_modal_count: int
    passive_voice_count: int


class RedundancyReport(BaseModel):
    score: int
    redundant_pairs: list[RedundantPair]
    redundancy_percent: int


class LLMAnalysis(BaseModel):
    contradictions: list[Contradiction]
    ambiguous_phrases: list[AmbiguousPhrase]
    coverage_gaps: list[CoverageGap]
    one_line_summary: str


class AnalysisResponse(BaseModel):
    overall_score: int
    summary: str
    instruction_count: int
    clarity: ClarityReport
    redundancy: RedundancyReport
    contradictions: list[Contradiction]
    ambiguous_phrases: list[AmbiguousPhrase]
    coverage_gaps: list[CoverageGap]


def split_sentences(text: str) -> list[str]:
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents if len(sent.text.split()) > 2]


def count_instructions(text: str) -> int:
    doc = nlp(text)
    count = 0
    for sent in doc.sents:
        for token in sent:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                if token.tag_ in ("VB", "VBP") or any(
                    c.dep_ == "nsubj" and c.text.lower() in ("you", "model", "assistant")
                    for c in token.children
                ):
                    count += 1
                    break
    return max(count, len(list(doc.sents)))


def detect_passive_voice(doc) -> int:
    return sum(1 for token in doc if token.dep_ == "nsubjpass")


def detect_hedge_phrases(text: str) -> list[str]:
    found = []
    for pattern in HEDGE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found.extend(matches)
    weak_modals = WEAK_MODALS.findall(text)
    found.extend(weak_modals)
    return list(set(w.lower() for w in found))


def clarity_score(text: str) -> ClarityReport:
    doc = nlp(text)
    sentences = list(doc.sents)

    avg_len = sum(len(s.text.split()) for s in sentences) / max(len(sentences), 1)
    passive_count = detect_passive_voice(doc)
    hedge_phrases = detect_hedge_phrases(text)
    weak_modal_count = len(WEAK_MODALS.findall(text))

    penalty = (
        len(hedge_phrases) * 2.5
        + passive_count * 3
        + max(0, avg_len - 20) * 1.5
    )
    score = max(0, min(100, round(100 - penalty)))

    return ClarityReport(
        score=score,
        avg_sentence_length=round(avg_len, 1),
        hedge_phrases_found=hedge_phrases,
        weak_modal_count=weak_modal_count,
        passive_voice_count=passive_count,
    )


def redundancy_score(text: str) -> RedundancyReport:
    sentences = split_sentences(text)
    if len(sentences) < 2:
        return RedundancyReport(score=100, redundant_pairs=[], redundancy_percent=0)

    embeddings = embedder.encode(sentences)
    sim_matrix = cosine_similarity(embeddings)

    redundant_pairs = []
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            sim = float(sim_matrix[i][j])
            if sim > 0.82:
                redundant_pairs.append(RedundantPair(
                    sentence_1=sentences[i],
                    sentence_2=sentences[j],
                    similarity=round(sim, 3),
                ))

    redundancy_pct = round(len(redundant_pairs) / max(len(sentences), 1) * 100)
    score = max(0, min(100, 100 - redundancy_pct * 2))

    return RedundancyReport(
        score=score,
        redundant_pairs=redundant_pairs,
        redundancy_percent=redundancy_pct,
    )


def llm_analysis(system_prompt: str) -> LLMAnalysis:
    contradiction_response = client.beta.chat.completions.parse(
        model="gpt-5.4",
        messages=[
            {
                "role": "system",
                "content": "You are an expert prompt analyst. Find logical contradictions between instructions.",
            },
            {
                "role": "user",
                "content": (
                    f"Find all pairs of instructions that directly contradict each other in this system prompt.\n\n"
                    f"System prompt:\n{system_prompt}"
                ),
            },
        ],
        response_format=LLMAnalysis,
        temperature=0.1,
    )

    ambiguity_response = client.beta.chat.completions.parse(
        model="gpt-5.4",
        messages=[
            {
                "role": "system",
                "content": "You are an expert prompt analyst. Find ambiguous phrases and coverage gaps.",
            },
            {
                "role": "user",
                "content": (
                    f"Analyze this system prompt for:\n"
                    f"1. Ambiguous phrases that could be interpreted in multiple ways\n"
                    f"2. User situations or edge cases this prompt does NOT handle\n"
                    f"3. A one-line summary of what this prompt does\n\n"
                    f"System prompt:\n{system_prompt}"
                ),
            },
        ],
        response_format=LLMAnalysis,
        temperature=0.1,
    )

    contradictions = contradiction_response.choices[0].message.parsed.contradictions
    ambiguous_phrases = ambiguity_response.choices[0].message.parsed.ambiguous_phrases
    coverage_gaps = ambiguity_response.choices[0].message.parsed.coverage_gaps
    summary = ambiguity_response.choices[0].message.parsed.one_line_summary

    return LLMAnalysis(
        contradictions=contradictions,
        ambiguous_phrases=ambiguous_phrases,
        coverage_gaps=coverage_gaps,
        one_line_summary=summary,
    )


def compute_overall_score(
    clarity: ClarityReport,
    redundancy: RedundancyReport,
    llm: LLMAnalysis,
    instruction_count: int,
) -> int:
    contradiction_penalty = len(llm.contradictions) * 10
    ambiguity_penalty = len(llm.ambiguous_phrases) * 5
    gap_penalty = len(llm.coverage_gaps) * 4
    density_penalty = max(0, instruction_count - 15) * 1.5

    base = clarity.score * 0.4 + redundancy.score * 0.3 + 70 * 0.3
    final = max(0, min(100, round(
        base - contradiction_penalty - ambiguity_penalty - gap_penalty - density_penalty
    )))
    return final


@app.post("/analyze", response_model=AnalysisResponse)
def analyze(request: PromptRequest):
    if not request.system_prompt.strip():
        raise HTTPException(status_code=400, detail="system_prompt cannot be empty")

    try:
        clarity = clarity_score(request.system_prompt)
        redundancy = redundancy_score(request.system_prompt)
        llm = llm_analysis(request.system_prompt)
        instruction_count = count_instructions(request.system_prompt)
        overall = compute_overall_score(clarity, redundancy, llm, instruction_count)

        return AnalysisResponse(
            overall_score=overall,
            summary=llm.one_line_summary,
            instruction_count=instruction_count,
            clarity=clarity,
            redundancy=redundancy,
            contradictions=llm.contradictions,
            ambiguous_phrases=llm.ambiguous_phrases,
            coverage_gaps=llm.coverage_gaps,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)