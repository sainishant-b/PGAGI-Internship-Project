"""
LLM service wrapper for TalentScout Hiring Assistant.
Supports VoidAI and Groq as providers (OpenAI-compatible APIs).
"""

import time
import requests
from config import (
    VOIDAI_API_KEY, VOIDAI_BASE_URL, MODEL_NAME,
    TEMPERATURE, MAX_OUTPUT_TOKENS
)


class LLMService:
    """Wrapper for OpenAI-compatible chat completions API."""

    MAX_RETRIES = 3
    RETRY_DELAY = 3  # seconds

    def __init__(self):
        """Initialize the LLM service with API key."""
        if not VOIDAI_API_KEY or VOIDAI_API_KEY == "your_api_key_here":
            raise ValueError(
                "API key not configured. "
                "Please set VOIDAI_API_KEY in your .env file."
            )

        self.api_key = VOIDAI_API_KEY
        self.base_url = VOIDAI_BASE_URL
        self.model = MODEL_NAME

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        # Chat history for context retention (OpenAI message format)
        self.history = []

    def send_message(self, prompt: str) -> str:
        """
        Send a message to the LLM with automatic retry.

        Args:
            prompt: The prompt/message to send to the model.

        Returns:
            The model's text response.
        """
        # Add user message to history
        self.history.append({"role": "user", "content": prompt})

        for attempt in range(self.MAX_RETRIES):
            try:
                payload = {
                    "model": self.model,
                    "messages": self.history,
                    "temperature": TEMPERATURE,
                    "max_tokens": MAX_OUTPUT_TOKENS,
                }

                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=60,
                )

                if response.status_code == 200:
                    data = response.json()
                    assistant_text = data["choices"][0]["message"]["content"]

                    # Add assistant response to history
                    self.history.append({"role": "assistant", "content": assistant_text})
                    return assistant_text

                elif response.status_code == 429:
                    # Rate limited — retry
                    if attempt < self.MAX_RETRIES - 1:
                        time.sleep(self.RETRY_DELAY * (attempt + 1))
                        continue
                    self.history.pop()
                    return (
                        "I'm experiencing high demand right now. "
                        "Please wait a moment and try again. 🙏"
                    )
                else:
                    # Parse error body for details
                    try:
                        err_data = response.json()
                        err_msg = err_data.get("error", {}).get("message", "Unknown error")
                    except Exception:
                        err_msg = response.text[:200]

                    self.history.pop()
                    return (
                        f"⚠️ API Error (HTTP {response.status_code}): {err_msg}\n\n"
                        "Please check your API key in the `.env` file and restart."
                    )

            except requests.exceptions.Timeout:
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                    continue
                self.history.pop()
                return "The request timed out. Please try again. ⏳"

            except Exception as e:
                self.history.pop()
                return f"Error: {str(e)[:200]}. Please try again. 🔄"

        self.history.pop()
        return "Something went wrong. Please try again. 🔄"

    def generate_with_context(self, system_prompt: str, user_message: str) -> str:
        """
        Generate a response with a specific system context.

        Args:
            system_prompt: The system-level instruction/context.
            user_message: The user's actual message.

        Returns:
            The model's text response.
        """
        full_prompt = f"{system_prompt}\n\nCandidate says: {user_message}"
        return self.send_message(full_prompt)

    def reset_chat(self):
        """Reset the chat session to start fresh."""
        self.history = []
