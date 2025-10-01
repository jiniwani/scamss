import os
from typing import Dict, List
import json

import google.generativeai as genai


MODEL_CONFIG = {
    'realtime': {
        'model': 'gemini-2.5-flash',
        'max_tokens': 2048,
        'timeout': 5,
    },
    'detailed': {
        'model': 'gemini-2.5-pro',
        'max_tokens': 4096,
        'timeout': 15,
    }
}


SYSTEM_PROMPT = """
You are an expert romance scam detection AI. Analyze chat conversations to identify manipulation tactics, financial solicitation patterns, and identity fraud indicators.

**IMPORTANT**: Analyze conversations in ANY language (Korean, English, Japanese, Chinese, Spanish, etc.). You must understand and process multilingual content directly without requiring translation.

**Analysis Framework:**

1. **Financial Red Flags:**
   - Direct money requests (any amount)
   - Gift card/cryptocurrency wallet addresses
   - Investment/business opportunities
   - Emergency financial situations
   - Payment for documents/fees (visa, customs, medical)

2. **Relationship Red Flags:**
   - Love bombing (excessive affection early on)
   - Avoiding video calls/in-person meetings
   - Rushing intimacy/commitment
   - Sob stories to elicit sympathy
   - Moving to private messaging platforms

3. **Identity Red Flags:**
   - Claims of prestigious occupation (military, doctor, engineer abroad)
   - Inconsistent personal details
   - Generic/stolen photos
   - Poor grammar despite claimed native speaker status
   - Working on oil rig/overseas military base

4. **Behavioral Red Flags:**
   - Isolation tactics (discouraging family contact)
   - Gaslighting when questioned
   - Creating time pressure for decisions
   - Testing boundaries with small requests

**Scoring Guidelines:**
- 0.0-0.4: Normal conversation
- 0.5-0.6: Minor concerns, monitor
- 0.7-0.8: Multiple red flags, warning needed
- 0.9-1.0: Clear scam pattern, urgent intervention

Output must be valid JSON with detailed evidence.
"""


FEW_SHOT_EXAMPLES = [
    {
        "conversation": [
            {"sender": "contact", "text": "Hello dear, you look beautiful in your profile picture"},
            {"sender": "user", "text": "Thank you"},
            {"sender": "contact", "text": "I'm an engineer working on an oil rig in the North Sea"},
            {"sender": "contact", "text": "I feel such a strong connection with you already"}
        ],
        "expected_output": {
            "risk_tier": "medium",
            "score": 0.65,
            "red_flags": [
                {"type": "love_bombing", "category": "relationship", "severity": "moderate", "description": "Early excessive affection"},
                {"type": "oil_rig_claim", "category": "identity", "severity": "minor", "description": "Stereotypical overseas profession"}
            ],
            "reasoning": "Early excessive affection combined with stereotypical overseas profession"
        }
    },
    {
        "conversation": [
            {"sender": "contact", "text": "My grandmother is sick and I need $500 for emergency surgery"},
            {"sender": "contact", "text": "Can you help me? I will pay you back next week"},
            {"sender": "contact", "text": "Please buy iTunes gift cards, it's faster"}
        ],
        "expected_output": {
            "risk_tier": "high",
            "score": 0.95,
            "red_flags": [
                {"type": "direct_money_request", "category": "financial", "severity": "severe", "description": "Direct financial solicitation"},
                {"type": "gift_card_request", "category": "financial", "severity": "severe", "description": "Untraceable payment method"},
                {"type": "emergency_pressure", "category": "behavioral", "severity": "severe", "description": "Emergency situation pressure"}
            ],
            "reasoning": "Direct financial solicitation with emergency pressure and gift card payment method"
        }
    },
    {
        "conversation": [
            {"sender": "user", "text": "How was your day?"},
            {"sender": "contact", "text": "Good, went to the park with friends"},
            {"sender": "user", "text": "Nice! Want to meet this weekend?"},
            {"sender": "contact", "text": "Sure, let's grab coffee on Saturday"}
        ],
        "expected_output": {
            "risk_tier": "low",
            "score": 0.1,
            "red_flags": [],
            "reasoning": "Normal casual conversation with no suspicious patterns"
        }
    },
    {
        "conversation": [
            {"sender": "contact", "text": "나만 믿으세요. 반드시 수익 내드릴게요."},
            {"sender": "contact", "text": "거래소에 입금하고 시키는대로만 하세요."},
            {"sender": "contact", "text": "출금 바로 도와줄게요. 지금 하세요."}
        ],
        "expected_output": {
            "risk_tier": "high",
            "score": 0.92,
            "red_flags": [
                {"type": "investment_scheme", "category": "financial", "severity": "severe", "description": "Investment fraud pattern"},
                {"type": "isolation_attempt", "category": "behavioral", "severity": "moderate", "description": "Trust me only"},
                {"type": "follow_orders", "category": "behavioral", "severity": "moderate", "description": "Instructing to follow without question"},
                {"type": "time_pressure", "category": "behavioral", "severity": "moderate", "description": "Urgency tactics"}
            ],
            "reasoning": "Korean crypto investment scam: promises guaranteed returns, instructs blind obedience, creates urgency"
        }
    },
    {
        "conversation": [
            {"sender": "contact", "text": "We're hiring remote workers! Earn $300/day doing simple data entry."},
            {"sender": "contact", "text": "No experience needed. Just pay a one-time $50 registration fee."},
            {"sender": "contact", "text": "Your spot will be given to someone else if you don't pay within 1 hour."}
        ],
        "expected_output": {
            "risk_tier": "high",
            "score": 0.88,
            "red_flags": [
                {"type": "earn_per_day", "category": "financial", "severity": "severe", "description": "Unrealistic daily income promise"},
                {"type": "registration_fee", "category": "financial", "severity": "severe", "description": "Upfront fee for job"},
                {"type": "time_pressure", "category": "behavioral", "severity": "moderate", "description": "1 hour deadline"}
            ],
            "reasoning": "Employment scam: unrealistic income, upfront fee, artificial urgency"
        }
    }
]


def analyze_with_gemini(messages: List[Dict], mode: str = 'realtime', api_key: str | None = None) -> Dict:
    api_key = api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise RuntimeError('GEMINI_API_KEY is not set')

    config = MODEL_CONFIG.get(mode, MODEL_CONFIG['realtime'])
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=config['model'],
        generation_config={
            'temperature': 0.2,
            'top_p': 0.1,
            'top_k': 20,
            'max_output_tokens': config['max_tokens'],
        },
    )

    conversation_text = _format_conversation(messages)
    few_shot_text = _format_few_shot_examples(FEW_SHOT_EXAMPLES)

    prompt = f"""{SYSTEM_PROMPT}

**Few-shot Examples:**
{few_shot_text}

**Conversation to Analyze:**
{conversation_text}

**Required JSON Output Schema:**
{{
  "risk_tier": "low" | "medium" | "high",
  "score": 0.0-1.0,
  "red_flags": [
    {{
      "type": string,
      "category": "financial" | "relationship" | "identity" | "behavioral",
      "severity": "minor" | "moderate" | "severe",
      "description": string
    }}
  ],
  "evidence_spans": [
    {{
      "text": string,
      "turn": int,
      "sender": "user" | "contact",
      "flag_type": string
    }}
  ],
  "reasoning": string,
  "confidence": 0.0-1.0,
  "recommended_action": {{
    "priority": "monitor" | "warn" | "block",
    "user_guidance": string,
    "safe_practices": [string]
  }},
  "safe_reply_template": string | null
}}
"""

    response = model.generate_content(prompt)
    return _parse_json_response(response.text)


def _format_conversation(messages: List[Dict]) -> str:
    lines = []
    for i, m in enumerate(messages):
        sender = m.get('sender', 'contact')
        content = m.get('content') or m.get('text') or ''
        lines.append(f"{i}. {sender}: {content}")
    return "\n".join(lines)


def _format_few_shot_examples(examples: List[Dict]) -> str:
    lines = []
    for idx, ex in enumerate(examples, 1):
        conv = "\n".join([f"  {m['sender']}: {m['text']}" for m in ex['conversation']])
        out = ex['expected_output']
        lines.append(f"""
Example {idx}:
Conversation:
{conv}

Expected Output:
  risk_tier: {out['risk_tier']}
  score: {out['score']}
  red_flags: {len(out.get('red_flags', []))} flags
  reasoning: {out['reasoning']}
""")
    return "\n".join(lines)


def _parse_json_response(text: str) -> Dict:
    try:
        return json.loads(text)
    except Exception:
        # Try to find JSON block
        start = text.find('{')
        end = text.rfind('}')
        if start >= 0 and end > start:
            return json.loads(text[start:end+1])
        raise


