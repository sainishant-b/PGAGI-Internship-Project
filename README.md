# 🎯 TalentScout — Intelligent Hiring Assistant

An AI-powered hiring assistant chatbot for **TalentScout**, a fictional recruitment agency specializing in technology placements. The chatbot conducts initial candidate screening by gathering essential information and generating tailored technical assessment questions.

Built with **Streamlit** and **Google Gemini AI**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **Intelligent Screening** | Guided multi-step conversation collecting candidate info |
| 🧠 **Tech Assessment** | Auto-generates 3–5 technical questions per declared technology |
| 💬 **Context-Aware** | Maintains conversation flow with contextual follow-ups |
| 😊 **Sentiment Analysis** | Detects candidate emotions and adjusts tone (TextBlob) |
| 🌍 **Multilingual Support** | Responds in the candidate's language (powered by Gemini) |
| 🛡️ **Fallback Handling** | Redirects off-topic inputs back to hiring context |
| 🔒 **GDPR Compliant** | Anonymized storage, right to erasure support |
| 🎯 **Progress Tracking** | Visual progress bar and sidebar info summary |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  Streamlit UI                    │
│              (app.py — Chat Interface)           │
├─────────────────────────────────────────────────┤
│            Conversation Manager                  │
│    (State Machine — conversation_manager.py)     │
├────────────┬──────────────┬─────────────────────┤
│ LLM Service│  Sentiment   │   Candidate Store   │
│(Gemini API)│  (TextBlob)  │  (JSON / GDPR)      │
├────────────┴──────────────┴─────────────────────┤
│              Prompt Templates                    │
│           (prompts.py — All Prompts)             │
├─────────────────────────────────────────────────┤
│     Config (config.py)  │  Utils (utils.py)     │
└─────────────────────────────────────────────────┘
```

### Conversation Flow

```
Greeting → Name → Email → Phone → Experience → Position → Location → Tech Stack → Technical Questions → Closing
```

Each step validates input before advancing. The chatbot gracefully handles invalid inputs, off-topic messages, and exit keywords at any stage.

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
- A free Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

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
# GOOGLE_API_KEY=your_actual_api_key_here

# 6. Run the application
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 📖 Usage Guide

1. **Start**: The chatbot greets you and asks for your full name
2. **Provide Info**: Answer each question (name, email, phone, experience, position, location, tech stack)
3. **Technical Assessment**: After declaring your tech stack, the bot generates tailored questions
4. **Answer Questions**: Respond to technical questions and receive constructive feedback
5. **Complete**: Type "done" to finish the assessment, or "bye" to exit at any time

### Sidebar Features
- **Progress Bar**: Visual indicator of screening completion
- **Candidate Info**: Real-time summary of collected information
- **Sentiment Indicator**: Shows detected emotional tone
- **New Session**: Reset button to start a fresh screening

---

## 🛠️ Technical Details

### Libraries
| Library | Purpose |
|---|---|
| `streamlit` | Frontend chat interface |
| `google-generativeai` | Google Gemini LLM integration |
| `python-dotenv` | Secure environment variable loading |
| `textblob` | Sentiment analysis |

### Model
- **Model**: Google Gemini 2.0 Flash (`gemini-2.0-flash`)
- **Temperature**: 0.7 (balanced creativity/consistency)
- **Context**: Persistent chat session for multi-turn context retention

### Key Modules
| File | Purpose |
|---|---|
| `app.py` | Streamlit UI, session management, chat rendering |
| `conversation_manager.py` | State machine driving the conversation flow |
| `llm_service.py` | Gemini API wrapper with error handling |
| `prompts.py` | All LLM prompt templates |
| `sentiment.py` | TextBlob sentiment analysis |
| `candidate_store.py` | GDPR-compliant JSON data storage |
| `utils.py` | Input validation and helper functions |
| `config.py` | Configuration and constants |

---

## 📝 Prompt Design

Prompts are centralized in `prompts.py` and designed with these principles:

1. **System Prompt**: Establishes the chatbot persona as TalentScout's hiring assistant with strict boundaries (no off-topic responses). Includes multilingual instructions.

2. **Stage-Specific Prompts**: Each information-gathering step has a dedicated prompt that acknowledges the previous input and naturally transitions to the next question.

3. **Tech Question Prompt**: Instructs the LLM to generate practical, scenario-based questions at intermediate-to-advanced difficulty for each declared technology.

4. **Sentiment Adjustment**: When negative sentiment is detected, a prefix is prepended to the prompt instructing the LLM to be more encouraging and patient.

5. **Fallback Prompt**: Provides context about the current stage and instructs the LLM to politely redirect off-topic inputs.

---

## 🔒 Data Privacy (GDPR Compliance)

- **No PII in filenames**: Candidate data files use timestamp-based names
- **Secure storage**: Data saved as local JSON files in a git-ignored `data/` directory
- **Right to erasure**: Built-in function to delete individual candidate records
- **API key security**: Stored in `.env` file, never committed to version control
- **Minimal data**: Only collects information essential for the screening process

---

## 🧩 Challenges & Solutions

| Challenge | Solution |
|---|---|
| **Maintaining conversation context** | Used Gemini's persistent `start_chat()` with full history retention |
| **Handling off-topic inputs** | System prompt with strict boundaries + dedicated fallback handler |
| **Input validation** | Custom validators for email, phone, experience with user-friendly error messages |
| **Sentiment detection** | TextBlob for lightweight, inference-free sentiment analysis |
| **Multilingual support** | Leveraged Gemini's built-in multilingual capabilities via prompt engineering |
| **Data privacy** | Anonymized storage, git-ignored data directory, `.env` for secrets |

---

## 🌟 Bonus Features Implemented

- ✅ **Sentiment Analysis**: TextBlob-based emotion detection with tone adjustment
- ✅ **Multilingual Support**: Automatic language detection and response matching
- ✅ **Custom UI**: Branded Streamlit interface with progress tracking
- ✅ **Performance**: Efficient state machine avoids unnecessary LLM calls

---

## 📄 License

This project is developed as part of an internship assignment for PG AGI.

---

*Built with ❤️ using Streamlit and Google Gemini AI*
