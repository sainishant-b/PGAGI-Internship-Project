"""
Conversation manager for TalentScout Hiring Assistant.
Implements a state machine to guide the conversation flow.
"""

from enum import Enum
from prompts import (
    SYSTEM_PROMPT, GREETING_PROMPT, INFO_GATHERING_PROMPTS,
    TECH_QUESTION_PROMPT, EVALUATE_ANSWER_PROMPT,
    FALLBACK_PROMPT, CLOSING_PROMPT, SENTIMENT_ADJUSTED_PREFIX
)
from llm_service import GeminiService
from sentiment import analyze_sentiment, get_sentiment_context
from utils import (
    validate_email, validate_phone, validate_experience,
    is_exit_keyword, sanitize_input, parse_tech_stack, format_collected_info
)
from config import TECH_QUESTIONS_COUNT


class ConversationState(Enum):
    """Enum representing the stages of the screening conversation."""
    GREETING = "greeting"
    COLLECTING_NAME = "collecting_name"
    COLLECTING_EMAIL = "collecting_email"
    COLLECTING_PHONE = "collecting_phone"
    COLLECTING_EXPERIENCE = "collecting_experience"
    COLLECTING_POSITION = "collecting_position"
    COLLECTING_LOCATION = "collecting_location"
    COLLECTING_TECH_STACK = "collecting_tech_stack"
    ASKING_TECH_QUESTIONS = "asking_tech_questions"
    CLOSING = "closing"
    ENDED = "ended"


# Map states to human-readable step descriptions
STATE_DESCRIPTIONS = {
    ConversationState.GREETING: "Greeting",
    ConversationState.COLLECTING_NAME: "Collecting Full Name",
    ConversationState.COLLECTING_EMAIL: "Collecting Email Address",
    ConversationState.COLLECTING_PHONE: "Collecting Phone Number",
    ConversationState.COLLECTING_EXPERIENCE: "Collecting Years of Experience",
    ConversationState.COLLECTING_POSITION: "Collecting Desired Position",
    ConversationState.COLLECTING_LOCATION: "Collecting Location",
    ConversationState.COLLECTING_TECH_STACK: "Collecting Tech Stack",
    ConversationState.ASKING_TECH_QUESTIONS: "Technical Assessment",
    ConversationState.CLOSING: "Wrapping Up",
    ConversationState.ENDED: "Conversation Ended",
}


class ConversationManager:
    """
    Manages the conversation flow for the hiring assistant.
    Tracks state, collects candidate info, and coordinates with the LLM.
    """

    def __init__(self, llm_service: GeminiService):
        """
        Initialize the conversation manager.
        
        Args:
            llm_service: An instance of GeminiService for LLM interactions.
        """
        self.llm = llm_service
        self.state = ConversationState.GREETING
        self.candidate_data = {}
        self.tech_questions = []
        self.current_question_index = 0
        self.tech_answers = []
        self.sentiment_history = []
        self.conversation_history = []

    def get_greeting(self) -> str:
        """Generate the initial greeting message."""
        system_context = SYSTEM_PROMPT.format(
            current_step="Greeting",
            collected_info="None yet"
        )
        response = self.llm.generate_with_context(system_context, GREETING_PROMPT)
        self.state = ConversationState.COLLECTING_NAME
        return response

    def process_input(self, user_input: str) -> str:
        """
        Process user input based on the current conversation state.
        
        Args:
            user_input: The candidate's message.
        
        Returns:
            The assistant's response string.
        """
        # Sanitize input
        user_input = sanitize_input(user_input)
        
        if not user_input:
            return "I didn't catch that. Could you please try again? 😊"

        # Check for exit keywords
        if is_exit_keyword(user_input):
            return self._handle_closing(early_exit=True)

        # Analyze sentiment
        sentiment = analyze_sentiment(user_input)
        self.sentiment_history.append(sentiment)

        # Build sentiment context for the LLM
        sentiment_context = get_sentiment_context(sentiment)

        # Route to the appropriate handler based on current state
        handlers = {
            ConversationState.COLLECTING_NAME: self._handle_name,
            ConversationState.COLLECTING_EMAIL: self._handle_email,
            ConversationState.COLLECTING_PHONE: self._handle_phone,
            ConversationState.COLLECTING_EXPERIENCE: self._handle_experience,
            ConversationState.COLLECTING_POSITION: self._handle_position,
            ConversationState.COLLECTING_LOCATION: self._handle_location,
            ConversationState.COLLECTING_TECH_STACK: self._handle_tech_stack,
            ConversationState.ASKING_TECH_QUESTIONS: self._handle_tech_answer,
            ConversationState.CLOSING: self._handle_closing,
            ConversationState.ENDED: lambda x, s: "The conversation has ended. Please start a new session to begin again. 👋",
        }

        handler = handlers.get(self.state, self._handle_fallback)
        return handler(user_input, sentiment_context)

    def _build_system_context(self, sentiment_context: str = "") -> str:
        """Build the system prompt with current state and collected info."""
        state_desc = STATE_DESCRIPTIONS.get(self.state, "Unknown")
        collected = format_collected_info(self.candidate_data)
        
        context = SYSTEM_PROMPT.format(
            current_step=state_desc,
            collected_info=collected
        )
        
        if sentiment_context:
            context = sentiment_context + "\n\n" + context
        
        return context

    def _handle_name(self, user_input: str, sentiment_ctx: str) -> str:
        """Process and store the candidate's full name."""
        self.candidate_data['full_name'] = user_input.strip().title()
        self.state = ConversationState.COLLECTING_EMAIL
        
        prompt = INFO_GATHERING_PROMPTS['full_name'].format(input=user_input)
        return self.llm.generate_with_context(
            self._build_system_context(sentiment_ctx), prompt
        )

    def _handle_email(self, user_input: str, sentiment_ctx: str) -> str:
        """Validate and store the candidate's email."""
        email = user_input.strip()
        
        if not validate_email(email):
            return (
                "That doesn't look like a valid email address. "
                "Could you please provide a valid email? (e.g., name@example.com) 📧"
            )
        
        self.candidate_data['email'] = email
        self.state = ConversationState.COLLECTING_PHONE
        
        prompt = INFO_GATHERING_PROMPTS['email'].format(input=email)
        return self.llm.generate_with_context(
            self._build_system_context(sentiment_ctx), prompt
        )

    def _handle_phone(self, user_input: str, sentiment_ctx: str) -> str:
        """Validate and store the candidate's phone number."""
        phone = user_input.strip()
        
        if not validate_phone(phone):
            return (
                "That doesn't seem like a valid phone number. "
                "Please enter a phone number with 7-15 digits. (e.g., +91-9876543210) 📱"
            )
        
        self.candidate_data['phone'] = phone
        self.state = ConversationState.COLLECTING_EXPERIENCE
        
        prompt = INFO_GATHERING_PROMPTS['phone'].format(input=phone)
        return self.llm.generate_with_context(
            self._build_system_context(sentiment_ctx), prompt
        )

    def _handle_experience(self, user_input: str, sentiment_ctx: str) -> str:
        """Validate and store years of experience."""
        is_valid, years = validate_experience(user_input)
        
        if not is_valid:
            return (
                "I couldn't quite understand the years of experience. "
                "Could you please provide a number? (e.g., '3' or '5 years') 💼"
            )
        
        self.candidate_data['experience'] = years
        self.state = ConversationState.COLLECTING_POSITION
        
        prompt = INFO_GATHERING_PROMPTS['experience'].format(input=f"{years} years")
        return self.llm.generate_with_context(
            self._build_system_context(sentiment_ctx), prompt
        )

    def _handle_position(self, user_input: str, sentiment_ctx: str) -> str:
        """Store the candidate's desired position(s)."""
        self.candidate_data['position'] = user_input.strip()
        self.state = ConversationState.COLLECTING_LOCATION
        
        prompt = INFO_GATHERING_PROMPTS['position'].format(input=user_input)
        return self.llm.generate_with_context(
            self._build_system_context(sentiment_ctx), prompt
        )

    def _handle_location(self, user_input: str, sentiment_ctx: str) -> str:
        """Store the candidate's current location."""
        self.candidate_data['location'] = user_input.strip()
        self.state = ConversationState.COLLECTING_TECH_STACK
        
        prompt = INFO_GATHERING_PROMPTS['location'].format(input=user_input)
        return self.llm.generate_with_context(
            self._build_system_context(sentiment_ctx), prompt
        )

    def _handle_tech_stack(self, user_input: str, sentiment_ctx: str) -> str:
        """Parse and store the tech stack, then generate technical questions."""
        technologies = parse_tech_stack(user_input)
        
        if not technologies:
            return (
                "I couldn't identify any technologies from your input. "
                "Could you please list your tech stack separated by commas? "
                "(e.g., Python, React, PostgreSQL, Docker) 🛠️"
            )
        
        self.candidate_data['tech_stack'] = technologies
        self.candidate_data['tech_stack_raw'] = user_input.strip()
        
        # Acknowledge the tech stack
        ack_prompt = INFO_GATHERING_PROMPTS['tech_stack'].format(
            input=', '.join(technologies)
        )
        ack_response = self.llm.generate_with_context(
            self._build_system_context(sentiment_ctx), ack_prompt
        )
        
        # Generate technical questions
        question_prompt = TECH_QUESTION_PROMPT.format(
            tech_stack=', '.join(technologies),
            num_questions=TECH_QUESTIONS_COUNT
        )
        questions_response = self.llm.send_message(question_prompt)
        
        self.tech_questions = [questions_response]
        self.current_question_index = 0
        self.state = ConversationState.ASKING_TECH_QUESTIONS
        
        return f"{ack_response}\n\n---\n\n{questions_response}\n\nPlease take your time to answer these questions. You can answer all at once or one by one. When you're done, just let me know! 😊"

    def _handle_tech_answer(self, user_input: str, sentiment_ctx: str) -> str:
        """Process technical answers and provide feedback."""
        self.tech_answers.append(user_input)
        
        # Check if candidate wants to finish
        done_keywords = ["done", "finished", "that's all", "next", "move on", "complete"]
        if any(kw in user_input.lower() for kw in done_keywords):
            return self._handle_closing()
        
        # Evaluate the answer and provide feedback
        eval_prompt = EVALUATE_ANSWER_PROMPT.format(
            question="Technical Assessment",
            answer=user_input
        )
        
        response = self.llm.generate_with_context(
            self._build_system_context(sentiment_ctx), eval_prompt
        )
        
        response += "\n\nFeel free to continue answering, or type **'done'** when you're finished with the technical assessment. 📝"
        return response

    def _handle_closing(self, early_exit: bool = False, *args) -> str:
        """Generate the closing message and end the conversation."""
        self.state = ConversationState.ENDED
        
        name = self.candidate_data.get('full_name', 'Candidate')
        
        if early_exit:
            closing_prompt = CLOSING_PROMPT.format(name=name)
            return self.llm.send_message(closing_prompt)
        
        closing_prompt = CLOSING_PROMPT.format(name=name)
        return self.llm.send_message(closing_prompt)

    def _handle_fallback(self, user_input: str, sentiment_ctx: str) -> str:
        """Handle unexpected inputs or states."""
        state_desc = STATE_DESCRIPTIONS.get(self.state, "Unknown")
        prompt = FALLBACK_PROMPT.format(
            input=user_input,
            current_step=state_desc
        )
        return self.llm.generate_with_context(
            self._build_system_context(sentiment_ctx), prompt
        )

    def get_current_state_description(self) -> str:
        """Get a human-readable description of the current state."""
        return STATE_DESCRIPTIONS.get(self.state, "Unknown")

    def get_progress_percentage(self) -> int:
        """Calculate conversation progress as a percentage."""
        state_order = list(ConversationState)
        current_index = state_order.index(self.state)
        return int((current_index / (len(state_order) - 1)) * 100)

    def get_latest_sentiment(self) -> dict:
        """Get the most recent sentiment analysis result."""
        if self.sentiment_history:
            return self.sentiment_history[-1]
        return {"polarity": 0.0, "label": "neutral", "emoji": "😐"}
