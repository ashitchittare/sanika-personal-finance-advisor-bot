/**
 * FinBot AI Financial Advisor Frontend Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('finbotChatContainer');
    const questionInput = document.getElementById('finbotQuestionInput');
    const sendButton = document.getElementById('finbotSendBtn');
    const quickPrompts = document.querySelectorAll('.quick-prompt-btn');

    if (!chatContainer || !questionInput || !sendButton) return;

    // Configure marked options for clean HTML rendering
    if (window.marked) {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function appendUserMessage(text) {
        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble chat-bubble-user animate__animated animate__fadeInUp';
        bubble.textContent = text;
        chatContainer.appendChild(bubble);
        scrollToBottom();
    }

    function appendBotLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'finbotLoadingIndicator';
        loadingDiv.className = 'chat-bubble chat-bubble-bot d-flex align-items-center gap-2 text-muted';
        loadingDiv.innerHTML = `
            <div class="spinner-grow spinner-grow-sm text-warning" role="status"></div>
            <span>FinBot is analyzing your financial records and formulating personalized guidance...</span>
        `;
        chatContainer.appendChild(loadingDiv);
        scrollToBottom();
        return loadingDiv;
    }

    function appendBotResponse(markdownText, mode, healthScore) {
        const loadingIndicator = document.getElementById('finbotLoadingIndicator');
        if (loadingIndicator) loadingIndicator.remove();

        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble chat-bubble-bot animate__animated animate__fadeIn';
        
        let parsedHtml = '';
        if (window.marked) {
            parsedHtml = marked.parse(markdownText);
        } else {
            parsedHtml = `<p>${markdownText.replace(/\n/g, '<br>')}</p>`;
        }

        bubble.innerHTML = `
            <div class="d-flex align-items-center justify-content-between border-bottom pb-2 mb-2">
                <span class="badge bg-dark-slate text-warning fw-semibold">
                    <i class="bi bi-robot me-1"></i> ${mode || 'FinBot Engine'}
                </span>
                <small class="text-muted">Just now</small>
            </div>
            <div class="finbot-content">${parsedHtml}</div>
        `;

        chatContainer.appendChild(bubble);
        scrollToBottom();
    }

    async function sendQuery(queryText) {
        const query = queryText.trim();
        if (!query) return;

        appendUserMessage(query);
        questionInput.value = '';
        questionInput.disabled = true;
        sendButton.disabled = true;
        appendBotLoading();

        try {
            const response = await fetch('/finbot/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            if (!response.ok) {
                throw new Error(`HTTP Error ${response.status}`);
            }

            const data = await response.json();
            appendBotResponse(data.advice, data.mode, data.health_score);
        } catch (err) {
            console.error('FinBot Request Error:', err);
            appendBotResponse(
                "⚠️ **FinBot Advisory Notice:** Unable to reach the processing service right now. Please try again or check your server logs.",
                "System Fallback"
            );
        } finally {
            questionInput.disabled = false;
            sendButton.disabled = false;
            questionInput.focus();
        }
    }

    sendButton.addEventListener('click', () => {
        sendQuery(questionInput.value);
    });

    questionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuery(questionInput.value);
        }
    });

    // Wire quick prompt suggestion buttons
    quickPrompts.forEach(btn => {
        btn.addEventListener('click', () => {
            const promptText = btn.getAttribute('data-prompt');
            if (promptText) {
                sendQuery(promptText);
            }
        });
    });
});
