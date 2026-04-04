# 🩺 DrPrompt

> A doctor for your system prompts. Diagnose clarity, redundancy, contradictions, and coverage gaps in seconds.

## What is DrPrompt?

System prompts are the backbone of every LLM application — but most are written once, never tested, and silently broken. DrPrompt is a REST API that takes any system prompt and returns a structured diagnostic report, exposing issues that are invisible to the naked eye.

## Diagnosis Metrics

| Metric | How it works |
|---|---|
| **Overall Score** | 0–100 health score combining all metrics |
| **Clarity** | Detects vague words, passive voice, and long sentences |
| **Redundancy** | Finds sentences that say the same thing twice |
| **Contradictions** | Flags instructions that conflict with each other |
| **Ambiguous Phrases** | Surfaces phrases with multiple possible interpretations |
| **Coverage Gaps** | Identifies user situations the prompt doesn't handle |

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Set your OpenAI API key

```bash
export OPENAI_API_KEY=sk-...
```

### 3. Run the server

```bash
python main.py
```

Server runs at `http://localhost:8000`.

## API

### `POST /analyze`

Analyze a system prompt and return a full diagnostic report.

**Request**

```json
{
  "system_prompt": "You are a helpful assistant..."
}
```

**Response**

```json
{
  "overall_score": 61,
  "summary": "A customer support assistant prompt with conflicting tone and verbosity instructions.",
  "clarity": {
    "score": 72,
    "avg_sentence_length": 18.4,
    "vague_words_found": ["sometimes", "generally", "try"],
    "passive_voice_count": 2
  },
  "redundancy": {
    "score": 60,
    "redundant_pairs": [
      {
        "sentence_1": "Never share internal company information.",
        "sentence_2": "Do not share any confidential or private company data.",
        "similarity": 0.74
      }
    ],
    "redundancy_percent": 20
  },
  "contradictions": [
    {
      "sentence_1": "Keep responses concise and short.",
      "sentence_2": "Provide detailed and thorough explanations when users are confused.",
      "reason": "Conciseness and detailed explanations are directly at odds with no conditional logic to resolve the conflict."
    }
  ],
  "ambiguous_phrases": [
    {
      "phrase": "urgent issues",
      "reason": "No definition of what constitutes an urgent issue.",
      "suggestion": "Define urgency explicitly, e.g. billing failures, account lockouts, or data loss."
    }
  ],
  "coverage_gaps": [
    {
      "gap": "Abusive or hostile users",
      "example": "A user sends threatening or offensive messages."
    }
  ]
}
```

## License

MIT
