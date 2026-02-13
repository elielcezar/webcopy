// WebCopy - JavaScript da Interface Web

class WebCopyUI {
    constructor() {
        this.currentJobId = null;
        this.pollInterval = null;
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        // Sections
        this.formSection = document.getElementById('form-section');
        this.progressSection = document.getElementById('progress-section');
        this.resultSection = document.getElementById('result-section');
        
        // Form elements
        this.urlInput = document.getElementById('url-input');
        this.submitBtn = document.getElementById('submit-btn');
        
        // Progress elements
        this.progressBar = document.getElementById('progress-bar');
        this.progressStatus = document.getElementById('progress-status');
        this.progressDetails = document.getElementById('progress-details');
        
        // Result elements
        this.resultUrl = document.getElementById('result-url');
        this.resultPath = document.getElementById('result-path');
        this.downloadBtn = document.getElementById('download-btn');
        this.previewBtn = document.getElementById('preview-btn');
        this.newCopyBtn = document.getElementById('new-copy-btn');
        
        // Error
        this.errorMessage = document.getElementById('error-message');
        this.errorText = document.getElementById('error-text');
    }

    attachEventListeners() {
        this.submitBtn.addEventListener('click', () => this.startCopy());
        this.urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.startCopy();
        });
        this.newCopyBtn.addEventListener('click', () => this.resetUI());
        this.downloadBtn.addEventListener('click', () => this.downloadZip());
        this.previewBtn.addEventListener('click', () => this.openPreview());
    }

    validateUrl(url) {
        try {
            const urlObj = new URL(url);
            return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
        } catch {
            return false;
        }
    }

    showError(message) {
        this.errorText.textContent = message;
        this.errorMessage.classList.add('active');
        setTimeout(() => {
            this.errorMessage.classList.remove('active');
        }, 5000);
    }

    async startCopy() {
        const url = this.urlInput.value.trim();
        
        // Validate URL
        if (!url) {
            this.showError('Por favor, insira uma URL');
            return;
        }
        
        if (!this.validateUrl(url)) {
            this.showError('URL inválida. Use formato: https://example.com');
            return;
        }

        // Disable button and show loading
        this.submitBtn.disabled = true;
        this.submitBtn.innerHTML = '<span class="spinner"></span> Iniciando...';

        try {
            const response = await fetch('/api/copy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (response.ok) {
                this.currentJobId = data.job_id;
                this.showProgressSection();
                this.startPolling();
            } else {
                this.showError(data.error || 'Erro ao iniciar cópia');
                this.submitBtn.disabled = false;
                this.submitBtn.innerHTML = '<i class="fas fa-copy"></i> Copiar Site';
            }
        } catch (error) {
            this.showError('Erro de conexão com o servidor');
            this.submitBtn.disabled = false;
            this.submitBtn.innerHTML = '<i class="fas fa-copy"></i> Copiar Site';
        }
    }

    showProgressSection() {
        this.formSection.classList.add('hidden');
        this.resultSection.classList.remove('active');
        this.progressSection.classList.add('active');
        this.progressBar.style.width = '0%';
        this.progressStatus.textContent = 'Iniciando...';
        this.progressDetails.innerHTML = '';
    }

    showResultSection(data) {
        this.progressSection.classList.remove('active');
        this.resultSection.classList.add('active');
        
        // Fill result info
        this.resultUrl.textContent = data.url || 'N/A';
        this.resultPath.textContent = data.output_path || 'N/A';
    }

    resetUI() {
        this.formSection.classList.remove('hidden');
        this.progressSection.classList.remove('active');
        this.resultSection.classList.remove('active');
        this.urlInput.value = '';
        this.submitBtn.disabled = false;
        this.submitBtn.innerHTML = '<i class="fas fa-copy"></i> Copiar Site';
        this.currentJobId = null;
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    startPolling() {
        // Poll every 2 seconds
        this.pollInterval = setInterval(() => {
            this.checkStatus();
        }, 2000);
        
        // Initial check
        this.checkStatus();
    }

    async checkStatus() {
        if (!this.currentJobId) return;

        try {
            const response = await fetch(`/api/status/${this.currentJobId}`);
            const data = await response.json();

            if (response.ok) {
                this.updateProgress(data);

                if (data.status === 'completed') {
                    clearInterval(this.pollInterval);
                    this.showResultSection(data);
                } else if (data.status === 'error') {
                    clearInterval(this.pollInterval);
                    this.showError(data.error || 'Erro durante o processamento');
                    this.resetUI();
                }
            }
        } catch (error) {
            console.error('Error checking status:', error);
        }
    }

    updateProgress(data) {
        // Update progress bar
        const progress = data.progress || 0;
        this.progressBar.style.width = `${progress}%`;
        
        // Update status message
        this.progressStatus.textContent = data.message || 'Processando...';
        
        // Update progress steps
        if (data.steps && data.steps.length > 0) {
            this.progressDetails.innerHTML = data.steps.map(step => {
                let icon = '⏳';
                let className = '';
                
                if (step.status === 'completed') {
                    icon = '✓';
                    className = 'completed';
                } else if (step.status === 'current') {
                    icon = '🔄';
                    className = 'current';
                }
                
                return `
                    <div class="progress-step ${className}">
                        <span>${icon}</span>
                        <span>${step.message}</span>
                    </div>
                `;
            }).join('');
        }
    }

    downloadZip() {
        if (this.currentJobId) {
            window.location.href = `/api/download/${this.currentJobId}`;
        }
    }

    openPreview() {
        if (this.currentJobId) {
            window.open(`/api/preview/${this.currentJobId}`, '_blank');
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new WebCopyUI();
});
