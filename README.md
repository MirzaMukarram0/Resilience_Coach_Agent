# Resilience Coach Agent

An AI-powered mental wellness support system providing emotional analysis, stress detection, and personalized coping strategies using Gemini API and LangGraph.

## 🎯 Project Overview

The Resilience Coach Agent is designed to help users manage stress, build emotional resilience, and receive personalized coping strategies through AI-driven conversations. Built with a Supervisor-Worker architecture, it operates as an independent worker agent callable via JSON contracts.

## ✨ Features

- **Emotional Tone Analysis**: Detects sentiment and emotional states using Gemini LLM
- **Stress Level Detection**: Identifies stress indicators in user input
- **Personalized Recommendations**: Provides breathing exercises, grounding techniques, and mindfulness tasks
- **Empathetic Conversation**: Natural, supportive communication style
- **Robust Input Validation**: Prevents empty, spam, and malicious inputs
- **Security Hardened**: XSS prevention, rate limiting, and comprehensive error handling
- **Privacy-First**: No personal data storage, anonymized logging only
- **Supervisor Integration**: JSON-based API for external system connectivity

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **AI/NLP**: Google Gemini API
- **Orchestration**: LangGraph

## 📋 Prerequisites

- Python 3.8+
- Gemini API key (free tier available)
- pip (Python package manager)

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/MirzaMukarram0/Resilience_Coach_Agent.git
cd Resilience_Coach_Agent
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Windows
copy .env.example .env

# Edit .env and add your Gemini API key
# Get your key from: https://makersuite.google.com/app/apikey
```

## 🎮 Usage

### Quick Start (Recommended)
Run everything with a single command:
```bash
python agent.py
```
This will:
- Start the Flask backend on port 5000
- Start the frontend server on port 8000
- Automatically open the web interface in your browser

Press `Ctrl+C` to stop all servers.

### Manual Start (Alternative)

1. **Run the Flask application**
```bash
python -m backend.app
```

2. **Access the web interface**
Open `frontend/index.html` in your browser, or serve it with:
```bash
# From frontend directory
python -m http.server 8000
```
Then navigate to: `http://localhost:8000`

3. **API Integration**

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Resilience Agent Request:**
```bash
curl -X POST http://localhost:5000/resilience \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "resilience_coach",
    "input_text": "I am feeling overwhelmed and anxious",
    "metadata": {
      "user_id": "abc123",
      "language": "en"
    }
  }'
```

## 📁 Project Structure

```
Resilience_Coach_Agent/
├── backend/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── config.py         # Configuration
│   │   ├── gemini.py         # Gemini API client
│   │   ├── recommendations.py # Coping strategies
│   │   └── workflow.py       # LangGraph workflow
│   ├── routes/
│   │   ├── __init__.py
│   │   └── api.py            # API endpoints
│   ├── __init__.py
│   └── app.py                # Flask application
├── frontend/
│   ├── index.html            # Web interface
│   ├── styles.css            # Styling
│   └── app.js                # Frontend logic
├── agent.py                  # Unified launcher
├── requirements.txt
├── .env.example
└── README.md
```

## 🧪 Testing

### Automated Test Suite:
```bash
python test_api.py
```
Runs 11 comprehensive tests including:
- Valid requests
- Input validation (empty, short, long)
- Spam detection
- XSS prevention
- Missing/invalid fields
- Multiple emotional states

### Quick Verification:
```bash
python quick_verify.py
```

### Manual Tests:
```bash
# Health check
curl http://localhost:5000/health

# Valid request
curl -X POST http://localhost:5000/resilience -H "Content-Type: application/json" -d "{\"agent\":\"resilience_coach\",\"input_text\":\"I feel stressed\"}"

# See manual_tests.ps1 for more examples
```

## 📝 API Documentation

### Request Format
```json
{
  "agent": "resilience_coach",
  "input_text": "user message here",
  "metadata": {
    "user_id": "optional_id",
    "language": "en"
  }
}
```

### Response Format
```json
{
  "agent": "resilience_coach",
  "status": "success",
  "analysis": {
    "sentiment": "negative",
    "stress_level": "high",
    "emotions": ["anxiety", "overwhelm"]
  },
  "recommendation": {
    "type": "breathing_exercise",
    "steps": ["Step 1", "Step 2", "Step 3"]
  },
  "message": "Supportive message here"
}
```

## 🔒 Security & Privacy

### Security Features:
- **Input Validation**: All inputs validated and sanitized
- **XSS Prevention**: Blocks script tags and malicious code
- **Rate Limiting**: 30 requests per minute per user
- **Spam Detection**: Filters gibberish and repeated characters
- **Response Validation**: Prevents hallucination and invalid outputs
- **Error Handling**: Comprehensive error handling at all levels

### Privacy:
- No personal identifiers stored
- Anonymized logging only
- Not a replacement for professional mental health services
- No medical diagnosis provided

## 📅 Project Timeline

- **Deadline**: December 12, 2025
- **Status**: In Development

## 👤 Author

**Mirza Mukarram**
- GitHub: [@MirzaMukarram0](https://github.com/MirzaMukarram0)

## 📄 License

This project is developed as part of an academic semester project.

## 🙏 Acknowledgments

- Google Gemini API for NLP capabilities
- LangGraph for workflow orchestration
- Flask community for excellent documentation
