"""
Configuration module for TalentScout Hiring Assistant.
Loads environment variables and defines application constants.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
MODEL_NAME = "gemini-2.0-flash"

# --- Model Parameters ---
TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 1024
TOP_P = 0.95

# --- Conversation Settings ---
EXIT_KEYWORDS = [
    "bye", "goodbye", "exit", "quit", "end", "stop",
    "thanks bye", "thank you bye", "see you", "take care",
    "done", "finished", "that's all", "no more"
]

# Number of technical questions per technology
TECH_QUESTIONS_COUNT = 4

# --- Application Info ---
APP_NAME = "TalentScout"
APP_TAGLINE = "Intelligent Hiring Assistant"
APP_VERSION = "1.0.0"
COMPANY_DESCRIPTION = (
    "TalentScout is a leading recruitment agency specializing in "
    "technology placements. We connect top tech talent with innovative companies."
)
