# TalentScout — Intelligent Hiring Assistant

An AI-powered hiring assistant chatbot for **TalentScout**, a fictional recruitment agency specializing in technology placements. The chatbot conducts initial candidate screening by gathering essential information and generating tailored technical assessment questions.

Built with **Streamlit** and **VoidAI/Groq LLM Models**.

---

## Features

| Feature | Description |
|---|---|
| **Intelligent Screening** | Guided multi-step conversation collecting candidate info |
| **Tech Assessment** | Auto-generates technical questions per declared technology |
| **Context-Aware** | Maintains conversation flow with contextual follow-ups |
| **Sentiment Analysis** | Detects candidate emotions and adjusts tone (TextBlob) |
| **Multilingual Support** | Responds in the candidate's language (powered by LLM) |
| **Fallback Handling** | Redirects off-topic inputs back to hiring context |
| **GDPR Compliant** | Anonymized storage, right to erasure support |
| **Progress Tracking** | Visual progress bar and sidebar info summary |
| **Notion UI Theme** | Minimalist aesthetic using black/white/gray and professional fonts |

---

## Architecture

```text
┌─────────────────────────────────────────────────┐
│                  Streamlit UI                   │
│              (app.py — Chat Interface)          │
├─────────────────────────────────────────────────┤
│            Conversation Manager                 │
│    (State Machine — conversation_manager.py)    │
├────────────┬──────────────┬─────────────────────┤
│ LLM Service│  Sentiment   │   Candidate Store   │
│(VoidAI API)│  (TextBlob)  │  (JSON / GDPR)      │
├────────────┴──────────────┴─────────────────────┤
│              Prompt Templates                   │
│           (prompts.py — All Prompts)            │
├─────────────────────────────────────────────────┤
│     Config (config.py)  │  Utils (utils.py)     │
└─────────────────────────────────────────────────┘
```

### Conversation Flow

```text
Greeting → Basic Info (Name/Email/Phone parsed simultaneously) → Experience → Position → Location → Tech Stack → Technical Questions → Closing
```

Each step validates input before advancing. The chatbot gracefully handles invalid inputs, off-topic messages, and exit keywords at any stage.

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- A free Groq API key or VoidAI API key

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/sainishant-b/PGAGI-Internship-Project.git
cd PGAGI-Internship-Project

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download TextBlob corpora (one-time)
python -m textblob.download_corpora

# 5. Configure your API key
# Edit the .env file and replace the placeholder:
# VOIDAI_API_KEY=gsk_your_groq_key_here

# 6. Run the application
python -m streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Usage Guide

1. **Start**: The chatbot greets you and asks for your full name, email, and phone number in a single message.
2. **Provide Info**: Answer each question (experience, position, location, tech stack).
3. **Technical Assessment**: After declaring your tech stack, the bot generates tailored questions.
4. **Answer Questions**: Respond to technical questions and receive constructive feedback.
5. **Complete**: Type "done" to finish the assessment, or "bye" to exit at any time.

### Sidebar Features
- **Progress Bar**: Visual indicator of screening completion
- **Candidate Info**: Real-time summary of collected information
- **Sentiment Indicator**: Shows detected emotional tone
- **New Session**: Reset button to start a fresh screening

---

## Technical Details

### Libraries
| Library | Purpose |
|---|---|
| `streamlit` | Frontend chat interface |
| `requests` | LLM REST API integration |
| `python-dotenv` | Secure environment variable loading |
| `textblob` | Sentiment analysis |

### Key Modules
| File | Purpose |
|---|---|
| `app.py` | Streamlit UI, session management, chat rendering |
| `conversation_manager.py` | State machine driving the conversation flow |
| `llm_service.py` | OpenAI-compatible REST API wrapper with error handling |
| `prompts.py` | All LLM prompt templates |
| `sentiment.py` | TextBlob sentiment analysis |
| `candidate_store.py` | GDPR-compliant JSON data storage |
| `utils.py` | Input validation and helper functions |
| `config.py` | Configuration and constants |

---

## Prompt Design

Prompts are centralized in `prompts.py` and designed with these principles:

1. **System Prompt**: Establishes the chatbot persona as TalentScout's hiring assistant with strict boundaries (no off-topic responses). Includes multilingual instructions.

2. **Stage-Specific Prompts**: Each information-gathering step has a dedicated prompt that acknowledges the previous input and naturally transitions to the next question.

3. **Tech Question Prompt**: Instructs the LLM to generate practical, scenario-based questions at intermediate-to-advanced difficulty for each declared technology.

4. **Sentiment Adjustment**: When negative sentiment is detected, a prefix is prepended to the prompt instructing the LLM to be more encouraging and patient.

5. **Data Extraction**: Custom prompts are used in the background to cleanly parse complex multi-field input (Name, Email, Phone) mathematically bypassing strict field validations.

6. **Fallback Prompt**: Provides context about the current stage and instructs the LLM to politely redirect off-topic inputs.

---

## Data Privacy (GDPR Compliance)

- **No PII in filenames**: Candidate data files use timestamp-based names
- **Secure storage**: Data saved as local JSON files in a git-ignored `data/` directory
- **Right to erasure**: Built-in function to delete individual candidate records
- **API key security**: Stored in `.env` file, never committed to version control
- **Minimal data**: Only collects information essential for the screening process

---

## Challenges & Solutions

| Challenge | Solution |
|---|---|
| **API Rate Limits** | Implemented exponential backoff and transparent error handling in llm_service |
| **Handling off-topic inputs** | System prompt with strict boundaries + dedicated fallback handler |
| **Input validation** | Extracted multiple inputs at once via LLM JSON parsing, supplemented with regex. |
| **UI Aesthetics** | Used a Notion-style config.toml file to enforce a clean interface across environments. |
| **Multilingual support** | Leveraged the LLM's built-in multilingual capabilities via prompt engineering |
| **Data privacy** | Anonymized storage, git-ignored data directory, `.env` for secrets |

---

## Bonus Features Implemented

- **Automated Final Evaluation**: Generates a comprehensive final evaluation outlining areas of excellence, a hypothetical score, and specific actionable improvement tips.
- **Sentiment Analysis**: TextBlob-based emotion detection with tone adjustment
- **Multilingual Support**: Automatic language detection and response matching
- **Minimalist UI**: Branded Streamlit interface utilizing a custom minimalist aesthetic configuration
- **Performance**: Stateless execution model avoids unnecessary API history payloads

---

## License

This project is developed as part of an internship assignment for PG AGI.

---

*Built by TalentScout*
