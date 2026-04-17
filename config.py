"""
Configuration module for TalentScout Hiring Assistant.
Loads environment variables and defines application constants.

Supports two providers (set via VOIDAI_API_KEY in .env):
  - VoidAI: https://api.voidai.app/v1/chat/completions
  - Groq (free fallback): https://api.groq.com/openai/v1/chat/completions
    Get a free key at: https://console.groq.com/keys

The provider is auto-detected from the API key prefix.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Configuration ---
VOIDAI_API_KEY = os.getenv("VOIDAI_API_KEY", "")

# Auto-detect provider from key prefix
if VOIDAI_API_KEY.startswith("gsk_"):
    # Groq key detected
    VOIDAI_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
    MODEL_NAME = "llama-3.3-70b-versatile"
else:
    # Default: VoidAI
    VOIDAI_BASE_URL = "https://api.voidai.app/v1/chat/completions"
    MODEL_NAME = "gpt-4o"

# --- Model Parameters ---
TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 1024

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
