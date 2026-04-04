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
    "overall_score": 43,
    "summary": "It instructs the assistant to act as a polite, professional customer support agent that is warm but not informal, usually responds in English, protects confidential company information, escalates urgent or critical issues to humans, greets users initially, and aims to be concise while still giving fuller explanations when needed.",
    "instruction_count": 10,
    "clarity": {
        "score": 92,
        "avg_sentence_length": 9.8,
        "hedge_phrases_found": [
            "try to",
            "sometimes"
        ],
        "weak_modal_count": 1,
        "passive_voice_count": 1
    },
    "redundancy": {
        "score": 84,
        "redundant_pairs": [
            {
                "sentence_1": "Never share internal company information.",
                "sentence_2": "Do not share any confidential or private company data with users.",
                "similarity": 0.755
            }
        ],
        "redundancy_percent": 8
    },
    "contradictions": [],
    "ambiguous_phrases": [
        {
            "phrase": "helpful AI assistant for a customer support team",
            "reason": "It is unclear whether the assistant is speaking directly to customers, assisting internal support agents, or both. The allowed scope of actions and information may differ significantly.",
            "suggestion": "Specify the audience and role, e.g. 'You assist external customers with general support questions' or 'You assist internal support agents in drafting responses to customers.'"
        },
        {
            "phrase": "Always be polite and professional",
            "reason": "These are broad style requirements without operational definitions. Different writers may interpret them differently, especially in complaints, abuse, or crisis situations.",
            "suggestion": "Define expected behaviors, such as 'Use respectful language, avoid blame, acknowledge frustration, and avoid slang or sarcasm.'"
        },
        {
            "phrase": "Try to be friendly and approachable at all times",
            "reason": "'Try to' weakens the instruction, while 'at all times' implies no exceptions. This may conflict with professionalism, safety, or abuse-handling scenarios.",
            "suggestion": "Clarify priority and exceptions, e.g. 'Use a warm tone when appropriate, but remain firm and neutral in cases of abuse, threats, or policy enforcement.'"
        },
        {
            "phrase": "You should always respond in English unless the user writes in another language, in which case you can sometimes respond in their language if you feel it is appropriate",
            "reason": "This contains multiple ambiguities: what counts as 'another language' in mixed-language messages, what 'sometimes' means, and what criteria determine whether it is 'appropriate.'",
            "suggestion": "Replace with a deterministic rule, e.g. 'Respond in the user's most recent language. If the message mixes languages, ask which language they prefer.'"
        },
        {
            "phrase": "Never share internal company information",
            "reason": "'Internal company information' is not defined. It is unclear whether this includes internal processes, non-public policies, employee names, ticket notes, tooling, or troubleshooting steps.",
            "suggestion": "Define categories explicitly, e.g. 'Do not disclose non-public policies, internal notes, employee-only documentation, system architecture, or unpublished procedures.'"
        },
        {
            "phrase": "Do not share any confidential or private company data with users",
            "reason": "This overlaps with 'internal company information' but may not mean the same thing. The distinction between confidential, private, and internal is unclear.",
            "suggestion": "Consolidate into one precise confidentiality rule with examples of prohibited and allowed disclosures."
        },
        {
            "phrase": "Always escalate urgent issues to a human agent",
            "reason": "'Urgent issues' is undefined. It is unclear whether urgency refers to business impact, emotional distress, safety risk, account compromise, legal threats, outages, or time sensitivity.",
            "suggestion": "Define urgent categories and escalation triggers, e.g. 'Escalate safety risks, security breaches, payment fraud, legal complaints, and service outages affecting active customers.'"
        },
        {
            "phrase": "For critical issues make sure to tell the user to contact support directly",
            "reason": "'Critical issues' may overlap with 'urgent issues,' but the difference is not explained. It is also unclear whether the assistant should both escalate and tell the user to contact support, or choose one.",
            "suggestion": "Define the distinction and required action sequence, e.g. 'For critical issues, immediately advise the user to contact live support and create/escalate a handoff if available.'"
        },
        {
            "phrase": "Keep responses concise and short",
            "reason": "This conflicts with the later instruction to provide detailed and thorough explanations. 'Concise' and 'short' are also subjective without length guidance.",
            "suggestion": "Set a priority rule, e.g. 'Default to 3-5 sentences, but provide longer step-by-step explanations when the user asks for detail or appears confused.'"
        },
        {
            "phrase": "Provide detailed and thorough explanations when users are confused",
            "reason": "The prompt does not define how to detect confusion. Signals such as repeated questions, explicit statements, or contradictory replies are not specified.",
            "suggestion": "Define confusion indicators, e.g. 'If the user says they do not understand, asks the same question again, or appears to misunderstand instructions, provide a step-by-step explanation.'"
        },
        {
            "phrase": "Always greet the user at the start of the conversation",
            "reason": "It is unclear whether this means only the first assistant turn, every new chat session, or every message after a long pause or transfer.",
            "suggestion": "Specify timing, e.g. 'Include a brief greeting only in the first reply of each new conversation.'"
        },
        {
            "phrase": "Do not use informal language",
            "reason": "This may conflict with being warm, conversational, friendly, and approachable. It is unclear whether contractions, simple wording, or empathetic phrases count as informal.",
            "suggestion": "Define acceptable tone markers, e.g. 'Use plain, professional language; contractions are allowed, but avoid slang, emojis, and overly casual phrasing.'"
        },
        {
            "phrase": "Be warm and conversational in your tone",
            "reason": "This may conflict with 'Do not use informal language' and 'professional.' 'Conversational' can range from natural and clear to casual and chatty.",
            "suggestion": "Clarify the intended register, e.g. 'Use a professional but human tone: empathetic, clear, and natural, without slang or jokes.'"
        }
    ],
    "coverage_gaps": [
        {
            "gap": "No instructions for handling abusive, threatening, or harassing users",
            "example": "A user insults the assistant or threatens staff. The prompt does not say whether to warn, de-escalate, refuse, or escalate."
        },
        {
            "gap": "No process for self-harm, medical, legal, or physical safety emergencies",
            "example": "A user says they are in danger or may harm themselves. The prompt only mentions urgent and critical issues generally, without safety-specific guidance."
        },
        {
            "gap": "No guidance for authentication or account-specific requests",
            "example": "A user asks to change account details, access billing records, or reset security settings. The prompt does not say whether the assistant can verify identity or must redirect."
        },
        {
            "gap": "No handling for requests involving personal data or privacy rights",
            "example": "A user asks for a copy of their data or requests deletion under privacy law. The prompt does not specify how to respond or escalate."
        },
        {
            "gap": "No instructions for mixed-language or multilingual conversations",
            "example": "A user writes partly in English and partly in Spanish. The prompt does not define which language to use."
        },
        {
            "gap": "No guidance for unsupported languages",
            "example": "A user writes in a language the assistant cannot reliably support. The prompt does not say whether to reply in English, apologize, or route to human support."
        },
        {
            "gap": "No policy for when the assistant is uncertain or lacks enough information",
            "example": "A user asks a product question the assistant does not know. The prompt does not say whether to admit uncertainty, ask clarifying questions, or escalate."
        },
        {
            "gap": "No instructions for clarifying ambiguous user requests",
            "example": "A user says 'It is broken' without naming the product or issue. The prompt does not direct the assistant to ask follow-up questions before answering."
        },
        {
            "gap": "No distinction between external users and internal employees",
            "example": "An employee asks for internal troubleshooting steps. The prompt forbids sharing internal information with 'users,' but does not define whether employees are included."
        },
        {
            "gap": "No guidance on what support channels are available or how to contact support directly",
            "example": "The assistant tells the user to contact support directly, but provides no phone number, email, chat link, or hours."
        },
        {
            "gap": "No handoff protocol for escalation",
            "example": "The prompt says to escalate urgent issues, but does not specify whether to summarize the issue, collect details, create a ticket, or simply advise the user to wait for a human."
        },
        {
            "gap": "No prioritization rules for conflicting instructions",
            "example": "A confused user needs a long explanation, but the prompt also requires concise and short responses. The assistant is not told which rule takes precedence."
        },
        {
            "gap": "No guidance for repeated greetings across long conversations",
            "example": "In a multi-turn chat, the assistant may greet the user every message or only once; the prompt does not define the expected behavior."
        },
        {
            "gap": "No instructions for attachments, screenshots, or links",
            "example": "A user uploads a screenshot of an error or sends a suspicious link. The prompt does not say whether to analyze it, avoid opening links, or escalate."
        },
        {
            "gap": "No guidance for security incidents or fraud",
            "example": "A user reports account takeover, phishing, or unauthorized charges. These may be urgent or critical, but the prompt does not explicitly classify or route them."
        },
        {
            "gap": "No handling for outages or widespread incidents",
            "example": "Many users report the service is down. The prompt does not say whether to acknowledge known incidents, avoid speculation, or direct users to a status page."
        },
        {
            "gap": "No instructions for legal complaints, regulatory issues, or media inquiries",
            "example": "A user threatens legal action or asks for an official company statement. The prompt does not specify escalation or refusal boundaries."
        },
        {
            "gap": "No guidance for requests that require actions the assistant cannot perform",
            "example": "A user asks the assistant to cancel an order or issue a refund. The prompt does not say whether to explain limitations, collect details, or transfer to a human."
        },
        {
            "gap": "No definition of allowed content about company policies or public information",
            "example": "A user asks about refund policy or service terms. The prompt bans internal/confidential information, but does not clarify whether public policy summaries are allowed."
        },
        {
            "gap": "No instructions for maintaining consistency across turns",
            "example": "The assistant may switch between English and another language or between formal and conversational tone during the same conversation without a rule."
        }
    ]
}
```

## License

MIT
