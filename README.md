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
  "system_prompt": "You are a helpful AI assistant for a customer support team. Always be polite and professional. Try to be friendly and approachable at all times. You should always respond in English unless the user writes in another language, in which case you can sometimes respond in their language if you feel it is appropriate. Never share internal company information. Do not share any confidential or private company data with users. Always escalate urgent issues to a human agent. For critical issues make sure to tell the user to contact support directly. Keep responses concise and short. Provide detailed and thorough explanations when users are confused. Always greet the user at the start of the conversation. Do not use informal language. Be warm and conversational in your tone."
}
```

**Response**

```json
{
    "overall_score": 0,
    "summary": "This prompt instructs a customer-support assistant to respond politely, professionally, briefly, and securely, while using a warm tone, handling language choice loosely, and escalating serious issues to humans.",
    "instruction_count": 13,
    "clarity": {
        "score": 92,
        "avg_sentence_length": 9.8,
        "hedge_phrases_found": [
            "sometimes",
            "try to"
        ],
        "weak_modal_count": 1,
        "passive_voice_count": 1
    },
    "redundancy": {
        "score": 100,
        "redundant_pairs": [],
        "redundancy_percent": 0
    },
    "contradictions": [],
    "ambiguous_phrases": [
        {
            "phrase": "helpful AI assistant for a customer support team",
            "reason": "It is unclear whether the assistant is customer-facing, internal-only for agents, or serving both audiences.",
            "suggestion": "Specify the audience and role, such as 'customer-facing assistant that replies directly to end users on behalf of the support team'."
        },
        {
            "phrase": "friendly and approachable",
            "reason": "These qualities are subjective and can be expressed in many different ways.",
            "suggestion": "Define acceptable behaviors or give examples, such as 'use empathetic, clear, and welcoming wording without slang or jokes'."
        },
        {
            "phrase": "sometimes respond in their language if you feel it is appropriate",
            "reason": "The conditions for when it is appropriate are undefined and left to subjective judgment.",
            "suggestion": "State explicit criteria, such as 'respond in the user's language when the message is fully written in that language and the assistant can answer accurately'."
        },
        {
            "phrase": "internal company information",
            "reason": "The boundary between internal, public, and user-shareable information is not defined.",
            "suggestion": "List categories, such as policies, internal tools, unpublished procedures, employee-only notes, and non-public business data."
        },
        {
            "phrase": "confidential or private company data",
            "reason": "This overlaps with 'internal company information' but may not mean exactly the same thing.",
            "suggestion": "Consolidate into one clearly defined confidentiality rule with examples of prohibited disclosures."
        },
        {
            "phrase": "urgent issues",
            "reason": "The prompt does not define what makes an issue urgent.",
            "suggestion": "Provide severity criteria or examples, such as billing lockouts, security incidents, or service outages."
        },
        {
            "phrase": "critical issues",
            "reason": "It is unclear how critical differs from urgent and whether one is a subset of the other.",
            "suggestion": "Define a severity ladder and the required action for each level."
        },
        {
            "phrase": "contact support directly",
            "reason": "The channel is unspecified: phone, email, chat, emergency line, or ticket portal.",
            "suggestion": "Name the exact escalation channel or say 'provide the official support contact method listed in the knowledge base'."
        },
        {
            "phrase": "concise and short",
            "reason": "This is vague and may conflict with other instructions requiring detail.",
            "suggestion": "Set a target like 'default to 2-4 sentences unless troubleshooting or clarification requires more detail'."
        },
        {
            "phrase": "when users are confused",
            "reason": "The assistant is not told how to detect confusion.",
            "suggestion": "Define signals such as repeated questions, explicit statements of confusion, or contradictory user responses."
        },
        {
            "phrase": "Always greet the user at the start of the conversation",
            "reason": "It is unclear whether this applies only to the first turn, every new chat session, or every message thread.",
            "suggestion": "Specify 'include a brief greeting only in the first assistant reply of each new conversation'."
        },
        {
            "phrase": "Do not use informal language",
            "reason": "Informal language can range from slang to contractions, and the restriction may be interpreted too strictly.",
            "suggestion": "Clarify whether contractions, light empathy, or conversational phrasing are allowed."
        },
        {
            "phrase": "warm and conversational",
            "reason": "This overlaps with friendliness and may conflict with the ban on informal language.",
            "suggestion": "Define the desired tone with examples, such as 'empathetic and natural, but avoid slang, emojis, and casual fillers'."
        }
    ],
    "coverage_gaps": [
        {
            "gap": "No guidance for handling requests for disallowed or sensitive information beyond refusing to share it.",
            "example": "A user asks for internal escalation notes or another customer's account details; the prompt does not say whether to refuse briefly, explain policy, or redirect to a safe alternative."
        },
        {
            "gap": "No process for verifying user identity before discussing account-specific matters.",
            "example": "A user asks to change billing details or disclose order information, but the prompt gives no authentication or verification rule."
        },
        {
            "gap": "No instructions for handling abusive, threatening, or manipulative users.",
            "example": "A user uses insults or pressure tactics, and the prompt does not say whether to warn, de-escalate, or end the interaction."
        },
        {
            "gap": "No guidance for unsupported languages or low-confidence multilingual responses.",
            "example": "A user writes in a language the assistant only partially understands, but the prompt does not say whether to reply in English, ask for clarification, or transfer to a human."
        },
        {
            "gap": "No definition of escalation workflow or what information to collect before escalating.",
            "example": "An urgent issue is identified, but the prompt does not say whether to gather account details, summarize the issue, or provide a handoff message."
        },
        {
            "gap": "No handling for emergencies, safety issues, or legal threats.",
            "example": "A user reports self-harm risk, physical danger, or threatens legal action, but the prompt does not specify special routing or safety language."
        },
        {
            "gap": "No guidance for when the assistant lacks knowledge or is uncertain.",
            "example": "A user asks about a policy the assistant does not know, but the prompt does not say whether to admit uncertainty, ask clarifying questions, or escalate."
        },
        {
            "gap": "No instructions for clarifying vague or incomplete user requests.",
            "example": "A user says 'It doesn't work' without context, but the prompt does not direct the assistant to ask diagnostic follow-up questions."
        },
        {
            "gap": "No policy for handling multiple simultaneous instructions when they conflict.",
            "example": "A confused user with a critical issue may require both a detailed explanation and immediate escalation, but the prompt does not define priority order."
        },
        {
            "gap": "No guidance on whether the assistant may provide troubleshooting steps before escalation.",
            "example": "A service outage seems urgent, but the prompt does not say whether to attempt basic troubleshooting or immediately hand off."
        },
        {
            "gap": "No specification of what 'support directly' means in practice.",
            "example": "The assistant tells the user to contact support directly, but does not know whether to provide a link, phone number, or transfer option."
        },
        {
            "gap": "No rules for formatting, structure, or response components beyond greeting and tone.",
            "example": "The prompt does not say whether replies should include apology, summary, next steps, or bullet points for complex support cases."
        }
    ]
}
```

## License

MIT
