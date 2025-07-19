console.log("Web interface loading...");

// ===== GLOBAL VARIABLES =====
let isLoading = false;
let systemStatus = {
    system_ready: false,
    vector_db_ready: false,
    document_count: 0,
    chat_history_count: 0
};
let recentQuestions = [];

// ===== DOM ELEMENTS =====
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const loadingOverlay = document.getElementById('loadingOverlay');
const statusIndicator = document.getElementById('statusIndicator');
const systemStatusEl = document.getElementById('systemStatus');
const recentQueriesEl = document.getElementById('recentQueries');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
const refreshStatusBtn = document.getElementById('refreshStatusBtn');

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('AMIF Grant Assistant Web Interface starting...');
    
    setupEventListeners();
    checkSystemStatus();
    loadChatHistory();
    
    // Show startup message
    setTimeout(() => {
        updateStatusIndicator('ready', 'System Ready');
    }, 1000);
});

// ===== EVENT LISTENERS =====
function setupEventListeners() {
    // Message sending
    sendBtn.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // Örnek soruları tıklayabilir yap
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('example-item')) {
            const question = e.target.getAttribute('data-question');
            messageInput.value = question;
            messageInput.focus();
        }
    });
    
    // Kontrol butonları
    clearHistoryBtn.addEventListener('click', clearChatHistory);
    refreshStatusBtn.addEventListener('click', checkSystemStatus);
}

// ===== MESSAGE HANDLING =====
async function handleSendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isLoading) {
        return;
    }
    
    if (!systemStatus.system_ready) {
        alert('System is not ready yet. Please wait...');
        return;
    }
    
    // Update UI
    addMessageToChat('user', message);
    messageInput.value = '';
    setLoading(true);
    
    // Memory event - mesaj gönderildi
    onMessageSent();
    
    // Typing indicator göster
    showTypingIndicator();
    
    // Hoşgeldin mesajını gizle
    hideWelcomeMessage();
    
    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: message })
        });
        
        const data = await response.json();
        
        // Typing indicator'ı gizle
        hideTypingIndicator();
        
        if (data.success) {
            addMessageToChat('assistant', data.response, data.source_details || data.sources, data.timestamp);
            
            // Add to recent questions
            addToRecentQuestions(message);
            
            // Memory event - yanıt alındı
            onMessageReceived();
            
            checkSystemStatus();
        } else {
            addMessageToChat('assistant', 'Error: ' + data.error, [], null);
            alert('An error occurred while processing the query.');
        }
        
    } catch (error) {
        console.error('API Error:', error);
        
        // Typing indicator'ı gizle (hata durumunda)
        hideTypingIndicator();
        
        addMessageToChat('assistant', 'Connection error. Please try again.', [], null);
        alert('Cannot connect to server.');
    } finally {
        setLoading(false);
    }
}

// ===== CHAT UI FUNCTIONS =====
function addMessageToChat(type, content, sources, timestamp) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-' + type;
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    messageText.textContent = content;
    
    messageContent.appendChild(messageText);
    
            // Sources ekle (sadece assistant mesajları için)
        if (type === 'assistant' && sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            
            const sourcesTitle = document.createElement('h4');
            sourcesTitle.textContent = 'Sources';
        sourcesDiv.appendChild(sourcesTitle);
        
        const sourcesGrid = document.createElement('div');
        sourcesGrid.className = 'sources-grid';
        
        sources.forEach((source, index) => {
            const sourceCard = document.createElement('div');
            sourceCard.className = 'source-card';
            
            // Minimal kaynak gösterimi
            let sourceName = '';
            let pageInfo = '';
            
            if (typeof source === 'object' && source.source) {
                sourceName = source.source;
                pageInfo = source.page || '';
            } else {
                sourceName = typeof source === 'string' ? source : source.source || source;
                pageInfo = source.page || '';
            }
            
            sourceCard.innerHTML = `
                <span class="source-number">${index + 1}.</span>
                <span class="source-title">${sourceName}</span>
                <span class="source-page">${pageInfo}</span>
            `;
            
            sourcesGrid.appendChild(sourceCard);
        });
        
        sourcesDiv.appendChild(sourcesGrid);
        messageContent.appendChild(sourcesDiv);
    }
    
    // Timestamp ekle
    if (timestamp) {
        const timestampDiv = document.createElement('div');
        timestampDiv.className = 'message-timestamp';
        const date = new Date(timestamp);
        timestampDiv.textContent = date.toLocaleTimeString('en-US');
        messageContent.appendChild(timestampDiv);
    }
    
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideWelcomeMessage() {
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.style.display = 'none';
    }
}

// ===== TYPING INDICATOR =====
function showTypingIndicator() {
    // Mevcut typing indicator'ı kaldır
    hideTypingIndicator();
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message message-assistant typing-message';
    typingDiv.id = 'typingIndicator';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    
    typingIndicator.innerHTML = `
        <span class="typing-text">AMIF Grant Assistant yazıyor</span>
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    messageContent.appendChild(typingIndicator);
    typingDiv.appendChild(messageContent);
    chatMessages.appendChild(typingDiv);
    
    // Animasyon için class ekle
    setTimeout(() => {
        typingIndicator.classList.add('show');
    }, 50);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        // Fade out animasyonu
        const indicator = typingIndicator.querySelector('.typing-indicator');
        if (indicator) {
            indicator.style.opacity = '0';
            indicator.style.transform = 'translateY(-10px)';
        }
        
        // Kısa bir delay sonra kaldır
        setTimeout(() => {
            typingIndicator.remove();
        }, 200);
    }
}

// ===== SYSTEM STATUS =====
async function checkSystemStatus() {
    try {
        updateStatusIndicator('loading', 'Checking status...');
        
        const response = await fetch('/status');
        const data = await response.json();
        
        // Flask endpoint'inden gelen veriyi JavaScript formatına çevir
        systemStatus = {
            system_ready: data.database_connected,
            vector_db_ready: data.database_connected,
            document_count: data.database_info?.document_count || 0,
            chat_history_count: 0
        };
        
        updateSystemStatusUI();
        
        if (systemStatus.system_ready) {
            updateStatusIndicator('ready', 'System Ready');
        } else {
            updateStatusIndicator('error', 'System Not Ready');
        }
        
    } catch (error) {
        console.error('Status check error:', error);
        updateStatusIndicator('error', 'Connection Error');
        alert('Cannot connect to server.');
    }
}

function updateSystemStatusUI() {
    const statusItems = systemStatusEl.querySelectorAll('.status-item');
    
    // System status
    updateStatusItem(statusItems[0], 
        systemStatus.system_ready ? 'Ready' : 'Not Ready',
        systemStatus.system_ready ? 'ready' : 'error'
    );
    
    // Database status
    updateStatusItem(statusItems[1],
        systemStatus.vector_db_ready ? 'Connected' : 'Disconnected',
        systemStatus.vector_db_ready ? 'ready' : 'error'
    );
    
    // Document count
    updateStatusItem(statusItems[2],
        systemStatus.document_count.toLocaleString('en-US'),
        systemStatus.document_count > 0 ? 'ready' : 'error'
    );
    
    // History count
    updateStatusItem(statusItems[3],
        systemStatus.chat_history_count.toString(),
        'ready'
    );
}

function updateStatusItem(element, value, status) {
    const valueEl = element.querySelector('.status-value');
    valueEl.textContent = value;
    
    // Clear classes and add new one
    element.classList.remove('loading', 'ready', 'error');
    element.classList.add(status);
}

function updateStatusIndicator(status, text) {
    const statusDot = statusIndicator.querySelector('.status-dot');
    const statusText = statusIndicator.querySelector('.status-text');
    
    statusDot.classList.remove('ready', 'error');
    statusText.textContent = text;
    
    if (status === 'ready') {
        statusDot.classList.add('ready');
    } else if (status === 'error') {
        statusDot.classList.add('error');
    }
}

// ===== CHAT HISTORY =====
async function loadChatHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        if (data.success && data.history.length > 0) {
            hideWelcomeMessage();
            
            data.history.forEach(entry => {
                addMessageToChat('user', entry.query);
                addMessageToChat('assistant', entry.response, entry.sources, entry.timestamp);
                conversationMessageCount += 2; // User + assistant for each entry
            });
            
            updateMemorySessionDisplay();
        }
        
    } catch (error) {
        console.error('History loading error:', error);
    }
}

async function clearChatHistory() {
    if (!confirm('Are you sure you want to clear all chat history?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/clear-history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            location.reload();
        } else {
            showNotification('Error occurred while clearing history.', 'error');
        }
        
    } catch (error) {
        console.error('History clearing error:', error);
        showNotification('Cannot connect to server.', 'error');
    }
}

// ===== UTILITY FUNCTIONS =====
function setLoading(loading) {
    isLoading = loading;
    
    if (loading) {
        sendBtn.disabled = true;
        messageInput.disabled = true;
        sendBtn.textContent = 'Sending...';
    } else {
        sendBtn.disabled = false;
        messageInput.disabled = false;
        sendBtn.textContent = 'Send';
        messageInput.focus();
    }
}

function showNotification(message, type) {
    console.log('[' + type.toUpperCase() + '] ' + message);
}

// ===== MEMORY PANEL =====
let currentSessionId = null;
let conversationMessageCount = 0;

function initializeMemoryPanel() {
    // Initialize memory panel
    updateMemoryPanel();
    
    // Get session ID from cookie
    currentSessionId = getCookie('session_id');
    if (!currentSessionId) {
        // Create new session
        currentSessionId = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        setCookie('session_id', currentSessionId, 1); // 1 day
    }
    
    updateMemorySessionDisplay();
}

function updateMemoryPanel() {
    const memoryIndicator = document.getElementById('memoryIndicator');
    const memoryActivity = document.getElementById('memoryActivity');
    
    if (memoryIndicator) {
        const memoryDot = memoryIndicator.querySelector('.memory-dot');
        const memoryText = memoryIndicator.querySelector('.memory-text');
        
        memoryDot.classList.add('active');
        memoryText.textContent = 'Memory Active';
    }
    
    if (memoryActivity) {
        const activityText = memoryActivity.querySelector('.activity-text');
        activityText.textContent = 'Ready';
        memoryActivity.className = 'memory-activity';
    }
}

function updateMemorySessionDisplay() {
    const sessionIdEl = document.getElementById('currentSessionId');
    const conversationCountEl = document.getElementById('conversationCount');
    
    if (sessionIdEl && currentSessionId) {
        // Shorten session ID
        const shortSessionId = currentSessionId.substring(0, 8) + '...';
        sessionIdEl.textContent = shortSessionId;
        sessionIdEl.title = currentSessionId; // Show full session ID as tooltip
    }
    
    if (conversationCountEl) {
        conversationCountEl.textContent = `${conversationMessageCount} messages`;
    }
}

function showMemoryActivity(state, message) {
    const memoryActivity = document.getElementById('memoryActivity');
    const activityText = memoryActivity?.querySelector('.activity-text');
    
    if (!memoryActivity || !activityText) return;
    
    // Change activity state
    memoryActivity.className = `memory-activity ${state}`;
    activityText.textContent = message;
    
    // Return to normal state after a certain time
    setTimeout(() => {
        memoryActivity.className = 'memory-activity';
        activityText.textContent = 'Ready';
    }, 3000);
}

function onMessageSent() {
    conversationMessageCount++;
    updateMemorySessionDisplay();
    showMemoryActivity('thinking', 'Processing question...');
}

function onMessageReceived() {
    conversationMessageCount++;
    updateMemorySessionDisplay();
    showMemoryActivity('saving', 'Updating memory...');
}

// Cookie helper functions
function setCookie(name, value, days) {
    const expires = new Date();
    expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${name}=${value}; expires=${expires.toUTCString()}; path=/`;
}

function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

// ===== RECENT QUESTIONS MANAGEMENT =====
function addToRecentQuestions(question) {
    // Prevent duplicate questions
    if (recentQuestions.includes(question)) {
        return;
    }
    
    // Add to beginning (newest on top)
    recentQuestions.unshift(question);
    
    // Keep maximum 5 questions
    if (recentQuestions.length > 5) {
        recentQuestions = recentQuestions.slice(0, 5);
    }
    
    updateRecentQuestionsUI();
    saveRecentQuestions();
}

function updateRecentQuestionsUI() {
    if (!recentQueriesEl) return;
    
    if (recentQuestions.length === 0) {
        recentQueriesEl.innerHTML = '<div class="no-queries">No questions asked yet.</div>';
        return;
    }
    
    let html = '';
    recentQuestions.forEach((question, index) => {
        // Shorten question (50 characters max)
        const shortQuestion = question.length > 50 
            ? question.substring(0, 47) + '...' 
            : question;
            
        html += `
            <div class="recent-question-item" data-question="${question}" title="${question}">
                <span class="question-text">${shortQuestion}</span>
            </div>
        `;
    });
    
    recentQueriesEl.innerHTML = html;
    
    // Add click events
    recentQueriesEl.querySelectorAll('.recent-question-item').forEach(item => {
        item.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            messageInput.value = question;
            messageInput.focus();
        });
    });
}

function loadRecentQuestions() {
    const saved = localStorage.getItem('recentQuestions');
    if (saved) {
        try {
            recentQuestions = JSON.parse(saved);
            updateRecentQuestionsUI();
        } catch (e) {
            console.error('Recent questions yükleme hatası:', e);
            recentQuestions = [];
        }
    }
}

function saveRecentQuestions() {
    try {
        localStorage.setItem('recentQuestions', JSON.stringify(recentQuestions));
    } catch (e) {
        console.error('Recent questions kaydetme hatası:', e);
    }
}

function clearRecentQuestions() {
    recentQuestions = [];
    updateRecentQuestionsUI();
    localStorage.removeItem('recentQuestions');
}

// Initialize memory panel
initializeMemoryPanel();

    // Load recent questions
loadRecentQuestions();

// Auto-refresh status
setInterval(checkSystemStatus, 30000);

console.log('✅ AMIF Grant Assistant Web Interface loaded!');
 