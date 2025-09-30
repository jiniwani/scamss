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


SYSTEM_PROMPT = (
    "You are an expert romance scam detection AI. Analyze chat conversations to identify "
    "manipulation tactics, financial solicitation patterns, and identity fraud indicators. "
    "Output must be valid JSON with detailed evidence."
)


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

    prompt = f"{SYSTEM_PROMPT}\n\nConversation:\n{conversation_text}\n\nReturn JSON with keys: risk_tier, score, red_flags, evidence_spans, reasoning, recommended_action, safe_reply_template"

    response = model.generate_content(prompt)
    return _parse_json_response(response.text)


def _format_conversation(messages: List[Dict]) -> str:
    lines = []
    for i, m in enumerate(messages):
        sender = m.get('sender', 'contact')
        content = m.get('content') or m.get('text') or ''
        lines.append(f"{i}. {sender}: {content}")
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


