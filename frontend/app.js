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
        // Check health every 5 minutes to keep service alive
        healthCheckInterval = setInterval(checkHealth, 5 * 60 * 1000);
        
        // Wake up service on first page load
        wakeUpService();
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

// Wake up service after sleep (Render free tier goes to sleep after 15 min)
function wakeUpService() {
    console.log('Waking up service and reconnecting Gemini API...');
    updateStatus('connecting', 'Waking up...');
    
    // Hit health endpoint to trigger reconnection
    fetch(`${API_URL}/health`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log('Service wake-up response:', data);
            if (data.gemini_connected) {
                updateStatus('connected', 'Connected');
            } else {
                updateStatus('error', 'API Issue');
            }
        })
        .catch(error => {
            console.error('Wake-up failed:', error);
            updateStatus('error', 'Disconnected');
        });
}

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
            if (data.gemini_connected) {
                updateStatus('connected', 'Connected');
            } else {
                updateStatus('error', 'API Issue');
            }
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

function sendMessage(retryCount = 0) {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (message.length < 3 || isProcessing) return;
    
    isProcessing = true;
    const sendButton = document.getElementById('sendButton');
    const buttonText = document.getElementById('buttonText');
    
    sendButton.disabled = true;
    buttonText.innerHTML = '<span class="loading-spinner"></span>';
    
    // Display user message (only on first attempt)
    if (retryCount === 0) {
        displayMessage(message, 'user');
        input.value = '';
        updateCharCount();
    }
    
    console.log('Sending message:', message, 'Attempt:', retryCount + 1);
    
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
            // Reset UI on success
            isProcessing = false;
            sendButton.disabled = false;
            buttonText.textContent = 'Send Message';
            toggleSendButton();
        } else {
            throw new Error(data.message || 'Request failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        
        // Retry logic: If first request fails (likely stale connection), wake up and retry
        if (retryCount < 1) {
            console.log('Request failed, waking up service and retrying...');
            buttonText.innerHTML = '<span class="loading-spinner"></span> Reconnecting...';
            
            // Wake up service and retry after 2 seconds
            wakeUpService();
            setTimeout(() => {
                sendMessage(retryCount + 1);
            }, 2000);
        } else {
            // After retry, show error
            displayErrorMessage(error.message);
            isProcessing = false;
            sendButton.disabled = false;
            buttonText.textContent = 'Send Message';
            toggleSendButton();
        }
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
    const isApiError = data.analysis && (data.analysis.sentiment?.includes('error_') || data.analysis.stress_level === 'api_unavailable');
    
    // Analysis section
    if (data.analysis) {
        const analysisDiv = document.createElement('div');
        const sentiment = data.analysis.sentiment || 'neutral';
        analysisDiv.className = `analysis-section ${sentiment}`;
        
        if (isCrisis) {
            analysisDiv.className = 'analysis-section crisis';
        } else if (isApiError) {
            analysisDiv.className = 'analysis-section api-error';
        }
        
        const title = document.createElement('h4');
        title.textContent = isCrisis ? '⚠️ Crisis Detected' : (isApiError ? '⚠️ AI Service Status' : 'Emotional Analysis');
        analysisDiv.appendChild(title);
        
        const content = document.createElement('div');
        content.className = 'analysis-content';
        
        // Sentiment with badge
        const sentimentP = document.createElement('p');
        const sentimentDisplay = isApiError ? 'API Error' : capitalizeFirst(sentiment.replace('error_', '').replace('_', ' '));
        sentimentP.innerHTML = `<strong>Sentiment:</strong><span class="sentiment-badge ${sentiment}">${sentimentDisplay}</span>`;
        content.appendChild(sentimentP);
        
        // Stress level with indicator
        const stressLevel = data.analysis.stress_level || 'medium';
        const stressP = document.createElement('div');
        stressP.className = 'stress-indicator';
        const stressDisplay = isApiError ? 'API Unavailable' : capitalizeFirst(stressLevel.replace('_', ' '));
        stressP.innerHTML = `<strong>Stress Level:</strong><span class="stress-level ${stressLevel}">${stressDisplay}</span>`;
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
