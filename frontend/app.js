const API_URL = 'http://localhost:5000';

let isProcessing = false;
let healthCheckInterval = null;

// Initialize app
window.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    healthCheckInterval = setInterval(checkHealth, 30000); // Check every 30 seconds
    
    const userInput = document.getElementById('userInput');
    userInput.addEventListener('input', updateCharCount);
    userInput.addEventListener('input', toggleSendButton);
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!this.value.trim() || isProcessing) return;
            sendMessage();
        }
    });
});

// Health check
function checkHealth() {
    fetch(`${API_URL}/health`)
        .then(response => response.json())
        .then(data => {
            updateStatus('connected', 'Connected');
        })
        .catch(error => {
            updateStatus('error', 'Disconnected');
        });
}

function updateStatus(status, text) {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    statusDot.className = `status-dot ${status}`;
    statusText.textContent = text;
}

function updateCharCount() {
    const input = document.getElementById('userInput');
    const charCount = document.getElementById('charCount');
    charCount.textContent = `${input.value.length} / 2000`;
}

function toggleSendButton() {
    const input = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const message = input.value.trim();
    
    sendButton.disabled = message.length < 3 || isProcessing;
}

function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (message.length < 3 || isProcessing) return;
    
    isProcessing = true;
    const sendButton = document.getElementById('sendButton');
    const buttonText = document.getElementById('buttonText');
    
    sendButton.disabled = true;
    buttonText.innerHTML = '<span class="loading-spinner"></span>';
    
    // Display user message
    displayMessage(message, 'user');
    input.value = '';
    updateCharCount();
    
    // Call API
    fetch(`${API_URL}/resilience`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            agent: 'resilience_coach',
            input_text: message,
            metadata: {
                user_id: 'web_user_' + Date.now(),
                language: 'en'
            }
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            displayAgentResponse(data);
        } else {
            throw new Error(data.message || 'Request failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        displayErrorMessage();
    })
    .finally(() => {
        isProcessing = false;
        sendButton.disabled = false;
        buttonText.textContent = 'Send Message';
        toggleSendButton();
    });
}

function displayMessage(text, sender) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function displayAgentResponse(data) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Main message
    if (data.message) {
        const messageText = document.createElement('p');
        messageText.textContent = data.message;
        messageText.style.marginBottom = '12px';
        contentDiv.appendChild(messageText);
    }
    
    // Analysis section
    if (data.analysis) {
        const analysisDiv = document.createElement('div');
        analysisDiv.className = 'analysis-section';
        
        const title = document.createElement('h4');
        title.textContent = 'Emotional Analysis';
        analysisDiv.appendChild(title);
        
        const content = document.createElement('div');
        content.className = 'analysis-content';
        content.innerHTML = `
            <p><strong>Sentiment:</strong> ${capitalizeFirst(data.analysis.sentiment || 'N/A')}</p>
            <p><strong>Stress Level:</strong> ${capitalizeFirst(data.analysis.stress_level || 'N/A')}</p>
            ${data.analysis.emotions && data.analysis.emotions.length > 0 ? 
                `<p><strong>Emotions:</strong> ${data.analysis.emotions.map(capitalizeFirst).join(', ')}</p>` : ''}
        `;
        analysisDiv.appendChild(content);
        contentDiv.appendChild(analysisDiv);
    }
    
    // Recommendation section
    if (data.recommendation) {
        const recDiv = document.createElement('div');
        recDiv.className = 'recommendation-section';
        
        const title = document.createElement('h4');
        title.textContent = 'Recommended Strategy';
        recDiv.appendChild(title);
        
        const content = document.createElement('div');
        content.className = 'recommendation-content';
        
        const typeName = formatRecommendationType(data.recommendation.type);
        const typeP = document.createElement('p');
        typeP.innerHTML = `<strong>${typeName}</strong>`;
        content.appendChild(typeP);
        
        if (data.recommendation.steps && data.recommendation.steps.length > 0) {
            const stepsList = document.createElement('ol');
            stepsList.className = 'recommendation-steps';
            data.recommendation.steps.forEach(step => {
                const li = document.createElement('li');
                li.textContent = step;
                stepsList.appendChild(li);
            });
            content.appendChild(stepsList);
        }
        
        recDiv.appendChild(content);
        contentDiv.appendChild(recDiv);
    }
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function displayErrorMessage() {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = 'I apologize, but I encountered an issue processing your request. Please try again in a moment.';
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

function scrollToBottom() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

function formatRecommendationType(type) {
    if (!type) return 'General Support';
    return type.split('_').map(capitalizeFirst).join(' ');
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (healthCheckInterval) {
        clearInterval(healthCheckInterval);
    }
});

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
