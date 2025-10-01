from typing import Dict, List
import re
from collections import Counter


def analyze_language_style(messages: List[Dict]) -> Dict:
    """
    Analyze writing style for bot-like patterns, grammar issues, and copy-paste behavior.
    """
    all_texts = []
    emoji_counts = []
    exclamation_counts = []
    grammar_issues = 0
    
    for msg in messages:
        # Handle both dict and Pydantic model
        if hasattr(msg, 'content'):
            content = msg.content
            sender = msg.sender
        else:
            content = msg.get('content') or msg.get('text') or ''
            sender = msg.get('sender', 'contact')
        
        # Only analyze contact's messages
        if sender != 'contact':
            continue
        
        all_texts.append(content)
        
        # Count emojis (rough approximation)
        emoji_count = len(re.findall(r'[\U0001F300-\U0001F9FF]|[❤️😊😍🥰💕💖]', content))
        emoji_counts.append(emoji_count)
        
        # Count exclamation marks
        exclamation_count = content.count('!')
        exclamation_counts.append(exclamation_count)
        
        # Detect common grammar mistakes (native speaker claims vs actual grammar)
        if _has_grammar_issues(content):
            grammar_issues += 1
    
    # Detect copy-paste / repeated phrases
    duplicate_phrases = _detect_duplicates(all_texts)
    
    # Detect ChatGPT-like patterns
    chatgpt_signals = _detect_ai_generated(all_texts)
    
    # Calculate metrics
    avg_emojis = sum(emoji_counts) / len(emoji_counts) if emoji_counts else 0
    avg_exclamations = sum(exclamation_counts) / len(exclamation_counts) if exclamation_counts else 0
    
    return {
        'message_count': len(all_texts),
        'avg_emojis_per_message': avg_emojis,
        'avg_exclamations_per_message': avg_exclamations,
        'grammar_issue_count': grammar_issues,
        'duplicate_phrases': duplicate_phrases,
        'has_duplicates': len(duplicate_phrases) > 0,
        'chatgpt_signals': chatgpt_signals,
        'excessive_emojis': avg_emojis > 3,
        'excessive_exclamations': avg_exclamations > 2
    }


def _has_grammar_issues(text: str) -> bool:
    """
    Detect common non-native grammar patterns.
    """
    grammar_patterns = [
        r'\bam working in\b',  # "I am working in oil rig" (should be "on an oil rig")
        r'\bfor making money\b',  # "for making money" (awkward)
        r'\bplease assistance\b',  # word order error
        r'\bvery much love you\b',  # "very much love you" (should be "love you very much")
        r'\bneed help financial\b',  # adjective after noun
        r'\byou can trust to me\b',  # "trust to me" (should be "trust me")
    ]
    
    return any(re.search(p, text, re.IGNORECASE) for p in grammar_patterns)


def _detect_duplicates(texts: List[str]) -> List[str]:
    """
    Detect repeated phrases (copy-paste behavior).
    """
    # Extract phrases (3+ words)
    phrase_pattern = r'\b\w+\s+\w+\s+\w+(?:\s+\w+)*\b'
    all_phrases = []
    
    for text in texts:
        phrases = re.findall(phrase_pattern, text.lower())
        all_phrases.extend(phrases)
    
    # Find duplicates
    phrase_counts = Counter(all_phrases)
    duplicates = [phrase for phrase, count in phrase_counts.items() if count >= 2 and len(phrase) > 15]
    
    return duplicates[:5]  # Return top 5


def _detect_ai_generated(texts: List[str]) -> Dict:
    """
    Detect ChatGPT-like writing patterns.
    """
    ai_patterns = [
        r'as an? (?:AI|language model)',
        r'i apologize,? but',
        r'it\'s important to note',
        r'however,? it\'s worth',
        r'in conclusion',
        r'to summarize',
    ]
    
    combined = ' '.join(texts).lower()
    ai_signals = [p for p in ai_patterns if re.search(p, combined)]
    
    # Overly formal/polite patterns
    formal_count = len(re.findall(r'\b(kindly|please find|as per|hereby|aforementioned)\b', combined, re.IGNORECASE))
    
    return {
        'has_ai_patterns': len(ai_signals) > 0,
        'ai_pattern_count': len(ai_signals),
        'overly_formal': formal_count > 3
    }


def calculate_style_risk_boost(style_analysis: Dict) -> float:
    """
    Calculate risk boost based on writing style anomalies.
    """
    boost = 0.0
    
    # Excessive emojis/exclamations (trying too hard)
    if style_analysis.get('excessive_emojis') or style_analysis.get('excessive_exclamations'):
        boost += 0.08
    
    # Grammar issues despite native speaker claim
    if style_analysis.get('grammar_issue_count', 0) >= 2:
        boost += 0.12
    
    # Copy-paste behavior (scripted responses)
    if style_analysis.get('has_duplicates'):
        boost += 0.15
    
    # AI-generated text (using bots)
    if style_analysis.get('chatgpt_signals', {}).get('has_ai_patterns'):
        boost += 0.1
    
    return min(boost, 0.35)

