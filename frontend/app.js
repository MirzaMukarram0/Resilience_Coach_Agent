// API Configuration
const API_URL = 'http://localhost:5000';

// DOM Elements
const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

// Event Listeners
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send message to agent
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Disable input while processing
    userInput.disabled = true;
    sendBtn.disabled = true;
    
    // Display user message
    addMessage(message, 'user');
    userInput.value = '';
    
    // Show loading indicator
    const loadingId = addLoadingMessage();
    
    try {
        const response = await fetch(`${API_URL}/resilience`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                agent: 'resilience_coach',
                input_text: message,
                metadata: {
                    user_id: 'web_user',
                    language: 'en'
                }
            })
        });
        
        const data = await response.json();
        
        // Remove loading indicator
        removeLoadingMessage(loadingId);
        
        if (data.status === 'success') {
            addAgentResponse(data);
        } else {
            addMessage(`Error: ${data.message}`, 'agent');
        }
        
    } catch (error) {
        removeLoadingMessage(loadingId);
        addMessage(`Connection error: ${error.message}. Make sure the backend server is running.`, 'agent');
    }
    
    // Re-enable input
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
}

// Add user or simple agent message
function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.textContent = text;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add formatted agent response
function addAgentResponse(data) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent-message';
    
    // Analysis section
    if (data.analysis) {
        const analysisDiv = document.createElement('div');
        analysisDiv.className = 'analysis';
        analysisDiv.innerHTML = `
            <strong>📊 Analysis:</strong><br>
            Sentiment: ${data.analysis.sentiment}<br>
            Stress Level: ${data.analysis.stress_level}<br>
            Emotions: ${data.analysis.emotions.join(', ')}
        `;
        messageDiv.appendChild(analysisDiv);
    }
    
    // Supportive message
    if (data.message) {
        const supportDiv = document.createElement('p');
        supportDiv.textContent = data.message;
        supportDiv.style.margin = '10px 0';
        messageDiv.appendChild(supportDiv);
    }
    
    // Recommendation section
    if (data.recommendation) {
        const recDiv = document.createElement('div');
        recDiv.className = 'recommendation';
        
        let stepsHtml = '<ol>';
        data.recommendation.steps.forEach(step => {
            stepsHtml += `<li>${step}</li>`;
        });
        stepsHtml += '</ol>';
        
        recDiv.innerHTML = `
            <h4>💡 Recommended: ${data.recommendation.type.replace(/_/g, ' ')}</h4>
            ${stepsHtml}
        `;
        messageDiv.appendChild(recDiv);
    }
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Add loading indicator
function addLoadingMessage() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message agent-message';
    loadingDiv.id = 'loading-' + Date.now();
    loadingDiv.innerHTML = '<div class="loading"></div> Analyzing...';
    chatContainer.appendChild(loadingDiv);
    scrollToBottom();
    return loadingDiv.id;
}

// Remove loading indicator
function removeLoadingMessage(id) {
    const loadingDiv = document.getElementById(id);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Check backend health on load
async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();
        console.log('Backend status:', data);
    } catch (error) {
        console.error('Backend connection failed:', error);
        addMessage('⚠️ Warning: Cannot connect to backend server. Please ensure it is running on port 5000.', 'agent');
    }
}

// Initialize
checkHealth();
