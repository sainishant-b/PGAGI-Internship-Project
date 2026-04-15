"""
Sentiment analysis module for TalentScout Hiring Assistant.
Uses TextBlob to detect candidate emotional tone and adjust responses.
"""

from textblob import TextBlob


def analyze_sentiment(text: str) -> dict:
    """
    Analyze the sentiment of a given text.
    
    Uses TextBlob's polarity analysis to determine if the text
    is positive, negative, or neutral.
    
    Args:
        text: The text to analyze.
    
    Returns:
        Dictionary with 'polarity' (float), 'label' (str), and 'emoji' (str).
    """
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # Range: -1.0 to 1.0
        
        if polarity > 0.2:
            label = "positive"
            emoji = "😊"
        elif polarity < -0.2:
            label = "negative"
            emoji = "😟"
        else:
            label = "neutral"
            emoji = "😐"
        
        return {
            "polarity": round(polarity, 3),
            "label": label,
            "emoji": emoji,
        }
    except Exception:
        return {
            "polarity": 0.0,
            "label": "neutral",
            "emoji": "😐",
        }


def get_sentiment_context(sentiment_data: dict) -> str:
    """
    Generate a context string for the LLM based on sentiment analysis.
    
    Args:
        sentiment_data: The sentiment analysis result dictionary.
    
    Returns:
        Context string to prepend to the LLM prompt.
    """
    label = sentiment_data.get("label", "neutral")
    polarity = sentiment_data.get("polarity", 0.0)
    
    if label == "negative":
        return (
            f"[SENTIMENT ALERT: The candidate seems {label} (score: {polarity}). "
            f"Be extra supportive, patient, and encouraging in your response. "
            f"Reassure them that this is a friendly conversation, not a test.]"
        )
    elif label == "positive":
        return (
            f"[SENTIMENT NOTE: The candidate seems {label} (score: {polarity}). "
            f"Match their positive energy and enthusiasm.]"
        )
    else:
        return ""
