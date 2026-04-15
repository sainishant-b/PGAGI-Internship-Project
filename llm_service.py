"""
Google Gemini LLM service wrapper for TalentScout Hiring Assistant.
Handles all interactions with the Gemini API.
"""

import google.generativeai as genai
from config import GOOGLE_API_KEY, MODEL_NAME, TEMPERATURE, MAX_OUTPUT_TOKENS, TOP_P


class GeminiService:
    """Wrapper for Google Gemini API interactions."""

    def __init__(self):
        """Initialize the Gemini service with API key and model configuration."""
        if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
            raise ValueError(
                "Google API key not configured. "
                "Please set GOOGLE_API_KEY in your .env file. "
                "Get a free key at: https://aistudio.google.com/apikey"
            )

        genai.configure(api_key=GOOGLE_API_KEY)

        self.generation_config = genai.types.GenerationConfig(
            temperature=TEMPERATURE,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            top_p=TOP_P,
        )

        self.model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=self.generation_config,
        )

        # Start a persistent chat session for context retention
        self.chat = self.model.start_chat(history=[])

    def send_message(self, prompt: str) -> str:
        """
        Send a message to the Gemini model and get a response.

        Args:
            prompt: The prompt/message to send to the model.

        Returns:
            The model's text response.
        """
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "rate" in error_msg.lower():
                return (
                    "I'm experiencing high demand right now. "
                    "Please wait a moment and try again. 🙏"
                )
            elif "safety" in error_msg.lower():
                return (
                    "I couldn't process that input. "
                    "Could you please rephrase your response? 😊"
                )
            else:
                return (
                    "I encountered a temporary issue. "
                    "Please try again in a moment. 🔄"
                )

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
        self.chat = self.model.start_chat(history=[])
