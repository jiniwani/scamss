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
from ..services.sequence_analyzer import detect_scam_sequence, calculate_sequence_risk_boost
from ..services.style_analyzer import analyze_language_style, calculate_style_risk_boost
from ..utils.pii import mask_pii
from ..utils.translations import FLAG_TYPE_KO

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
    
    # Detect scam sequence pattern
    sequence_analysis = detect_scam_sequence(body.messages)
    sequence_boost = calculate_sequence_risk_boost(sequence_analysis)
    
    # Analyze language style
    style_analysis = analyze_language_style(body.messages)
    style_boost = calculate_style_risk_boost(style_analysis)

    conversation_context = {
        'message_count': len(msgs),
        'financial_flags_count': sum(
            flags.get('count', 0) for flag, flags in detected.get('financial', {}).items()
        ),
    }
    base_score = calculate_risk_score(detected, conversation_context)
    
    # Apply all boosts (context, entity, sentiment, money, sequence, style)
    total_boost = (context_boost + entity_boost + sentiment_boost + 
                   money_boost + sequence_boost + style_boost)
    score = min(1.0, base_score + total_boost)

    # Build red_flags list
    red_flags_list = []
    for category, flags in detected.items():
        for flag_type, details in flags.items():
            severity = 'severe' if category == 'financial' and flag_type in ('direct_money_request', 'gift_card_request') else 'moderate'
            red_flags_list.append({
                'type': flag_type,
                'type_ko': FLAG_TYPE_KO.get(flag_type, flag_type.replace('_', ' ')),
                'category': category,
                'severity': severity,
                'description': FLAG_TYPE_KO.get(flag_type, flag_type.replace('_', ' ')),
            })

    tier_info = determine_risk_tier(score, red_flags_list)
    
    # Generate evidence highlights
    evidence_spans = _extract_evidence_spans(body.messages, red_flags_list, detected)
    
    # Generate safe reply template
    safe_reply = _generate_safe_reply_template(tier_info['tier'], red_flags_list)

    latency_ms = int((time.time() - start) * 1000)
    return {
        'risk_tier': tier_info['tier'],
        'score': score,
        'red_flags': red_flags_list,
        'evidence_spans': evidence_spans,
        'reasoning': '규칙 기반 다층 분석 (맥락, 엔티티, 감정, 금액, 시퀀스, 스타일)',
        'confidence': tier_info['confidence'],
        'recommended_action': {
            'priority': 'monitor' if tier_info['tier'] == 'low' else ('warn' if tier_info['tier'] == 'medium' else 'block'),
            'user_guidance': _get_user_guidance(tier_info['tier']),
            'safe_practices': [
                '개인정보 절대 공유 금지',
                '금전 요구 시 즉시 대화 중단 및 차단',
                '비디오 통화로 신원 확인',
                '가족/친구에게 상황 공유',
                '의심스러우면 경찰(112) 또는 사이버범죄 신고센터(182) 신고'
            ],
        },
        'safe_reply_template': safe_reply,
        'analysis_metadata': {
            'model_used': 'rule-based-multilayer',
            'processing_time_ms': latency_ms,
            'language_detected': pp['language']['language'],
            'pii_masked_count': sum(d['count'] for d in pp['pii']['detected_pii']) if pp['pii']['detected_pii'] else 0,
        },
    }


def _extract_evidence_spans(messages, red_flags_list, detected_flags):
    """Extract specific text spans that triggered red flags."""
    evidence = []
    flag_types = {f['type'] for f in red_flags_list}
    
    for i, msg in enumerate(messages):
        content = msg.content if hasattr(msg, 'content') else (msg.get('content') or '')
        lowered = content.lower()
        
        # Check which flags this message triggers
        for category, flags in detected_flags.items():
            for flag_type in flags.keys():
                if flag_type not in flag_types:
                    continue
                    
                # Extract relevant portion (max 100 chars)
                snippet = content[:100] if len(content) > 100 else content
                evidence.append({
                    'text': snippet,
                    'turn': i,
                    'sender': msg.sender if hasattr(msg, 'sender') else msg.get('sender', 'contact'),
                    'flag_type': flag_type,
                    'timestamp': msg.timestamp if hasattr(msg, 'timestamp') else msg.get('timestamp', '')
                })
                break  # One evidence per message
    
    return evidence[:10]  # Top 10


def _generate_safe_reply_template(tier, red_flags_list):
    """Generate safe reply template based on risk tier."""
    if tier == 'high':
        return None  # Don't reply to high-risk contacts
    
    flag_types = {f['type'] for f in red_flags_list}
    
    if 'direct_money_request' in flag_types or 'gift_card_request' in flag_types:
        return "죄송하지만 금전 지원은 어렵습니다. 공식 채널을 통해 도움을 요청하시는 게 좋을 것 같아요."
    
    if 'meeting_avoidance' in flag_types:
        return "직접 만나서 이야기하면 좋겠어요. 언제 시간 되시나요?"
    
    if 'love_bombing' in flag_types:
        return "감사합니다. 다만 서로를 더 알아가는 시간이 필요할 것 같아요."
    
    return "좀 더 생각해보고 답변드릴게요. 급하지 않으니 천천히 이야기해요."


def _get_user_guidance(tier):
    """Get user guidance message based on tier."""
    if tier == 'high':
        return "🚨 매우 위험: 전형적인 스캠 패턴이 다수 발견되었습니다. 즉시 대화를 중단하고 차단하세요."
    elif tier == 'medium':
        return "⚠️ 주의 필요: 여러 의심스러운 패턴이 감지되었습니다. 신중하게 대응하고 개인정보·금전 요구를 거절하세요."
    else:
        return "✅ 안전: 현재까지 명확한 스캠 지표는 없으나, 금전 요구나 개인정보 공유 시 즉시 경계하세요."


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


