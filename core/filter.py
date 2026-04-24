import re

SELF_REF = re.compile(r'\b(i|me|my|mine|myself)\b', re.IGNORECASE)
PSYCH_WORDS = re.compile(
    r'\b(feel|felt|think|thought|believe|want|need|love|hate|wish|hope|afraid|'
    r'sad|angry|mad|worried|anxious|stressed|dream|remember|forget|hurt|happy|'
    r'confused|overwhelmed|proud|guilty|shame)\b', 
    re.IGNORECASE
)
NOISE_WORDS = re.compile(
    r'\b(is this still available|asking price|firm on price|cash only|venmo|'
    r'tracking number|shipping|order confirmed|your receipt|account suspended|'
    r'click here|limited time|guarantee|wire transfer|gift card)\b', 
    re.IGNORECASE
)

def evaluate_psych_signal(text):
    if not text or not isinstance(text, str):
        return 0.0, False
        
    words = text.split()
    word_count = len(words)
    
    if word_count < 4:
        return 0.0, False
        
    # The Gatekeeper: Only kill if it's a SHORT transactional text.
    # We do not want to kill a 500-word daily conversation just because someone said "venmo".
    if word_count < 30 and len(NOISE_WORDS.findall(text)) > 0:
        return 0.0, False 

    score = 0.0
    if word_count > 12: score += 1.0
    if word_count > 30: score += 2.0
    if SELF_REF.search(text): score += 1.5
        
    state_matches = len(PSYCH_WORDS.findall(text))
    if state_matches > 0:
        score += (state_matches * 2.0)
        
    is_valuable = score >= 3.0
    return score, is_valuable