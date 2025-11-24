# Resilience Coach Agent

An intelligent AI-powered mental wellness support system with **pure AI analysis**, **long-term memory**, **reasoning capabilities**, and **transparent error handling** using Gemini API, LangGraph, and ChromaDB.

## 🎯 Project Overview

The Resilience Coach Agent provides context-aware emotional support through an advanced **pure AI reasoning system** that remembers past conversations, detects patterns, and adapts recommendations based on user history. Built with intelligent conditional routing, memory-enhanced analysis, and **complete transparency about AI service status**.

## ✨ Key Features

### 🧠 **Pure AI Intelligence System**
- **Zero Hardcoded Analysis**: All emotional analysis powered by Gemini AI (no rule-based fallbacks)
- **Context-Aware Analysis**: Uses past interactions to understand recurring patterns
- **LangGraph Reasoning**: 9-node workflow with conditional branching logic
- **Confidence Scoring**: Measures analysis certainty for transparent AI behavior
- **Reasoning Traces**: Explains how AI conclusions were reached
- **Transparent Error Handling**: Honest reporting of API quotas and service status

### 💾 **Long-Term Memory (ChromaDB)**
- **Semantic Search**: Retrieves relevant past conversations using embeddings
- **Emotional Pattern Detection**: Identifies recurring emotions, stress trends, crisis frequency
- **Personalized Recommendations**: Avoids suggesting ineffective strategies
- **Privacy-Compliant**: GDPR-ready user data deletion

### 🚨 **Crisis Detection & Routing**
- **Automatic Crisis Assessment**: Scores messages 0-1 for crisis severity
- **Conditional Workflow**: High-risk messages (>0.7) route to specialized crisis response
- **Emergency Resources**: Provides suicide hotlines and immediate support contacts
- **Escalation Logic**: Detects suicidal ideation, self-harm indicators, extreme hopelessness

### 🎯 **Personalized Coping Strategies**
- 8 evidence-based strategies (breathing, grounding, meditation, journaling, etc.)
- Memory-aware recommendations (avoids repeating recent strategies)
- Pattern-based selection (loneliness → connection, burnout → rest)
- Alternative strategy suggestions for better engagement

### 🔐 **Security & Validation**
- Input sanitization (XSS prevention, spam detection)
- Rate limiting (15 req/min for Gemini API compliance)
- Response validation (prevents hallucination)
- Comprehensive error handling with transparent API status
- **Honest Error States**: Never shows fake "neutral" responses during API issues

## 🏗️ Architecture

### Workflow Graph (LangGraph)
```
memory_retrieval → analyze → crisis_detection → [ROUTING]
                                                    ↓
                               ┌───────────────────┴────────────────────┐
                               ↓                                        ↓
                        [crisis > 0.7]                            [normal flow]
                               ↓                                        ↓
                       crisis_response                            reasoning
                               ↓                                        ↓
                               └───────────→ memory_storage ←──────────┘
                                                ↓
                                           recommend
                                                ↓
                                            support
                                                ↓
                                            format
```

### State Structure
```python
AgentState {
    user_input: str                    # Current message
    user_id: str                       # User identifier for memory
    memory_context: list               # Relevant past interactions
    emotional_patterns: dict           # Recurring emotions, avg stress, crisis frequency
    analysis: dict                     # Sentiment, stress, emotions, confidence, reasoning
    crisis_score: float               # 0-1 crisis severity
    reasoning_trace: str              # Explanation of analysis
    recommendation: dict              # Strategy type and steps
    message: str                      # Supportive response
    confidence_score: float           # Analysis confidence
}
```

## 🛠️ Tech Stack

- **Backend**: Flask 3.0.0 (Python)
- **AI/NLP**: Google Gemini API (gemini-2.0-flash-lite for optimal quota usage)
- **Architecture**: Pure AI - zero hardcoded sentiment analysis or recommendations
- **Orchestration**: LangGraph 0.2+ (reasoning graph with conditional routing)
- **Memory**: ChromaDB 0.4.22 (vector database with persistent storage)
- **Embeddings**: Google Generative AI (embedding-001)
- **Deployment**: Gunicorn + Render
- **Error Handling**: Transparent API status with honest fallbacks

## 📋 Prerequisites

- Python 3.8+
- Gemini API key (free tier available at [Google AI Studio](https://makersuite.google.com/app/apikey))
- pip (Python package manager)

## 🚀 Installation

### Local Development

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

# Linux/Mac
cp .env.example .env

# Edit .env and add your Gemini API key
# Get your key from: https://makersuite.google.com/app/apikey
```

### 🌐 Production Deployment (Render)

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide**

Quick steps:
1. Push code to GitHub
2. Create free account on [Render](https://render.com)
3. Connect repository and deploy
4. Add `GEMINI_API_KEY` environment variable

Your app will be live at: `https://your-app-name.onrender.com`

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
│   │   ├── config.py             # Configuration (gemini-2.0-flash-lite)
│   │   ├── gemini.py             # Pure AI Gemini client (NO hardcoded rules)
│   │   ├── memory.py             # ChromaDB memory layer
│   │   ├── recommendations.py    # Deprecated - Gemini handles all recommendations
│   │   └── workflow.py           # LangGraph reasoning workflow (9 nodes)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── api.py                # API endpoints with transparent error handling
│   ├── utils.py                  # Input/output validation (supports error states)
│   ├── __init__.py
│   └── app.py                    # Flask application
├── frontend/
│   ├── index.html                # Web interface with error state display
│   ├── styles.css                # Styling (includes API error styling)
│   └── app.js                    # Frontend logic (handles error states)
├── chroma_db/                    # ChromaDB persistent storage
│   ├── .gitkeep                  # Ensures directory exists in deployment
│   └── chroma.sqlite3            # Database file (excluded from git)
├── deployment/
│   ├── Procfile                  # Heroku deployment config
│   ├── render.yaml               # Render deployment config (updated)
│   └── runtime.txt               # Python version specification
├── testing/
│   ├── test_api.py               # Comprehensive API test suite
│   ├── test_quota.py             # API quota testing script
│   └── test_expected_behavior.py # Expected behavior simulation
├── agent.py                      # Unified launcher (starts both servers)
├── requirements.txt              # All dependencies (updated)
├── .env.example                  # Environment template
├── .gitignore                    # Updated for ChromaDB files
├── README.md                     # This comprehensive guide
└── improvements.md               # Development notes
```

## 🧪 Memory & Context Management

### How Memory Works
1. **Storage**: Every interaction is stored with embeddings in ChromaDB
2. **Retrieval**: When a user sends a message, the system:
   - Performs semantic search to find 3 similar past conversations
   - Analyzes emotional patterns (top 3 recurring emotions, avg stress, crisis frequency)
3. **Usage**: Memory context informs:
   - Analysis (detects escalation: "You mentioned feeling lonely last week...")
   - Recommendations (avoids repeating strategies that didn't help)
   - Support messages (shows continuity: "I remember you mentioned...")

### Stored Metadata
```json
{
  "user_id": "user_identifier",
  "timestamp": "2025-11-24T19:15:00",
  "sentiment": "negative",
  "stress_level": "high",
  "crisis_score": 0.8,
  "emotions": ["anxiety", "overwhelm"],
  "strategy_type": "grounding_technique"
}
```

### Privacy & Data Management
- **Isolation**: Each user's data is tagged with `user_id` (can be anonymous)
- **Deletion**: Call `memory_store.clear_user_history(user_id)` for GDPR compliance
- **Persistence**: Data stored in `chroma_db/` directory (survives restarts)
- **No PII**: System never stores names, emails, or identifiable information

## ⚠️ Troubleshooting

### Gemini API Quota Exceeded (429 Error)
**Symptoms**: Response shows API error states instead of fake analysis:
```json
{
  "sentiment": "error_quota_exceeded",
  "stress_level": "api_unavailable",
  "message": "❌ AI Support Unavailable: Gemini API quota exceeded"
}
```

**Cause**: Free tier limits for `gemini-2.0-flash-lite`:
- 15 requests/minute  
- Daily token limits
- Embedding limits for memory storage

**Solutions**:
1. **Wait 24 hours** - Quota resets daily for free tier
2. **Get new API key** - Create from different Google account:
   - Visit: https://makersuite.google.com/app/apikey  
   - Create new project with fresh quotas
3. **Upgrade to paid plan** - Remove quota limitations
4. **Check current usage**: https://ai.dev/usage?tab=rate-limit

**✅ Note**: The system now shows honest error states instead of misleading "neutral" responses
   ```
3. **Get new API key** - Create another at [Google AI Studio](https://makersuite.google.com/app/apikey)
4. **Upgrade to paid tier** - Remove all limits at [Google AI](https://ai.google.dev/pricing)

### Memory Not Working
- Ensure `user_id` is provided in request metadata
- Check `chroma_db/` directory exists and has write permissions
- Verify embeddings aren't hitting quota (separate limit from generation)

### Server Won't Start
- Check Python version (3.8+ required)
- Install dependencies: `pip install -r requirements.txt`
- Verify `.env` file exists with `GEMINI_API_KEY`
- Check port 5000 isn't already in use

## 📝 API Documentation

### Request Format (Updated)
```json
{
  "agent": "resilience_coach",
  "input_text": "user message here",
  "metadata": {
    "user_id": "optional_user_identifier",  // For memory tracking
    "language": "en"
  }
}
```

### Response Format (Enhanced)
```json
{
  "agent": "resilience_coach",
  "status": "success",
  "analysis": {
    "sentiment": "negative",              // positive/neutral/negative/deeply_negative/error_quota_exceeded/error_api_failed
    "stress_level": "high",               // low/medium/high/crisis/api_unavailable
    "emotions": ["anxiety", "overwhelm"], // Detected emotions or ["api_quota_exceeded"] for errors
    "confidence": 0.85,                   // Analysis confidence (0.0 for API errors)
    "reasoning": "User expressed..."      // AI reasoning or error details
  },
  "crisis_score": 0.3,                    // Crisis severity (0.5 default for errors)
  "confidence": 0.85,                     // Overall confidence (0.0 for API errors)
  "reasoning": "Based on patterns...",    // Full reasoning or error explanation
  "recommendation": {
    "type": "breathing_exercise",         // or "api_quota_exceeded" for errors
    "name": "Breathing Exercise",
    "steps": ["Step 1", "Step 2", ...]   // or error messages for API issues
  },
  "message": "Supportive message with context awareness" // or honest error message
}

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
    "user_id": "optional_id",       // For memory persistence
    "language": "en"               // Currently supports English
  }
}
```

### Response Format  
**✅ Success Response (API Working):**
```json
{
  "agent": "resilience_coach",
  "status": "success",
  "analysis": {
    "sentiment": "negative",              // AI-analyzed emotional state
    "stress_level": "high",               // AI-assessed stress level
    "emotions": ["anxiety", "overwhelm"], // AI-detected emotions
    "confidence": 0.85,                   // AI confidence in analysis
    "reasoning": "User expressed explicit stress with strong emotional language..."
  },
  "recommendation": {
    "type": "grounding_technique",
    "name": "5-4-3-2-1 Grounding Exercise",
    "steps": ["Notice 5 things you can see", "Notice 4 things you can touch", ...]
  },
  "message": "I understand you're feeling overwhelmed. Based on our previous conversations, let's try a grounding technique...",
  "crisis_score": 0.3,
  "confidence": 0.85
}
```

**⚠️ API Quota Exceeded Response (Honest Error Handling):**
```json
{
  "agent": "resilience_coach", 
  "status": "success",
  "analysis": {
    "sentiment": "error_quota_exceeded",   // Honest about API status
    "stress_level": "api_unavailable",     // Clear error indication
    "emotions": ["api_quota_exceeded"],    // Explicit error state
    "confidence": 0.0,                     // No fake confidence
    "reasoning": "❌ Gemini API quota exceeded. Please try again later or upgrade API plan."
  },
  "recommendation": {
    "type": "api_quota_exceeded",
    "name": "API Service Error",
    "steps": ["❌ AI recommendations unavailable - API quota exceeded", "Please try again later or upgrade your API plan"]
  },
  "message": "❌ AI Support Unavailable: Gemini API quota exceeded. Please try again later or upgrade your API plan.",
  "crisis_score": 0.5,
  "confidence": 0.0
}
```
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
