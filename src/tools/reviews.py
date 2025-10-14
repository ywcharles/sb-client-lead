from typing import List
from textblob import TextBlob

def score_review_text(review_text: str) -> float:
    """
    Score a Google review text from 1 (negative) to 5 (positive) using TextBlob.
    """
    if not review_text:
        return 3.0  # neutral if empty
    
    polarity = TextBlob(review_text).sentiment.polarity  # -1 to 1
    # Map -1 → 1, 0 → 3, +1 → 5
    score = ((polarity + 1) / 2) * 4 + 1
    return round(score, 2)

def score_reviews_list(review_list: List[dict]):
    """
    Given a list of Google review objects, return:
      - avg score
      - dict mapping review 'name' to score
    """
    scores = {}
    sum_scores = 0
    count = 0

    for review in review_list:
        text = review.get("text", {}).get("text", "")
        review_score = score_review_text(text)
        sum_scores += review_score
        count += 1
        scores[text] = review_score

    avg = round(sum_scores / max(count, 1), 2)
    return avg, scores
