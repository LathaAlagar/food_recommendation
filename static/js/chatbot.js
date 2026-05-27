// FoodieFinds AI - Chatbot Interface Handler

document.addEventListener('DOMContentLoaded', () => {
    initChatbot();
});

function initChatbot() {
    const chatToggle = document.getElementById('chat-toggle-btn');
    const chatContainer = document.getElementById('chatbot-container');
    const closeChat = document.getElementById('close-chat-btn');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const voiceBtn = document.getElementById('voice-input-btn');
    
    if (!chatToggle || !chatContainer || !chatForm || !chatInput || !chatMessages) return;
    
    let isHistoryLoaded = false;
    let recognition = null;
    let isRecording = false;

    // --- Web Speech API (Voice Input) ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        
        recognition.onstart = () => {
            isRecording = true;
            voiceBtn.classList.add('pulse-recording', 'text-red-500', 'bg-red-50', 'dark:bg-red-950');
            chatInput.placeholder = "Listening...";
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            showToast('Voice search failed. Try again.', 'error');
            stopRecording();
        };
        
        recognition.onend = () => {
            stopRecording();
        };
    } else {
        voiceBtn.style.display = 'none'; // Hide if not supported
    }

    function startRecording() {
        if (!recognition) return;
        try {
            recognition.start();
        } catch (e) {
            console.error(e);
        }
    }

    function stopRecording() {
        if (!recognition) return;
        isRecording = false;
        voiceBtn.classList.remove('pulse-recording', 'text-red-500', 'bg-red-50', 'dark:bg-red-950');
        chatInput.placeholder = "Ask me anything...";
        try {
            recognition.stop();
        } catch (e) {
            // ignore
        }
    }

    voiceBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });

    // --- Open/Close Chat ---
    chatToggle.addEventListener('click', () => {
        chatContainer.classList.remove('hidden');
        chatToggle.classList.add('hidden');
        chatInput.focus();
        
        if (!isHistoryLoaded) {
            loadChatHistory();
        }
    });
    
    closeChat.addEventListener('click', () => {
        chatContainer.classList.add('hidden');
        chatToggle.classList.remove('hidden');
    });

    // --- Submit Message ---
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (!text) return;
        
        // Append user message
        appendMessage('user', text);
        chatInput.value = '';
        
        // Append typing state
        const typingIndicator = appendTypingIndicator();
        
        try {
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });
            
            typingIndicator.remove();
            
            if (response.ok) {
                const data = await response.json();
                appendMessage('model', data.reply);
            } else {
                appendMessage('model', "⚠️ Sorry, I ran into an error processing your query. Please try again.");
            }
        } catch (err) {
            typingIndicator.remove();
            appendMessage('model', "❌ Connection error. Please verify the backend is running.");
            console.error(err);
        }
    });

    // --- Actions ---
    async function loadChatHistory() {
        chatMessages.innerHTML = '';
        // Add a friendly greeting
        appendMessage('model', "👋 Hi! I am **FoodieFinds AI**, your personal food advisor. Ask me anything about foods, restaurants in Chennai, healthy options, weather-based suggestions, or cheap eats!");
        
        try {
            const response = await fetch('/api/chatbot/history');
            if (response.ok) {
                const history = await response.json();
                if (history && history.length > 0) {
                    history.forEach(item => {
                        appendMessage(item.role, item.message);
                    });
                }
                isHistoryLoaded = true;
            }
        } catch (e) {
            console.error("Could not fetch chat history:", e);
        }
    }

    function appendMessage(role, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex mb-3 ${role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-up`;
        
        const bubble = document.createElement('div');
        bubble.className = `max-w-[85%] rounded-2xl px-4 py-2.5 text-sm shadow-sm ${
            role === 'user' 
                ? 'bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-tr-none' 
                : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-tl-none border border-gray-200 dark:border-gray-700'
        }`;
        
        // Parse simple markdown format
        bubble.innerHTML = parseMarkdown(text);
        
        messageDiv.appendChild(bubble);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendTypingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex mb-3 justify-start animate-fade-up`;
        
        const bubble = document.createElement('div');
        bubble.className = 'bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm border border-gray-200 dark:border-gray-700 flex space-x-1 items-center';
        bubble.innerHTML = `
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
        `;
        
        messageDiv.appendChild(bubble);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }

    // A simple, bulletproof markdown parser
    function parseMarkdown(text) {
        let html = text;
        // Escape HTML to prevent XSS (except for our custom markdown tags)
        html = html
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
            
        // Convert bold: **text** -> <strong>text</strong>
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert inline code: `text` -> <code class="bg-gray-200 dark:bg-gray-700 px-1 rounded">$1</code>
        html = html.replace(/`(.*?)`/g, '<code class="bg-gray-200 dark:bg-gray-700 px-1 rounded text-xs">$1</code>');
        
        // Convert bullet points starting with * or - at new lines
        html = html.replace(/^(?:\*|-)\s+(.*)$/gm, '<li class="ml-4 list-disc my-1">$1</li>');
        
        // Group lists
        html = html.replace(/(<li.*<\/li>)/s, '<ul class="my-1">$1</ul>');
        
        // Convert Line Breaks
        html = html.replace(/\n/g, '<br>');
        
        // Emoticons/Icons
        html = html.replace(/(⭐|🍛|🌧️|☀️|🪙|🥗|🔥|👋|❌|⚠️|✅)/g, '<span class="mr-1">$1</span>');
        
        return html;
    }
}
