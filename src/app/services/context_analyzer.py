from typing import Dict, List
from datetime import datetime
import re


def analyze_conversation_context(messages: List[Dict]) -> Dict:
    """
    Analyze temporal patterns, topic shifts, and emotional manipulation in conversation flow.
    """
    if not messages or len(messages) < 2:
        return {
            'message_count': len(messages),
            'time_pattern': {},
            'topic_shift': {},
            'relationship_stage': 'unknown',
            'suspicion_signals': []
        }
    
    time_pattern = _analyze_time_intervals(messages)
    topic_shift = _detect_topic_shifts(messages)
    relationship_stage = _determine_relationship_stage(messages)
    suspicion_signals = []
    
    # Signal 1: Rapid escalation to money request
    if topic_shift.get('turns_before_money_request', 999) < 15:
        suspicion_signals.append({
            'type': 'rapid_money_request',
            'severity': 'high' if topic_shift['turns_before_money_request'] < 5 else 'medium',
            'detail': f"Money request within {topic_shift['turns_before_money_request']} messages"
        })
    
    # Signal 2: Love bombing in early stage
    if relationship_stage == 'early' and topic_shift.get('has_love_bombing'):
        suspicion_signals.append({
            'type': 'early_love_bombing',
            'severity': 'high',
            'detail': 'Excessive affection within first 10 messages'
        })
    
    # Signal 3: Sudden topic jump to financial
    if topic_shift.get('abrupt_shift_to_finance'):
        suspicion_signals.append({
            'type': 'abrupt_financial_shift',
            'severity': 'medium',
            'detail': 'Sudden shift from casual to financial topic'
        })
    
    return {
        'message_count': len(messages),
        'time_pattern': time_pattern,
        'topic_shift': topic_shift,
        'relationship_stage': relationship_stage,
        'suspicion_signals': suspicion_signals
    }


def _analyze_time_intervals(messages: List[Dict]) -> Dict:
    """
    Analyze time gaps between messages.
    """
    intervals = []
    for i in range(1, len(messages)):
        try:
            prev_ts = datetime.fromisoformat(messages[i-1].get('timestamp', '1970-01-01T00:00:00Z').replace('Z', '+00:00'))
            curr_ts = datetime.fromisoformat(messages[i].get('timestamp', '1970-01-01T00:00:00Z').replace('Z', '+00:00'))
            gap_seconds = (curr_ts - prev_ts).total_seconds()
            intervals.append(gap_seconds)
        except Exception:
            continue
    
    if not intervals:
        return {'avg_gap_seconds': 0, 'has_rapid_succession': False}
    
    avg_gap = sum(intervals) / len(intervals)
    # Rapid succession: multiple messages within 5 seconds
    rapid_count = sum(1 for g in intervals if g < 5)
    
    return {
        'avg_gap_seconds': avg_gap,
        'has_rapid_succession': rapid_count >= 3,
        'rapid_message_count': rapid_count
    }


def _detect_topic_shifts(messages: List[Dict]) -> Dict:
    """
    Detect shifts from casual to financial topics.
    """
    financial_keywords = [
        'money', 'cash', 'send', 'transfer', 'pay', 'fee', 'dollars', '$',
        '돈', '송금', '입금', '보내', '비용', '수수료', 'gift card', 'bitcoin'
    ]
    
    love_keywords = [
        'love', 'soul', 'destiny', 'marry', 'future', 'forever',
        '사랑', '운명', '결혼', '미래', 'soulmate'
    ]
    
    first_money_turn = None
    first_love_turn = None
    prev_topic = None
    abrupt_shift = False
    
    for i, msg in enumerate(messages):
        # Handle both dict and Pydantic model
        if hasattr(msg, 'content'):
            content = msg.content.lower()
        else:
            content = (msg.get('content') or msg.get('text') or '').lower()
        
        has_money = any(kw in content for kw in financial_keywords)
        has_love = any(kw in content for kw in love_keywords)
        
        current_topic = None
        if has_money:
            current_topic = 'financial'
            if first_money_turn is None:
                first_money_turn = i
        elif has_love:
            current_topic = 'love'
            if first_love_turn is None:
                first_love_turn = i
        else:
            current_topic = 'casual'
        
        # Detect abrupt shift (casual -> financial without love stage)
        if prev_topic == 'casual' and current_topic == 'financial' and first_love_turn is None:
            abrupt_shift = True
        
        prev_topic = current_topic
    
    return {
        'turns_before_money_request': first_money_turn if first_money_turn is not None else 999,
        'has_love_bombing': first_love_turn is not None and first_love_turn < 10,
        'abrupt_shift_to_finance': abrupt_shift,
        'love_before_money': (first_love_turn or 999) < (first_money_turn or 999)
    }


def _determine_relationship_stage(messages: List[Dict]) -> str:
    """
    Determine relationship stage based on message count and content.
    """
    count = len(messages)
    if count < 10:
        return 'early'
    elif count < 50:
        return 'developing'
    else:
        return 'established'


def calculate_context_risk_boost(context: Dict) -> float:
    """
    Calculate additional risk score based on conversation context.
    """
    boost = 0.0
    
    for signal in context.get('suspicion_signals', []):
        if signal['severity'] == 'high':
            boost += 0.15
        elif signal['severity'] == 'medium':
            boost += 0.08
    
    # Rapid succession messaging (bot-like behavior)
    if context.get('time_pattern', {}).get('has_rapid_succession'):
        boost += 0.1
    
    return min(boost, 0.4)  # Cap at 0.4 to avoid over-boosting

