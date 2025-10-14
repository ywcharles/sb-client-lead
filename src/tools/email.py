import re

ROLE_BASED_PREFIXES = {
    "info", "support", "help", "admin", "sales", "contact", "office",
    "billing", "customerservice", "noreply", "no-reply", "service", "team"
}

TEMP_DOMAINS = {"mailinator.com", "tempmail.com", "10minutemail.com"}

PERSONAL_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "icloud.com", "hotmail.com"}

def score_email(email: str) -> int:
    score = 0
    email = email.lower().strip()
    
    if "@" not in email:
        return 1  # invalid email
    
    local, domain = email.split("@", 1)
    
    # 1. Person vs role-based
    if local in ROLE_BASED_PREFIXES or local.startswith(tuple(ROLE_BASED_PREFIXES)):
        person_score = 0
    else:
        person_score = 2
    
    # 2. Domain type
    if domain in PERSONAL_DOMAINS:
        domain_score = 0.5
    elif domain in TEMP_DOMAINS:
        domain_score = 0  # suspicious
    else:
        domain_score = 1  # business/custom
    
    # 3. Name in email
    # Look for first.last or first_last pattern
    if re.match(r"^[a-z]+\.[a-z]+$", local) or re.match(r"^[a-z]+_[a-z]+$", local):
        name_score = 1
    elif re.match(r"^[a-z]+$", local):
        name_score = 0.5
    else:
        name_score = 0
    
    # Sum raw score
    score = person_score + domain_score + name_score
    
    # Ensure 1-5
    score = min(max(round(score), 1), 5)
    return score
