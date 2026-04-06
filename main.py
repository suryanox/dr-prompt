import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import re

app = FastAPI(title="DrPrompt", description="A doctor for your system prompts.")
client = AsyncOpenAI()

nlp = spacy.load("en_core_web_sm")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

REDUNDANCY_THRESHOLD = 0.72
MODEL = "gpt-5.4"

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

GRADE_MAP = [
    (90, "A", "Excellent"),
    (80, "B", "Good"),
    (70, "C", "Needs Work"),
    (50, "D", "Poor"),
    (0,  "F", "Critical"),
]


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
    severity: str


class AmbiguousPhrase(BaseModel):
    phrase: str
    reason: str
    suggestion: str
    rewrite: str
    severity: str


class CoverageGap(BaseModel):
    gap: str
    example: str
    impact: str


class QuickFix(BaseModel):
    issue: str
    fix: str
    category: str


class TopIssue(BaseModel):
    title: str
    description: str
    severity: str
    category: str


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


class PromptStats(BaseModel):
    word_count: int
    sentence_count: int
    instruction_count: int
    avg_words_per_sentence: float
    estimated_tokens: int


class ContradictionAnalysis(BaseModel):
    contradictions: list[Contradiction]


class AmbiguityAnalysis(BaseModel):
    ambiguous_phrases: list[AmbiguousPhrase]
    coverage_gaps: list[CoverageGap]


class QuickFixAnalysis(BaseModel):
    quick_fixes: list[QuickFix]
    top_issues: list[TopIssue]


class AnalysisResponse(BaseModel):
    overall_score: int
    grade: str
    verdict: str
    summary: str
    stats: PromptStats
    top_issues: list[TopIssue]
    quick_fixes: list[QuickFix]
    clarity: ClarityReport
    redundancy: RedundancyReport
    contradictions: list[Contradiction]
    ambiguous_phrases: list[AmbiguousPhrase]
    coverage_gaps: list[CoverageGap]


def get_grade(score: int) -> tuple[str, str]:
    for threshold, grade, verdict in GRADE_MAP:
        if score >= threshold:
            return grade, verdict
    return "F", "Critical"


def parse_doc(text: str):
    return nlp(text)


def split_sentences(doc) -> list[str]:
    return [sent.text.strip() for sent in doc.sents if len(sent.text.split()) > 2]


def compute_stats(doc, text: str, instruction_count: int) -> PromptStats:
    sentences = list(doc.sents)
    words = text.split()
    sentence_count = len(sentences)
    word_count = len(words)
    avg_words = round(word_count / max(sentence_count, 1), 1)
    estimated_tokens = round(len(text) / 4)

    return PromptStats(
        word_count=word_count,
        sentence_count=sentence_count,
        instruction_count=instruction_count,
        avg_words_per_sentence=avg_words,
        estimated_tokens=estimated_tokens,
    )


def count_instructions(doc) -> int:
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
    return count if count > 0 else len(list(doc.sents))


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


def clarity_score(doc, text: str) -> ClarityReport:
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


def redundancy_score(doc) -> RedundancyReport:
    sentences = split_sentences(doc)
    if len(sentences) < 2:
        return RedundancyReport(score=100, redundant_pairs=[], redundancy_percent=0)

    embeddings = embedder.encode(sentences)
    sim_matrix = cosine_similarity(embeddings)

    redundant_pairs = []
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            sim = float(sim_matrix[i][j])
            if sim > REDUNDANCY_THRESHOLD:
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


async def fetch_contradictions(system_prompt: str) -> ContradictionAnalysis:
    response = await client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert prompt analyst. Find logical contradictions between instructions. "
                    "For each contradiction assign a severity: 'high' if it will cause unpredictable behavior, "
                    "'medium' if it causes inconsistency, 'low' if it is a minor conflict."
                ),
            },
            {
                "role": "user",
                "content": f"Find all contradictions in this system prompt:\n\n{system_prompt}",
            },
        ],
        response_format=ContradictionAnalysis,
        temperature=0.1,
    )
    return response.choices[0].message.parsed


async def fetch_ambiguity(system_prompt: str) -> AmbiguityAnalysis:
    response = await client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert prompt analyst. "
                    "For ambiguous phrases: assign severity ('high', 'medium', 'low') and provide a concrete rewrite. "
                    "For coverage gaps: assign impact ('high', 'medium', 'low') based on how likely the gap is to occur."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Analyze this system prompt for:\n"
                    f"1. Ambiguous phrases that could be interpreted in multiple ways — include a concrete rewrite for each\n"
                    f"2. User situations or edge cases this prompt does NOT handle\n\n"
                    f"System prompt:\n{system_prompt}"
                ),
            },
        ],
        response_format=AmbiguityAnalysis,
        temperature=0.1,
    )
    return response.choices[0].message.parsed


async def fetch_quick_fixes_and_top_issues(system_prompt: str) -> QuickFixAnalysis:
    response = await client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert prompt engineer. "
                    "Identify the top 3 most impactful quick fixes and the top 3 most critical issues in a system prompt. "
                    "Quick fixes must be concrete and immediately actionable — include the exact text to use. "
                    "Top issues must be the single most critical problems ranked by severity."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"For this system prompt provide:\n"
                    f"1. Top 3 quick fixes — each with the exact replacement text ready to use\n"
                    f"2. Top 3 most critical issues — each with title, description, severity, and category\n\n"
                    f"Categories for issues: 'clarity', 'redundancy', 'contradiction', 'ambiguity', 'coverage'\n\n"
                    f"System prompt:\n{system_prompt}"
                ),
            },
        ],
        response_format=QuickFixAnalysis,
        temperature=0.1,
    )
    return response.choices[0].message.parsed


async def fetch_summary(system_prompt: str) -> str:
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": f"Summarize in one sentence what this system prompt is trying to do:\n\n{system_prompt}",
            }
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()


def compute_overall_score(
    clarity: ClarityReport,
    redundancy: RedundancyReport,
    contradictions: list,
    ambiguous_phrases: list,
    coverage_gaps: list,
    instruction_count: int,
) -> int:
    contradiction_penalty = len(contradictions) * 8
    ambiguity_penalty = min(len(ambiguous_phrases) * 2, 20)
    gap_penalty = min(len(coverage_gaps) * 2, 20)
    density_penalty = max(0, instruction_count - 15) * 1.0

    base = clarity.score * 0.4 + redundancy.score * 0.3 + 70 * 0.3
    final = max(0, min(100, round(
        base - contradiction_penalty - ambiguity_penalty - gap_penalty - density_penalty
    )))
    return final


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: PromptRequest):
    if not request.system_prompt.strip():
        raise HTTPException(status_code=400, detail="system_prompt cannot be empty")

    try:
        doc = parse_doc(request.system_prompt)

        clarity = clarity_score(doc, request.system_prompt)
        redundancy = redundancy_score(doc)
        instruction_count = count_instructions(doc)
        stats = compute_stats(doc, request.system_prompt, instruction_count)

        contradictions_result, ambiguity_result, quick_fix_result, summary = await asyncio.gather(
            fetch_contradictions(request.system_prompt),
            fetch_ambiguity(request.system_prompt),
            fetch_quick_fixes_and_top_issues(request.system_prompt),
            fetch_summary(request.system_prompt),
        )

        overall = compute_overall_score(
            clarity,
            redundancy,
            contradictions_result.contradictions,
            ambiguity_result.ambiguous_phrases,
            ambiguity_result.coverage_gaps,
            instruction_count,
        )

        grade, verdict = get_grade(overall)

        return AnalysisResponse(
            overall_score=overall,
            grade=grade,
            verdict=verdict,
            summary=summary,
            stats=stats,
            top_issues=quick_fix_result.top_issues,
            quick_fixes=quick_fix_result.quick_fixes,
            clarity=clarity,
            redundancy=redundancy,
            contradictions=contradictions_result.contradictions,
            ambiguous_phrases=ambiguity_result.ambiguous_phrases,
            coverage_gaps=ambiguity_result.coverage_gaps,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)