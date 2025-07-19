// DrugBot Web Interface JavaScript

class DrugBotApp {
    constructor() {
        this.isLoading = false;
        this.messageHistory = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.updateActivityStatus('ready');
    }

    setupEventListeners() {
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });

        // Auto-focus input
        messageInput.focus();
    }

    async loadInitialData() {
        try {
            // Load system stats
            await this.loadStats();
            
            // Load recent queries
            await this.loadRecentQueries();
            
        } catch (error) {
            console.error('Başlangıç verisi yüklenemedi:', error);
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            document.getElementById('totalDrugs').textContent = stats.total_drugs;
            document.getElementById('totalDocs').textContent = stats.total_documents;
            document.getElementById('queryCount').textContent = stats.query_count;
            document.getElementById('systemStatus').textContent = stats.status;
            
        } catch (error) {
            console.error('İstatistikler yüklenemedi:', error);
        }
    }

    async loadRecentQueries() {
        try {
            const response = await fetch('/api/recent');
            const queries = await response.json();
            
            const recentQueriesContainer = document.getElementById('recentQueries');
            
            if (queries.length === 0) {
                recentQueriesContainer.innerHTML = '<div class="no-queries">Henüz soru sorulmadı</div>';
                return;
            }
            
            let html = '';
            queries.forEach(query => {
                html += `
                    <div class="recent-question-item" onclick="askQuestion('${query.query}')">
                        <span class="question-text">${query.query}</span>
                    </div>
                `;
            });
            
            recentQueriesContainer.innerHTML = html;
            
        } catch (error) {
            console.error('Son sorgular yüklenemedi:', error);
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || this.isLoading) return;
        
        this.isLoading = true;
        this.updateSendButton(false);
        
        // Add user message to chat
        this.addMessage('user', message);
        
        // Clear input
        messageInput.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Update activity status
        this.updateActivityStatus('thinking');
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Hide typing indicator
                this.hideTypingIndicator();
                
                // Add assistant response
                this.addMessage('assistant', data.response, data.sources);
                
                // Update stats
                await this.loadStats();
                await this.loadRecentQueries();
                
            } else {
                this.hideTypingIndicator();
                this.addMessage('assistant', `❌ Hata: ${data.error}`);
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('assistant', '❌ Bağlantı hatası. Lütfen tekrar deneyin.');
            console.error('Mesaj gönderme hatası:', error);
        }
        
        this.isLoading = false;
        this.updateSendButton(true);
        this.updateActivityStatus('ready');
        
        // Focus back to input
        messageInput.focus();
    }

    addMessage(type, content, sources = []) {
        const chatMessages = document.getElementById('chatMessages');
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        
        // Remove welcome message if exists
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        
        let messageHTML = `
            <div class="message-content">${content}</div>
        `;
        
        // Add sources if available
        if (sources && sources.length > 0) {
            messageHTML += `
                <div class="message-sources">
                    <h4>Kaynaklar:</h4>
                    <div class="sources-grid">
                        ${sources.map((source, index) => `
                            <div class="source-card">
                                <div class="source-number">${index + 1}</div>
                                <div class="source-title">${source.title}</div>
                                <div class="source-page">${source.type}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // Add timestamp
        const timestamp = new Date().toLocaleTimeString('tr-TR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        messageHTML += `<div class="message-timestamp">${timestamp}</div>`;
        
        messageDiv.innerHTML = messageHTML;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typingIndicator';
        
        typingDiv.innerHTML = `
            <div class="typing-text">DrugBot yazıyor</div>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Show with animation
        setTimeout(() => {
            typingDiv.classList.add('show');
        }, 50);
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    updateSendButton(enabled) {
        const sendBtn = document.getElementById('sendBtn');
        sendBtn.disabled = !enabled;
        sendBtn.textContent = enabled ? 'Gönder' : 'Bekleyin...';
    }

    updateActivityStatus(status) {
        const activityPulse = document.getElementById('activityPulse');
        const activityText = document.getElementById('activityText');
        const memoryActivity = activityPulse.parentElement;
        
        // Remove all activity classes
        memoryActivity.classList.remove('thinking', 'processing', 'saving');
        
        switch (status) {
            case 'thinking':
                memoryActivity.classList.add('thinking');
                activityText.textContent = 'Düşünüyor...';
                break;
            case 'processing':
                memoryActivity.classList.add('processing');
                activityText.textContent = 'İşleniyor...';
                break;
            case 'saving':
                memoryActivity.classList.add('saving');
                activityText.textContent = 'Kaydediliyor...';
                break;
            default:
                activityText.textContent = 'Beklemede';
        }
    }

    clearHistory() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <h3>💊 DrugBot'a Hoş Geldiniz!</h3>
                <p>OnSIDES dataset'i ile güçlendirilmiş ilaç bilgi asistanınız</p>
                <p><strong>2,562 ilaç bileşeni</strong> hakkında bilgi alabilirsiniz</p>
                
                <div class="example-questions">
                    <p><strong>Örnek sorular:</strong></p>
                    <div class="example-item" onclick="askExample('aspirin yan etkileri nelerdir?')">
                        🔍 Aspirin yan etkileri nelerdir?
                    </div>
                    <div class="example-item" onclick="askExample('paracetamol aç karınla mı alınır?')">
                        🍽️ Paracetamol aç karınla mı alınır?
                    </div>
                    <div class="example-item" onclick="askExample('ibuprofen ne için kullanılır?')">
                        💊 İbuprofen ne için kullanılır?
                    </div>
                </div>
            </div>
        `;
        
        this.messageHistory = [];
    }

    askQuestion(question) {
        const messageInput = document.getElementById('messageInput');
        messageInput.value = question;
        this.sendMessage();
    }
}

// Global functions for HTML onclick events
function askExample(question) {
    window.drugbot.askQuestion(question);
}

function clearHistory() {
    window.drugbot.clearHistory();
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        window.drugbot.sendMessage();
    }
}

function sendMessage() {
    window.drugbot.sendMessage();
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.drugbot = new DrugBotApp();
    console.log('💊 DrugBot Web Interface başlatıldı');
});

// Handle connection errors
window.addEventListener('error', (event) => {
    console.error('JavaScript hatası:', event.error);
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Promise hatası:', event.reason);
}); 