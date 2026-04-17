"""
Utility functions for TalentScout Hiring Assistant.
Input validation, sanitization, and helper functions.
"""

import re
from config import EXIT_KEYWORDS


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: The email string to validate.
    
    Returns:
        True if the email format is valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (flexible - accepts various formats).
    
    Args:
        phone: The phone number string to validate.
    
    Returns:
        True if the phone format is valid, False otherwise.
    """
    # Remove common separators and check if mostly digits
    cleaned = re.sub(r'[\s\-\(\)\+\.]', '', phone.strip())
    return len(cleaned) >= 7 and len(cleaned) <= 15 and cleaned.isdigit()


def validate_experience(experience: str) -> tuple[bool, int]:
    """
    Extract and validate years of experience from input.
    
    Args:
        experience: The experience string (e.g., "5 years", "5", "five").
    
    Returns:
        Tuple of (is_valid, years_as_integer).
    """
    # Try to extract a number from the string
    numbers = re.findall(r'\d+', experience)
    if numbers:
        years = int(numbers[0])
        if 0 <= years <= 50:
            return True, years
    
    # Handle word-based numbers
    word_to_num = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
        'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'fresher': 0, 'fresh': 0, 'none': 0
    }
    
    for word, num in word_to_num.items():
        if word in experience.lower():
            return True, num
    
    return False, -1


def is_exit_keyword(text: str) -> bool:
    """
    Check if the user's input contains a conversation-ending keyword.
    
    Args:
        text: The user's input text.
    
    Returns:
        True if an exit keyword is detected, False otherwise.
    """
    cleaned = text.strip().lower()
    # Check exact match first
    if cleaned in EXIT_KEYWORDS:
        return True
    # Check if the message starts with an exit keyword
    for keyword in EXIT_KEYWORDS:
        if cleaned.startswith(keyword):
            return True
    return False


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potentially harmful content.
    
    Args:
        text: The raw user input.
    
    Returns:
        Sanitized text string.
    """
    # Remove excessive whitespace
    text = ' '.join(text.split())
    # Limit input length to prevent abuse
    text = text[:2000]
    return text.strip()


def parse_tech_stack(tech_input: str) -> list[str]:
    """
    Parse a tech stack string into individual technologies.
    
    Args:
        tech_input: Comma/space separated list of technologies.
    
    Returns:
        List of individual technology names.
    """
    # Split by common separators
    separators = r'[,;/\n]'
    items = re.split(separators, tech_input)
    
    # Clean and filter
    technologies = []
    for item in items:
        cleaned = item.strip().strip('-').strip('•').strip()
        if cleaned and len(cleaned) > 1:
            technologies.append(cleaned)
    
    return technologies


def format_collected_info(candidate_data: dict) -> str:
    """
    Format collected candidate info for display.
    
    Args:
        candidate_data: Dictionary of collected candidate information.
    
    Returns:
        Formatted string representation.
    """
    field_labels = {
        'full_name': 'Name',
        'email': 'Email',
        'phone': 'Phone',
        'experience': 'Experience',
        'position': 'Position',
        'location': 'Location',
        'tech_stack': 'Tech Stack',
    }
    
    lines = []
    for key, label in field_labels.items():
        value = candidate_data.get(key, '')
        if value:
            if key == 'experience':
                lines.append(f"{label}: {value} years")
            elif key == 'tech_stack':
                if isinstance(value, list):
                    lines.append(f"{label}: {', '.join(value)}")
                else:
                    lines.append(f"{label}: {value}")
            else:
                lines.append(f"{label}: {value}")
    
    return '\n'.join(lines) if lines else 'No information collected yet.'
