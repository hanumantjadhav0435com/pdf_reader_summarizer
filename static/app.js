class PDFChatApp {
    constructor() {
        this.sessionId = null;
        this.currentFile = null;
        this.isProcessing = false;
        
        this.initializeElements();
        this.bindEvents();
    }
    
    initializeElements() {
        // Upload elements
        this.uploadSection = document.getElementById('upload-section');
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.uploadBtn = document.getElementById('upload-btn');
        this.uploadProgress = document.getElementById('upload-progress');
        
        // Chat elements
        this.chatSection = document.getElementById('chat-section');
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.sendBtn = document.getElementById('send-btn');
        this.currentFileSpan = document.getElementById('current-file');
        this.chunksInfo = document.getElementById('chunks-info');
        
        // Sources elements
        this.sourcesSidebar = document.getElementById('sources-sidebar');
        this.sourcesContent = document.getElementById('sources-content');
        
        // Other elements
        this.statusIndicator = document.getElementById('status-indicator');
        this.clearSessionBtn = document.getElementById('clear-session');
        this.errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
    }
    
    bindEvents() {
        // Upload events
        this.uploadBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        
        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Chat events
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Clear session
        this.clearSessionBtn.addEventListener('click', () => this.clearSession());
        
        // Prevent form submission on enter
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target === this.chatInput) {
                e.preventDefault();
            }
        });
    }
    
    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('drag-over');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('drag-over');
    }
    
    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.fileInput.files = files;
            this.handleFileSelect({ target: { files } });
        }
    }
    
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        if (file.type !== 'application/pdf') {
            this.showError('Please select a PDF file.');
            return;
        }
        
        if (file.size > 16 * 1024 * 1024) {
            this.showError('File too large. Maximum size is 16MB.');
            return;
        }
        
        this.uploadFile(file);
    }
    
    async uploadFile(file) {
        this.setProcessing(true);
        this.showUploadProgress();
        this.updateStatus('Uploading...', 'warning');
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Upload failed');
            }
            
            this.sessionId = data.session_id;
            this.currentFile = data.filename;
            
            this.hideUploadProgress();
            this.showChatInterface(data);
            this.updateStatus('Ready', 'success');
            
        } catch (error) {
            this.hideUploadProgress();
            this.showError(error.message);
            this.updateStatus('Error', 'danger');
        } finally {
            this.setProcessing(false);
        }
    }
    
    showUploadProgress() {
        this.uploadProgress.style.display = 'block';
        // Simulate progress for better UX
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            this.uploadProgress.querySelector('.progress-bar').style.width = progress + '%';
        }, 200);
        
        // Store interval to clear it later
        this.progressInterval = interval;
    }
    
    hideUploadProgress() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        this.uploadProgress.style.display = 'none';
        this.uploadProgress.querySelector('.progress-bar').style.width = '0%';
    }
    
    showChatInterface(data) {
        this.uploadSection.style.display = 'none';
        this.chatSection.style.display = 'block';
        this.sourcesSidebar.style.display = 'block';
        this.clearSessionBtn.style.display = 'inline-block';
        
        this.currentFileSpan.textContent = `Chat with: ${data.filename}`;
        this.chunksInfo.textContent = `${data.chunks_count} content chunks processed`;
        
        // Clear previous messages except system message
        const systemMessage = this.chatMessages.querySelector('.system-message');
        this.chatMessages.innerHTML = '';
        if (systemMessage) {
            this.chatMessages.appendChild(systemMessage);
        }
        
        this.chatInput.focus();
    }
    
    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message || this.isProcessing) return;
        
        this.setProcessing(true);
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        this.addLoadingMessage();
        this.updateStatus('Thinking...', 'info');
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Chat request failed');
            }
            
            this.removeLoadingMessage();
            this.addMessage(data.response, 'assistant');
            this.showSources(data.sources);
            this.updateStatus('Ready', 'success');
            
        } catch (error) {
            this.removeLoadingMessage();
            this.showError(error.message);
            this.updateStatus('Error', 'danger');
        } finally {
            this.setProcessing(false);
            this.chatInput.focus();
        }
    }
    
    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (type === 'user') {
            contentDiv.innerHTML = `<i class="fas fa-user me-2"></i>${this.escapeHtml(content)}`;
        } else {
            contentDiv.innerHTML = `<i class="fas fa-robot me-2"></i>${this.escapeHtml(content)}`;
        }
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addLoadingMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message loading-message';
        messageDiv.id = 'loading-message';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `
            <i class="fas fa-robot me-2"></i>
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    removeLoadingMessage() {
        const loadingMessage = document.getElementById('loading-message');
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }
    
    showSources(sources) {
        if (!sources || sources.length === 0) {
            this.sourcesContent.innerHTML = `
                <p class="text-muted text-center">
                    <i class="fas fa-info-circle me-2"></i>
                    No specific sources found for this query
                </p>
            `;
            return;
        }
        
        let sourcesHtml = '';
        sources.forEach((source, index) => {
            sourcesHtml += `
                <div class="source-item">
                    <div class="source-content">
                        ${this.escapeHtml(this.truncateText(source.text, 200))}
                    </div>
                    <div class="source-meta">
                        <span class="page-badge">Page ${source.page}</span>
                        <small class="text-muted">Relevance: ${source.score || 'High'}</small>
                    </div>
                </div>
            `;
        });
        
        this.sourcesContent.innerHTML = sourcesHtml;
    }
    
    async clearSession() {
        if (!this.sessionId) return;
        
        try {
            await fetch('/clear_session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });
        } catch (error) {
            console.error('Failed to clear session:', error);
        } finally {
            this.resetInterface();
        }
    }
    
    resetInterface() {
        this.sessionId = null;
        this.currentFile = null;
        
        this.uploadSection.style.display = 'block';
        this.chatSection.style.display = 'none';
        this.sourcesSidebar.style.display = 'none';
        this.clearSessionBtn.style.display = 'none';
        
        this.fileInput.value = '';
        this.chatInput.value = '';
        this.updateStatus('Ready', 'secondary');
        
        // Reset sources
        this.sourcesContent.innerHTML = `
            <p class="text-muted text-center">
                <i class="fas fa-info-circle me-2"></i>
                Sources will appear here when you ask questions
            </p>
        `;
    }
    
    setProcessing(isProcessing) {
        this.isProcessing = isProcessing;
        this.sendBtn.disabled = isProcessing;
        this.chatInput.disabled = isProcessing;
        this.uploadBtn.disabled = isProcessing;
    }
    
    updateStatus(text, type) {
        this.statusIndicator.textContent = text;
        this.statusIndicator.className = `badge bg-${type} me-2`;
    }
    
    showError(message) {
        document.getElementById('errorModalBody').textContent = message;
        this.errorModal.show();
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PDFChatApp();
});
