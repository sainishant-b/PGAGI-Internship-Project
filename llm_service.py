"""
Google Gemini LLM service wrapper for TalentScout Hiring Assistant.
Handles all interactions with the Gemini API using the google-genai SDK.
"""

import time
from google import genai
from google.genai import types
from config import GOOGLE_API_KEY, MODEL_NAME, TEMPERATURE, MAX_OUTPUT_TOKENS, TOP_P


class GeminiService:
    """Wrapper for Google Gemini API interactions."""

    MAX_RETRIES = 3
    RETRY_DELAY = 10  # seconds

    def __init__(self):
        """Initialize the Gemini service with API key and model configuration."""
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
            raise ValueError(
                "Google API key not configured. "
                "Please set GOOGLE_API_KEY in your .env file. "
                "Get a free key at: https://aistudio.google.com/apikey"
            )

        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model_name = MODEL_NAME

        self.generation_config = types.GenerateContentConfig(
            temperature=TEMPERATURE,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            top_p=TOP_P,
        )

        # Chat history for context retention
        self.history = []

    def send_message(self, prompt: str) -> str:
        """
        Send a message to the Gemini model with automatic retry on rate limits.

        Args:
            prompt: The prompt/message to send to the model.

        Returns:
            The model's text response.
        """
        # Add user message to history
        self.history.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        ))

        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=self.history,
                    config=self.generation_config,
                )

                assistant_text = response.text

                # Add assistant response to history
                self.history.append(types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=assistant_text)]
                ))

                return assistant_text

            except Exception as e:
                error_msg = str(e).lower()

                # Rate limit / resource exhausted — retry after delay
                if "429" in str(e) or "retrydelay" in error_msg or "resource" in error_msg or "quota" in error_msg:
                    if attempt < self.MAX_RETRIES - 1:
                        wait_time = self.RETRY_DELAY * (attempt + 1)
                        time.sleep(wait_time)
                        continue

                    # All retries exhausted
                    # Remove the failed user message from history
                    self.history.pop()
                    return (
                        "I'm experiencing high demand right now. "
                        "Please wait a moment and try sending your message again. 🙏"
                    )

                elif "safety" in error_msg or "blocked" in error_msg:
                    self.history.pop()
                    return (
                        "I couldn't process that input. "
                        "Could you please rephrase your response? 😊"
                    )
                else:
                    self.history.pop()
                    return (
                        f"I encountered an issue: {str(e)[:200]}. "
                        "Please try again. 🔄"
                    )

        # Should not reach here, but just in case
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
