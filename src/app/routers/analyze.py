from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
import time
import os

from ..services.preprocess import preprocess_text
from ..services.risk_engine import detect_red_flags, calculate_risk_score, determine_risk_tier
from ..services.gemini_client import analyze_with_gemini
from ..services.context_analyzer import analyze_conversation_context, calculate_context_risk_boost
from ..services.entity_validator import detect_inconsistencies, calculate_entity_risk_boost
from ..services.sentiment_analyzer import analyze_emotional_manipulation, calculate_emotional_risk_boost
from ..services.money_pattern_analyzer import analyze_money_patterns, calculate_money_pattern_risk_boost
from ..utils.pii import mask_pii

router = APIRouter()


class Message(BaseModel):
    message_id: str
    sender: Literal["user", "contact"]
    content: str
    timestamp: str
    platform: Optional[str] = None


class AnalyzeOptions(BaseModel):
    mode: Literal["realtime", "detailed"] = "realtime"
    language: str = "auto"
    mask_pii: bool = True


class AnalyzeRequest(BaseModel):
    conversation_id: str
    messages: List[Message]
    options: AnalyzeOptions = Field(default_factory=AnalyzeOptions)


class AnalyzeTextRequest(BaseModel):
    text: str
    mode: Literal["realtime", "detailed"] = "realtime"
    mask_pii: bool = True


@router.post("/analyze")
def analyze(body: AnalyzeRequest):
    if not body.messages:
        raise HTTPException(status_code=400, detail="messages is required")

    start = time.time()

    # Concatenate contents for language detection; simple approach
    joined = "\n".join([m.content for m in body.messages])
    pp = preprocess_text(joined, do_mask=body.options.mask_pii)

    # If Gemini key is configured, try model-based analysis first
    use_gemini = bool(os.getenv('GEMINI_API_KEY')) and body.options.mode in ("realtime", "detailed")
    if use_gemini:
        try:
            # Mask PII per message before sending to model
            prepared_msgs = []
            for m in body.messages:
                content = m.content
                if body.options.mask_pii:
                    content = mask_pii(content)['masked_text']
                prepared_msgs.append({
                    'sender': m.sender,
                    'content': content,
                    'timestamp': m.timestamp,
                })

            model_result = analyze_with_gemini(prepared_msgs, mode=body.options.mode)

            # Ensure minimal metadata
            if 'analysis_metadata' not in model_result:
                model_result['analysis_metadata'] = {}
            model_result['analysis_metadata'].update({
                'model_used': f"gemini:{body.options.mode}",
                'processing_time_ms': int((time.time() - start) * 1000),
                'language_detected': pp['language']['language'],
                'pii_masked_count': sum(d['count'] for d in pp['pii']['detected_pii']) if pp['pii']['detected_pii'] else 0,
            })
            return model_result
        except Exception:
            # Fallback to rule-based pipeline below
            pass

    # Detect red flags on original message contents (baseline)
    msgs = [{
        'sender': m.sender,
        'content': m.content,
        'timestamp': m.timestamp,
    } for m in body.messages]

    detected = detect_red_flags(msgs)
    
    # Analyze conversation flow and temporal patterns
    context_analysis = analyze_conversation_context(body.messages)
    context_boost = calculate_context_risk_boost(context_analysis)
    
    # Validate entity consistency
    entity_validation = detect_inconsistencies(body.messages)
    entity_boost = calculate_entity_risk_boost(entity_validation)
    
    # Analyze emotional manipulation
    sentiment_analysis = analyze_emotional_manipulation(body.messages)
    sentiment_boost = calculate_emotional_risk_boost(sentiment_analysis)
    
    # Analyze money amount patterns
    money_analysis = analyze_money_patterns(body.messages)
    money_boost = calculate_money_pattern_risk_boost(money_analysis)

    conversation_context = {
        'message_count': len(msgs),
        'financial_flags_count': sum(
            flags.get('count', 0) for flag, flags in detected.get('financial', {}).items()
        ),
    }
    base_score = calculate_risk_score(detected, conversation_context)
    
    # Apply all boosts (context, entity, sentiment, money patterns)
    total_boost = context_boost + entity_boost + sentiment_boost + money_boost
    score = min(1.0, base_score + total_boost)

    # Build red_flags list
    red_flags_list = []
    for category, flags in detected.items():
        for flag_type, details in flags.items():
            severity = 'severe' if category == 'financial' and flag_type in ('direct_money_request', 'gift_card_request') else 'moderate'
            red_flags_list.append({
                'type': flag_type,
                'category': category,
                'severity': severity,
                'description': flag_type.replace('_', ' '),
            })

    tier_info = determine_risk_tier(score, red_flags_list)

    latency_ms = int((time.time() - start) * 1000)
    return {
        'risk_tier': tier_info['tier'],
        'score': score,
        'red_flags': red_flags_list,
        'evidence_spans': [],
        'reasoning': 'Rule-based baseline analysis',
        'confidence': tier_info['confidence'],
        'recommended_action': {
            'priority': 'monitor' if tier_info['tier'] == 'low' else ('warn' if tier_info['tier'] == 'medium' else 'block'),
            'user_guidance': '기본 규칙 기반 분석 결과입니다.',
            'safe_practices': [
                '개인정보 공유 금지',
                '금전 요구 즉시 중단',
                '비디오 통화로 신원 확인'
            ],
        },
        'analysis_metadata': {
            'model_used': 'rule-based',
            'processing_time_ms': latency_ms,
            'language_detected': pp['language']['language'],
            'pii_masked_count': sum(d['count'] for d in pp['pii']['detected_pii']) if pp['pii']['detected_pii'] else 0,
        },
    }


@router.post("/analyze_text")
def analyze_text(body: AnalyzeTextRequest, x_gemini_key: str | None = Header(default=None, alias="X-Gemini-Key")):
    # Wrap plain text into minimal AnalyzeRequest
    req = AnalyzeRequest(
        conversation_id="single-text",
        messages=[Message(message_id="m1", sender="contact", content=body.text, timestamp="1970-01-01T00:00:00Z")],
        options=AnalyzeOptions(mode=body.mode, language="auto", mask_pii=body.mask_pii),
    )
    # If API key is provided in header, prefer Gemini path
    if x_gemini_key:
        # Reuse Gemini path in analyze by setting env just for this call
        try:
            prepared_msgs = [{ 'sender': 'contact', 'content': body.text, 'timestamp': '1970-01-01T00:00:00Z' }]
            result = analyze_with_gemini(prepared_msgs, mode=body.mode, api_key=x_gemini_key)
            return result
        except Exception:
            pass
    return analyze(req)


