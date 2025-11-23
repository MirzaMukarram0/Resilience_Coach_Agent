// Use relative URL for API calls (same domain in production)
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000' 
    : '';

let isProcessing = false;
let healthCheckInterval = null;

// Initialize app
window.addEventListener('DOMContentLoaded', () => {
    updateStatus('connecting', 'Connecting...');
    
    // Try initial connection with retry
    setTimeout(() => {
        checkHealth();
        healthCheckInterval = setInterval(checkHealth, 30000); // Check every 30 seconds
    }, 1000);
    
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
    fetch(`${API_URL}/health`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        }
    })
        .then(response => {
            console.log('Health check response:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Backend connected:', data);
            updateStatus('connected', 'Connected');
        })
        .catch(error => {
            console.error('Health check failed:', error);
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
    
    console.log('Sending message:', message);
    
    // Call API
    fetch(`${API_URL}/resilience`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
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
        console.log('Response status:', response.status);
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(`HTTP ${response.status}: ${text}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.status === 'success') {
            displayAgentResponse(data);
        } else {
            throw new Error(data.message || 'Request failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        displayErrorMessage(error.message);
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
        // Check for crisis keywords
        const isCrisis = data.message.includes('crisis') || 
                        data.message.includes('Suicide Prevention') || 
                        data.message.includes('988') ||
                        data.message.includes('1-800-273-8255');
        
        if (isCrisis) {
            // Create crisis alert box
            const crisisDiv = document.createElement('div');
            crisisDiv.className = 'crisis-alert';
            
            const crisisTitle = document.createElement('h4');
            crisisTitle.textContent = '🚨 Crisis Support Available';
            crisisDiv.appendChild(crisisTitle);
            
            const crisisText = document.createElement('p');
            crisisText.textContent = data.message;
            crisisDiv.appendChild(crisisText);
            
            // Add hotline info prominently
            const hotlineDiv = document.createElement('div');
            hotlineDiv.className = 'crisis-hotline';
            hotlineDiv.innerHTML = '📞 <strong>Emergency Helplines:</strong><br>988 (Suicide & Crisis Lifeline)<br>1-800-273-8255 (24/7 Support)';
            crisisDiv.appendChild(hotlineDiv);
            
            contentDiv.appendChild(crisisDiv);
        } else {
            const messageText = document.createElement('p');
            messageText.textContent = data.message;
            messageText.style.marginBottom = '12px';
            contentDiv.appendChild(messageText);
        }
    }
    
    // Check for crisis in message for analysis styling
    const isCrisis = data.message && (data.message.includes('crisis') || data.message.includes('Suicide Prevention') || data.message.includes('988'));
    
    // Analysis section
    if (data.analysis) {
        const analysisDiv = document.createElement('div');
        const sentiment = data.analysis.sentiment || 'neutral';
        analysisDiv.className = `analysis-section ${sentiment}`;
        
        if (isCrisis) {
            analysisDiv.className = 'analysis-section crisis';
        }
        
        const title = document.createElement('h4');
        title.textContent = isCrisis ? '⚠️ Crisis Detected' : 'Emotional Analysis';
        analysisDiv.appendChild(title);
        
        const content = document.createElement('div');
        content.className = 'analysis-content';
        
        // Sentiment with badge
        const sentimentP = document.createElement('p');
        sentimentP.innerHTML = `<strong>Sentiment:</strong><span class="sentiment-badge ${sentiment}">${capitalizeFirst(sentiment)}</span>`;
        content.appendChild(sentimentP);
        
        // Stress level with indicator
        const stressLevel = data.analysis.stress_level || 'medium';
        const stressP = document.createElement('div');
        stressP.className = 'stress-indicator';
        stressP.innerHTML = `<strong>Stress Level:</strong><span class="stress-level ${stressLevel}">${capitalizeFirst(stressLevel)}</span>`;
        content.appendChild(stressP);
        
        // Emotions as tags
        if (data.analysis.emotions && data.analysis.emotions.length > 0) {
            const emotionsLabel = document.createElement('p');
            emotionsLabel.innerHTML = '<strong>Detected Emotions:</strong>';
            emotionsLabel.style.marginTop = '8px';
            emotionsLabel.style.marginBottom = '4px';
            content.appendChild(emotionsLabel);
            
            const emotionsList = document.createElement('div');
            emotionsList.className = 'emotions-list';
            data.analysis.emotions.forEach(emotion => {
                const tag = document.createElement('span');
                tag.className = 'emotion-tag';
                tag.textContent = capitalizeFirst(emotion);
                emotionsList.appendChild(tag);
            });
            content.appendChild(emotionsList);
        }
        
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

function displayErrorMessage(errorDetails) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    let errorMsg = 'I apologize, but I encountered an issue processing your request. Please try again in a moment.';
    if (errorDetails) {
        console.error('Error details:', errorDetails);
    }
    
    contentDiv.textContent = errorMsg;
    
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
