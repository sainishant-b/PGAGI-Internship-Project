"""
Candidate data storage module for TalentScout Hiring Assistant.
Handles saving, retrieving, and deleting candidate data with GDPR compliance.
"""

import json
import os
from datetime import datetime


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def ensure_data_dir():
    """Create the data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def save_candidate(candidate_data: dict, tech_answers: list, sentiment_history: list) -> str:
    """
    Save candidate screening data to a JSON file.
    
    Uses timestamp-based filenames to avoid PII in file names (GDPR compliance).
    
    Args:
        candidate_data: Dictionary of collected candidate information.
        tech_answers: List of technical question answers.
        sentiment_history: List of sentiment analysis results.
    
    Returns:
        The filepath where data was saved.
    """
    ensure_data_dir()
    
    # Use timestamp-based filename (no PII)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"candidate_{timestamp}.json"
    filepath = os.path.join(DATA_DIR, filename)
    
    record = {
        "timestamp": datetime.now().isoformat(),
        "candidate_info": candidate_data,
        "technical_answers": tech_answers,
        "sentiment_summary": {
            "history": sentiment_history,
            "average_polarity": _calc_avg_polarity(sentiment_history),
        },
        "metadata": {
            "screening_version": "1.0.0",
            "status": "pending_review",
        }
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    
    return filepath


def delete_candidate(filepath: str) -> bool:
    """
    Delete a candidate's data file (GDPR right to erasure).
    
    Args:
        filepath: Path to the candidate data file.
    
    Returns:
        True if deleted successfully, False otherwise.
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except OSError:
        return False


def list_candidates() -> list[dict]:
    """
    List all stored candidate records.
    
    Returns:
        List of dictionaries with filename and basic info.
    """
    ensure_data_dir()
    candidates = []
    
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(DATA_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                candidates.append({
                    "filename": filename,
                    "filepath": filepath,
                    "name": data.get("candidate_info", {}).get("full_name", "Unknown"),
                    "timestamp": data.get("timestamp", ""),
                    "status": data.get("metadata", {}).get("status", "unknown"),
                })
            except (json.JSONDecodeError, KeyError):
                continue
    
    return sorted(candidates, key=lambda x: x['timestamp'], reverse=True)


def _calc_avg_polarity(sentiment_history: list) -> float:
    """Calculate average sentiment polarity from history."""
    if not sentiment_history:
        return 0.0
    polarities = [s.get('polarity', 0.0) for s in sentiment_history]
    return round(sum(polarities) / len(polarities), 3)
