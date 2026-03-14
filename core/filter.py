import re

# 1. First-person pronouns (Self-reflection)
SELF_REF = re.compile(r'\b(i|me|my|mine|myself)\b', re.IGNORECASE)

# 2. Cognitive, emotional, and psychological state words
PSYCH_WORDS = re.compile(
    r'\b(feel|felt|think|thought|believe|want|need|love|hate|wish|hope|afraid|'
    r'sad|angry|mad|worried|anxious|stressed|dream|remember|forget|hurt|happy|'
    r'confused|overwhelmed|proud|guilty|shame)\b', 
    re.IGNORECASE
)

# 3. Transactional, logistical, and spam/scam markers
NOISE_WORDS = re.compile(
    r'\b(is this still available|asking price|firm on price|cash only|venmo|'
    r'tracking number|shipping|order confirmed|your receipt|account suspended|'
    r'click here|limited time|guarantee|wire transfer|gift card)\b', 
    re.IGNORECASE
)

def evaluate_psych_signal(text):
    """
    Evaluates a message for psychological density and rejects transactional noise.
    Returns a float score, and a boolean indicating if it passes the threshold.
    """
    if not text:
        return 0.0, False
        
    # --- NOISE CHECK (The Gatekeeper) ---
    # If the message contains explicit transactional or scam phrases, instantly reject it.
    if len(NOISE_WORDS.findall(text)) > 0:
        return 0.0, False 

    words = text.split()
    word_count = len(words)
    
    # 1. The Bouncer: Immediate rejection for extremely short logistical texts (e.g., "Ok", "On my way")
    if word_count < 4:
        return 0.0, False
        
    score = 0.0
    
    # 2. Length Bonus: Longer messages inherently contain more context
    if word_count > 12: 
        score += 1.0
    if word_count > 30: 
        score += 2.0
        
    # 3. Introspection Bonus: First-person framing
    if SELF_REF.search(text):
        score += 1.5
        
    # 4. Emotional/Cognitive Bonus: Internal state markers
    # We count how many times they express an internal state
    state_matches = len(PSYCH_WORDS.findall(text))
    if state_matches > 0:
        score += (state_matches * 2.0)
        
    # THRESHOLD: Decide what score makes a message "worth keeping".
    # A score of 3.0 means it has to be either:
    # A) Long (>30 words) + uses "I/Me"
    # B) Uses an emotional word + uses "I/Me"
    # C) Very long (>30 words) + no specific psych words but highly narrative
    is_valuable = score >= 3.0
    
    return score, is_valuable