# Resilience Coach Agent  
### Semester Project – AI Agent System (Supervisor–Worker Architecture)  
### Complete Technical & Functional Documentation  

---

## 1. Project Overview  
The **Resilience Coach Agent** is an AI-driven mental-wellness support system designed to help users manage stress, build emotional resilience, and receive personalized coping strategies. The agent operates within a **Supervisor–Worker (Registry) architecture**, where it functions as an independent worker agent callable via a structured JSON contract.

This Markdown file describes the full product scope, features, architecture, design decisions, tech stack, JSON handshake, and the integration approach using **Flask + LangGraph + Gemini API**.

---

## 2. Project Justification  
The increasing demand for scalable mental-wellness tools motivates the development of an AI agent capable of emotional support without requiring human intervention. Users increasingly seek **accessible, confidential, immediate, and empathetic digital mental-wellness assistance**.  
The Resilience Coach Agent fulfills this need by combining:

- **NLP-Powered Emotional Understanding**  
- **Stress-Level Detection**  
- **Personalized Coping Recommendations**  
- **Conversational Empathy**  
- **Secure and Ethical Data Handling**

This system enhances personal resilience through real-time AI feedback and adaptive guidance.

---

## 3. Product Characteristics / Features  

### **Core Features**
- **AI-Powered NLP Engine**  
  Detects emotional tone, stress cues, sentiment, and intent using Gemini LLM.

- **Personalized Coping Recommendations**  
  Provides breathing exercises, grounding techniques, mindfulness tasks, and motivational affirmations.

- **Conversational Interface**  
  Empathetic communication designed to mimic supportive counseling interactions.

- **Data Privacy & Ethics**  
  No personal identifiers stored; anonymized logs only.

- **Basic Analytics Summary**  
  Tracks improvement trends from input mood logs (non-personalized, anonymized).

---

## 4. Deliverables  

### **Included in Final Submission**
1. **Functional AI Agent**  
   Fully deployed Flask API + LangGraph agent powered by Gemini.

2. **Frontend UI (HTML/CSS)**  
   Simple text-box UI to communicate with the agent.

3. **Recommendation Engine**  
   Rules + Gemini reasoning for wellness tasks.

4. **User Onboarding (Simple)**  
   First-time usage explanation with guidelines.

5. **Complete Technical Documentation**  
   Architecture, code explanation, workflows, JSON contracts.

6. **Integration Test**  
   Script showing interaction between Supervisor and this agent.

7. **Evaluation Report**  
   Improvements summary + constraints.

---

## 5. Assumptions  
- Gemini API access available (Free Tier sufficient).  
- Flask, LangGraph, and Python environment configured.  
- Supervisor Agent and Registry will be provided by the course section.  
- Users are desktop browser users (no mobile app required).  
- No need to train custom ML models—Reliance on Gemini is acceptable and intended.

---

## 6. Constraints  
- **Time:** Project deadline is Dec 12, 2025  
- **Resources:** Limited compute—LLM training not allowed  
- **Ethics:** Must comply with privacy & fairness principles  
- **Budget:** Free services only (Gemini Free Tier)  
- **Technical:** API must follow JSON handshake rules  

---

## 7. Agent Description (System-Level Perspective)  

### **Functional Flow**
1. User sends text describing their feelings or current state.  
2. Agent analyzes emotional tone.  
3. Agent detects stress indicators.  
4. Agent generates personalized coping recommendations.  
5. Agent returns structured JSON with analysis, suggestions, and supportive message.

### **Input Type**
- Plain user message (text only)

### **Processing**
- Sentiment classification  
- Emotion estimation  
- Stress inference  
- Recommendation generation  

### **Outputs**
- Emotion & stress analysis  
- Suggested coping strategy  
- Motivational feedback  

### **Technical Characteristics**
- **Backend:** Python (Flask)  
- **NLP/AI:** Gemini LLM (API-based)  
- **Orchestration:** LangGraph  
- **Database:** None (stateless), only optional text logs  
- **Integration:** REST API for Supervisor connectivity

### **Goal**
Provide scalable, accessible emotional support to assist users in resilience-building.

---

## 8. Scope & Boundaries  

### **In Scope**
- Emotional tone analysis  
- Personalized well-being recommendations  
- JSON-based interaction  
- API-based deployment  
- HTML/CSS simple UI  
- Integration with Supervisor/Registry  

### **Out of Scope**
- Mobile app  
- User authentication system  
- Long-term personalized profiles  
- Custom model training  
- Medical diagnosis or clinical recommendations  

---

## 9. Acceptance Criteria  

| Requirement | Target |
|------------|--------|
| Model accuracy (sentiment/emotion) | ≥ 70–80% (Gemini accuracy level) |
| JSON contract compliance | 100% |
| Supervisor integration | Must pass health check + external call |
| UI clarity | 90% user satisfaction |
| Stability | No crashes in 50+ test calls |

---

## 10. Why We Use Gemini Instead of Training a Model  
Training an NLP model requires:

- Large datasets  
- GPU power  
- Weeks of training  
- Ethical review of mental-health datasets  

Given project constraints, it is **not feasible**.

### Using Gemini Provides:
- High emotional reasoning ability  
- Accurate sentiment + tone recognition  
- Context awareness  
- No training required  
- Free usage tier  
- Rapid prototyping  
- Industry-aligned deployment practices  

Thus, the Resilience Coach Agent is **powered entirely by Gemini**, with no self-trained ML models.

---

## 11. System Architecture  

### **High-Level Workflow**
User → Frontend → Supervisor → Resilience Agent → Gemini → Agent Response → Supervisor → User


### **Internal Agent Architecture**


┌─────────────────────────┐
│ Flask API │
│ - /resilience │
│ - /health │
└───────────────┬────────┘
│
LangGraph Workflow
│
┌────────────┼────────────┐
│ │ │
Parse Input Gemini NLP Recommendation Engine
│ │ │
└────────────┴────────────┘
│
JSON Output Formatter


---

## 12. JSON Handshake (Contract)

### **Request Format**
```json
{
  "agent": "resilience_coach",
  "input_text": "I am feeling overwhelmed and anxious",
  "metadata": {
    "user_id": "abc123",
    "language": "en"
  }
}

Response Format
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
    "steps": ["Inhale deeply 4 seconds", "Hold 2 seconds", "Exhale 6 seconds"]
  },
  "message": "You're doing the best you can. Let's take this one step at a time."
}

Health Check
{
  "status": "ok",
  "message": "Resilience Coach Agent is running."
}

13. Project Folder Structure
resilience_agent/
│
├── app.py                  # Flask App
├── agent/
│   ├── graph.py            # LangGraph workflow
│   ├── logic.py            # Recommendation rules
│   └── gemini_client.py    # Gemini Wrapper
│
├── static/
│   ├── index.html          # UI
│   └── styles.css
│
├── registry.json           # Agent entry for supervisor
├── tests/
│   └── integration_test.py
│
├── README.md
└── requirements.txt

14. Logging & Monitoring

The agent implements:

Console logging

Error tracking

Health check endpoint

Status reporting

Logs contain no personal data.

15. Integration Test (Expected Behaviour)

Supervisor sends:

{"agent": "resilience_coach", "input_text": "I'm feeling stressed today"}


Expected return:

Correct JSON

Valid analysis

Recommendation

No crash

Logged interaction

Integration must prove agent can be called from external script.

16. Conclusion

The Resilience Coach Agent is a fully functional AI agent designed for mental-wellbeing support, built under real-world engineering constraints. It avoids custom NLP model training and instead relies on Gemini API, ensuring accuracy, ethical compliance, and fast delivery.

It meets all course requirements:

JSON handshake

Flask API

LangGraph orchestration

Frontend

Supervisor compatibility

Health check

Integration test

This document serves as the complete specification and technical description for the project.