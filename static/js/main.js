// Globle-1 Version 1.0.1 - Fixed Pro status and UI errors
document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-messages');
    const chatWrapper = document.getElementById('chat-wrapper');
    const welcomeScreen = document.getElementById('welcome-screen');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const micBtn = document.getElementById('mic-btn'); // Added back
    const sidebar = document.querySelector('.sidebar');
    const sidebarCloseBtn = document.getElementById('sidebar-close-btn');
    const sidebarOpenBtn = document.getElementById('sidebar-open-btn');
    const attachBtn = document.getElementById('attach-btn');
    const fileAttachInput = document.getElementById('file-attach-input');
    const filePreviewContainer = document.getElementById('file-preview-container');
    let attachedFile = null;

    // Track system state
    let lastInputWasVoice = false;
    let isGenerating = false;

    const sidebarOverlay = document.getElementById('sidebar-overlay');

    // --- Media Viewer Logic ---
    const mediaModal = document.getElementById('media-modal');
    const mediaViewerBody = document.getElementById('media-viewer-body');
    const closeMediaBtn = document.getElementById('close-media-btn');
    const modalDownloadBtn = document.getElementById('modal-download-btn');

    function openMediaModal(element) {
        if (!mediaModal || !mediaViewerBody) return;

        mediaViewerBody.innerHTML = '';
        const clone = element.cloneNode(true);

        // Remove style constraints from clone to show full size
        clone.style.width = 'auto';
        clone.style.height = 'auto';
        clone.style.maxWidth = '100%';
        clone.style.maxHeight = '75vh';
        clone.style.cursor = 'default';

        if (clone.tagName === 'VIDEO') {
            clone.controls = true;
            clone.autoplay = true;
        }

        mediaViewerBody.appendChild(clone);
        mediaModal.classList.remove('hidden');

        // Setup download button for the modal
        if (modalDownloadBtn) {
            modalDownloadBtn.onclick = () => {
                const src = element.src || element.querySelector('source')?.src;
                if (src) {
                    if (src.startsWith('data:')) {
                        const link = document.createElement('a');
                        link.href = src;
                        link.download = 'generated-media.png';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    } else {
                        const downloadUrl = `/download_media?url=${encodeURIComponent(src)}`;
                        window.location.href = downloadUrl;
                    }
                }
            };
        }
    }

    if (closeMediaBtn) {
        closeMediaBtn.addEventListener('click', () => {
            mediaModal.classList.add('hidden');
            mediaViewerBody.innerHTML = '';
        });
    }

    if (mediaModal) {
        mediaModal.addEventListener('click', (e) => {
            if (e.target === mediaModal) {
                mediaModal.classList.add('hidden');
                mediaViewerBody.innerHTML = '';
            }
        });
    }

    // Configure marked globally to open links in new tab
    if (typeof marked !== 'undefined') {
        const renderer = new marked.Renderer();
        const linkRenderer = renderer.link.bind(renderer);
        renderer.link = (href, title, text) => {
            const html = linkRenderer(href, title, text);
            return html.replace(/^<a /, '<a target="_blank" rel="noopener noreferrer" ');
        };
        marked.setOptions({
            renderer: renderer,
            highlight: function (code, lang) {
                if (typeof hljs !== 'undefined') {
                    if (lang && hljs.getLanguage(lang)) {
                        return hljs.highlight(code, { language: lang }).value;
                    }
                    return hljs.highlightAuto(code).value;
                }
                return code;
            },
            breaks: true,
            gfm: true
        });
    }

    // Sidebar Toggle Logic
    function toggleSidebar(show) {
        if (show) {
            sidebar.classList.remove('collapsed');
            sidebarOpenBtn.classList.remove('visible');
            if (window.innerWidth <= 768) {
                sidebarOverlay.classList.add('active');
            }
        } else {
            sidebar.classList.add('collapsed');
            sidebarOpenBtn.classList.add('visible');
            if (window.innerWidth <= 768) {
                sidebarOverlay.classList.remove('active');
            }
        }
    }

    if (sidebarCloseBtn && sidebarOpenBtn) {
        sidebarCloseBtn.addEventListener('click', () => toggleSidebar(false));
        sidebarOpenBtn.addEventListener('click', () => toggleSidebar(true));
        if (sidebarOverlay) {
            sidebarOverlay.addEventListener('click', () => toggleSidebar(false));
        }
    }





    // --- Voice Logic (Externalized) ---
    const voiceAssistant = new VoiceAssistant({
        onStart: () => {
            micBtn.classList.add('recording');
            userInput.placeholder = "Listening...";
        },
        onEnd: () => {
            micBtn.classList.remove('recording');
            userInput.placeholder = "Ask anything";
        },
        onInterim: (transcript) => {
            userInput.value = transcript;
        },
        onResult: (transcript) => {
            console.log("🎤 Voice input received:", transcript);
            userInput.value = transcript;
            lastInputWasVoice = true;
            console.log("✅ lastInputWasVoice flag set to TRUE");
            handleSendMessage();
        },
        onError: (error) => {
            userInput.placeholder = "Error: " + error;
            console.error("Voice Error:", error);
            micBtn.classList.remove('recording');
        }
    });



    let currentChatId = localStorage.getItem('current_chat_id');
    let chatHistory = JSON.parse(localStorage.getItem('chat_history') || '[]');

    function saveChatToLocalStorage() {
        localStorage.setItem('chat_history', JSON.stringify(chatHistory));
        if (currentChatId) {
            localStorage.setItem('current_chat_id', currentChatId);
        } else {
            localStorage.removeItem('current_chat_id');
        }
        renderChatHistory();
    }

    function renderChatHistory(filter = '') {
        const historyList = document.getElementById('chat-history-list');
        if (!historyList) return;

        historyList.innerHTML = '';
        const filtered = chatHistory.filter(c => c.title.toLowerCase().includes(filter.toLowerCase()));

        // Add matching formulas from library
        const formulaLibrary = [
            {
                title: "Gravitational Force",
                tag: "Physics",
                formula: "$$F = \\frac{G m_1 m_2}{r^2}$$"
            },
            {
                title: "Quadratic Formula",
                tag: "Math LaTeX",
                formula: "$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$"
            },
            {
                title: "Sum Range Formula",
                tag: "Excel Spreadsheet",
                formula: "`=SUM(A1:A10)`"
            },
            {
                title: "IF Condition",
                tag: "Excel Spreadsheet",
                formula: "`=IF(A1>50,\"Pass\",\"Fail\")`"
            },
            {
                title: "Einstein's Relativity",
                tag: "Physics",
                formula: "$$E = mc^2$$"
            },
            {
                title: "Newton's Second Law",
                tag: "Physics",
                formula: "$$F = ma$$"
            },
            {
                title: "Sulfuric Acid",
                tag: "Chemistry",
                formula: "$$H_2SO_4$$"
            },
            {
                title: "Circle Area calculation",
                tag: "Programming Python",
                formula: "```python\narea = 3.14 * r * r\n```"
            },
            {
                title: "Fraction Render",
                tag: "HTML Website",
                formula: "\\( \\frac{a}{b} \\)"
            },
            {
                title: "Client Churn Prediction",
                tag: "Analytics",
                formula: "$$P(y=1) = \\frac{1}{1 + e^{-( \\beta_0 + \\beta_1 x_1 + \\dots )}}$$"
            },
            {
                title: "Compound Growth",
                tag: "Growth",
                formula: "$$A = P \\left(1 + \\frac{r}{n}\\right)^{nt}$$"
            }
        ];

        const filteredFormulas = formulaLibrary.filter(f =>
            filter && (f.title.toLowerCase().includes(filter.toLowerCase()) || f.tag.toLowerCase().includes(filter.toLowerCase()))
        );

        if (filteredFormulas.length > 0) {
            const label = document.createElement('div');
            label.className = 'history-label';
            label.style.marginTop = '10px';
            label.innerText = 'Formula Intelligence';
            historyList.appendChild(label);

            filteredFormulas.forEach(formula => {
                const item = document.createElement('div');
                item.className = 'history-item formula-item';
                item.style.borderLeft = '2px solid var(--accent-purple)';
                item.innerHTML = `
                    <div class="history-item-content">
                        <svg viewBox="0 0 24 24" width="16" height="16" stroke="var(--accent-purple)" stroke-width="2" fill="none">
                            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
                        </svg>
                        <span style="color: var(--accent-purple); font-weight: 600;">${formula.title}</span>
                    </div>
                `;
                item.addEventListener('click', () => {
                    userInput.value = `Tell me about the ${formula.title}: ${formula.formula}`;
                    handleSendMessage();
                    if (window.innerWidth <= 768) toggleSidebar(false);
                });
                historyList.appendChild(item);
            });
        }

        if (filtered.length > 0) {
            filtered.forEach(chat => {
                const item = document.createElement('div');
                item.className = 'history-item';
                if (chat.id === currentChatId) item.classList.add('active');

                item.innerHTML = `
                    <div class="history-item-content">
                        <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                        <span>${chat.title}</span>
                    </div>
                    <div class="delete-chat-btn" title="Delete chat">
                        <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                    </div>
                `;

                item.querySelector('.history-item-content').addEventListener('click', () => loadChat(chat.id));
                item.querySelector('.delete-chat-btn').addEventListener('click', (e) => {
                    e.stopPropagation();
                    deleteChat(chat.id);
                });
                historyList.appendChild(item);
            });
        }
    }

    function deleteChat(chatId) {
        if (!confirm('Are you sure you want to delete this chat?')) return;

        chatHistory = chatHistory.filter(c => c.id !== chatId);
        if (currentChatId === chatId) {
            currentChatId = null;
            chatContainer.innerHTML = '';
            welcomeScreen.style.display = 'flex';
        }
        saveChatToLocalStorage();
    }

    function loadChat(chatId) {
        currentChatId = chatId;
        const chat = chatHistory.find(c => c.id === chatId);
        if (!chat) return;

        chatContainer.innerHTML = '';
        welcomeScreen.style.display = 'none';

        chat.messages.forEach(msg => {
            addMessage(msg.text, msg.isAi, null, true);
        });


        chatWrapper.scrollTop = chatWrapper.scrollHeight;
        saveChatToLocalStorage();
    }

    function updateChatHistoryEntry(text, isAi) {
        if (!currentChatId && !isAi) {
            currentChatId = Date.now().toString();
            chatHistory.unshift({
                id: currentChatId,
                title: text.length > 30 ? text.substring(0, 30) + '...' : text,
                messages: []
            });
        }

        const chat = chatHistory.find(c => c.id === currentChatId);
        if (chat) {
            chat.messages.push({ text, isAi });
            saveChatToLocalStorage();
        }
    }

    // Initialize history
    renderChatHistory();

    // Restore last active chat if it exists
    if (currentChatId) {
        loadChat(currentChatId);
    }

    const historySearch = document.getElementById('history-search');
    const toggleSearchBtn = document.getElementById('toggle-search-btn');
    const sidebarSearchContainer = document.getElementById('sidebar-search-container');

    if (toggleSearchBtn && sidebarSearchContainer) {
        toggleSearchBtn.addEventListener('click', () => {
            const isHidden = sidebarSearchContainer.style.display === 'none';
            sidebarSearchContainer.style.display = isHidden ? 'block' : 'none';
            if (isHidden) {
                historySearch.focus();
            } else {
                historySearch.value = '';
                renderChatHistory();
            }
        });
    }

    if (historySearch) {
        historySearch.addEventListener('input', (e) => {
            renderChatHistory(e.target.value);
        });
    }

    const settingsNavBtn = document.getElementById('settings-nav-btn');
    if (settingsNavBtn) {
        settingsNavBtn.addEventListener('click', () => {
            const settingsTrigger = document.getElementById('settings-trigger');
            if (settingsTrigger) {
                settingsTrigger.click();
            }
            // If the above doesn't open the menu, show user-menu directly
            const userMenu = document.getElementById('user-menu');
            if (userMenu) {
                userMenu.style.display = userMenu.style.display === 'none' ? 'block' : 'none';
            }
        });
    }

    const genImageNavBtn = document.getElementById('gen-image-nav-btn');
    if (genImageNavBtn) {
        genImageNavBtn.addEventListener('click', () => {
            userInput.value = "Generate a beautiful image of ";
            userInput.focus();
            // On mobile, close sidebar after clicking
            if (window.innerWidth <= 768) {
                sidebar.classList.add('collapsed');
                sidebarOverlay.classList.remove('active');
            }
        });
    }

    const genVideoNavBtn = document.getElementById('gen-video-nav-btn');
    if (genVideoNavBtn) {
        genVideoNavBtn.addEventListener('click', () => {
            userInput.value = "Animate this and create a video of ";
            userInput.focus();
            // On mobile, close sidebar after clicking
            if (window.innerWidth <= 768) {
                sidebar.classList.add('collapsed');
                sidebarOverlay.classList.remove('active');
            }
        });
    }

    const closeAppBtn = document.getElementById('close-app-btn');
    if (closeAppBtn) {
        closeAppBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to close the website? This will clear your current session.')) {
                localStorage.removeItem('current_chat_id');
                localStorage.removeItem('chat_history');
                window.location.reload();
            }
        });
    }

    const projectNavBtn = document.getElementById('project-nav-btn');
    if (projectNavBtn) {
        projectNavBtn.addEventListener('click', () => {
            userInput.value = "[FAST PROJECT MODE] Create a detailed structure for: ";
            userInput.focus();
            // On mobile, close sidebar after clicking
            if (window.innerWidth <= 768) {
                sidebar.classList.add('collapsed');
                sidebarOverlay.classList.remove('active');
            }
        });
    }

    const newChatBtn = document.getElementById('new-chat-btn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', () => {
            currentChatId = null;
            chatContainer.innerHTML = '';
            welcomeScreen.style.display = 'flex';
            saveChatToLocalStorage();
        });
    }

    function addMessage(text, isAi = true, emotion = null, skipTypewriter = false, timeTaken = null) {
        // Hide welcome screen on first message
        if (welcomeScreen.style.display !== 'none') {
            welcomeScreen.style.display = 'none';
        }

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isAi ? 'ai-message' : 'user-message');

        if (isAi) {
            messageDiv.innerHTML = `
                <div class="message-content"></div>
                <div class="message-actions" style="opacity: 1;">
                    ${timeTaken ? `<span class="generation-time">${timeTaken}s</span>` : ''}
                    <button class="msg-action-btn download-btn" title="Download image" style="display: none;">
                        <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v4"></path>
                            <polyline points="7 10 12 15 17 10"></polyline>
                            <line x1="12" y1="15" x2="12" y2="3"></line>
                        </svg>
                    </button>
                    <button class="msg-action-btn speak-btn" title="Listen to response">
                        <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none">
                            <path d="M11 5L6 9H2v6h4l5 4V5z"></path>
                            <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                        </svg>
                    </button>
                    <button class="msg-action-btn copy-btn" title="Copy to clipboard">
                        <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                    </button>
                </div>
            `;

            const contentDiv = messageDiv.querySelector('.message-content');
            const actionsDiv = messageDiv.querySelector('.message-actions');

            // Typewriter effect logic
            if (skipTypewriter || text.includes('```')) {
                // For code generation, we render fully or use a faster reveal
                contentDiv.innerHTML = marked.parse(text);
                actionsDiv.style.opacity = '1';
                finalizeMessage();
            } else {
                // line-by-line reveal
                const lines = text.split('\n');
                let i = 0;
                const speed = 80; // milliseconds per line

                // If text contains HTML (like video), don't typewriter it or it breaks tags
                if (text.includes('<') && text.includes('>')) {
                    contentDiv.innerHTML = text;
                    actionsDiv.style.opacity = '1';
                    finalizeMessage();
                } else {
                    contentDiv.classList.add('typewriter-cursor');
                    function typeWriter() {
                        if (i < lines.length) {
                            const currentBatch = lines.slice(0, i + 1).join('\n');
                            contentDiv.innerHTML = marked.parse(currentBatch);
                            i++;
                            chatWrapper.scrollTop = chatWrapper.scrollHeight;
                            setTimeout(typeWriter, speed);
                        } else {
                            contentDiv.classList.remove('typewriter-cursor');
                            actionsDiv.style.opacity = '1';
                            finalizeMessage();
                        }
                    }
                    typeWriter();
                }
            }

            function finalizeMessage() {
                // Ensure all links open in a new tab
                contentDiv.querySelectorAll('a').forEach(link => {
                    link.setAttribute('target', '_blank');
                    link.setAttribute('rel', 'noopener noreferrer');
                });

                // Render Math Formulas with KaTeX
                if (window.renderMathInElement) {
                    renderMathInElement(contentDiv, {
                        delimiters: [
                            { left: "$$", right: "$$", display: true },
                            { left: "$", right: "$", display: false },
                            { left: "\\(", right: "\\)", display: false },
                            { left: "\\[", right: "\\]", display: true }
                        ],
                        throwOnError: false
                    });
                }

                // Ensure all code blocks are highlighted and add top professional headers
                messageDiv.querySelectorAll('pre').forEach((pre) => {
                    if (pre.querySelector('.code-header')) return;

                    const code = pre.querySelector('code');
                    let lang = 'Code';

                    if (code) {
                        hljs.highlightElement(code);
                        // Extract language from class (e.g., "language-python")
                        const langClass = Array.from(code.classList).find(c => c.startsWith('language-'));
                        if (langClass) {
                            lang = langClass.replace('language-', '');
                        }
                    }

                    // Create Header Bar
                    const header = document.createElement('div');
                    header.className = 'code-header';

                    const langSpan = document.createElement('span');
                    langSpan.className = 'code-lang';
                    langSpan.innerText = lang;

                    const copyBtn = document.createElement('button');
                    copyBtn.className = 'code-copy-btn';
                    copyBtn.innerHTML = `
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                        <span>Copy Code</span>
                    `;

                    copyBtn.addEventListener('click', () => {
                        const textToCopy = code ? code.innerText : pre.innerText;
                        navigator.clipboard.writeText(textToCopy).then(() => {
                            const originalHTML = copyBtn.innerHTML;
                            copyBtn.innerHTML = `
                                <svg viewBox="0 0 24 24" fill="none" stroke="#30d158" stroke-width="2">
                                    <polyline points="20 6 9 17 4 12"></polyline>
                                </svg>
                                <span style="color: #30d158">Copied!</span>
                            `;
                            setTimeout(() => { copyBtn.innerHTML = originalHTML; }, 2000);
                        });
                    });

                    header.appendChild(langSpan);
                    header.appendChild(copyBtn);
                    pre.insertBefore(header, pre.firstChild);
                });

                // Add listeners for the buttons
                const speakBtn = messageDiv.querySelector('.speak-btn');
                if (speakBtn) {
                    speakBtn.addEventListener('click', () => voiceAssistant.speak(text));
                }
                const copyBtn = messageDiv.querySelector('.copy-btn');
                if (copyBtn) {
                    copyBtn.addEventListener('click', () => {
                        // Use innerText to get clean text without HTML tags but keeping newlines
                        const cleanText = contentDiv.innerText;
                        navigator.clipboard.writeText(cleanText);

                        const originalHTML = copyBtn.innerHTML;
                        copyBtn.innerHTML = `
                            <svg viewBox="0 0 24 24" width="14" height="14" stroke="#30d158" stroke-width="2" fill="none"><polyline points="20 6 9 17 4 12"></polyline></svg>
                        `;
                        setTimeout(() => {
                            copyBtn.innerHTML = originalHTML;
                        }, 2000);
                    });
                }

                // Handle image download if image exists
                const downloadBtn = messageDiv.querySelector('.download-btn');
                const img = contentDiv.querySelector('img');
                const video = contentDiv.querySelector('video');

                if (img) {
                    img.style.cursor = 'zoom-in';
                    img.addEventListener('click', () => openMediaModal(img));

                    if (downloadBtn) {
                        downloadBtn.style.display = 'flex';
                        downloadBtn.addEventListener('click', (e) => {
                            e.stopPropagation();
                            if (img.src.startsWith('data:')) {
                                // Direct download for base64 data URLs
                                const link = document.createElement('a');
                                link.href = img.src;
                                link.download = 'generated-image.png';
                                document.body.appendChild(link);
                                link.click();
                                document.body.appendChild(link);
                                document.body.removeChild(link);
                            } else {
                                // Proxy download for external URLs
                                const downloadUrl = `/download_media?url=${encodeURIComponent(img.src)}`;
                                window.location.href = downloadUrl;
                            }
                        });
                    }
                }

                if (video) {
                    video.style.cursor = 'pointer';
                    video.addEventListener('click', (e) => {
                        // Only open modal if not clicking controls
                        if (e.offsetY < video.clientHeight - 40) {
                            openMediaModal(video);
                        }
                    });
                }

                // Speak the AI response if it was triggered by voice
                if (lastInputWasVoice) {
                    console.log("🔊 Auto-speaking AI response...");
                    voiceAssistant.speak(text);
                    lastInputWasVoice = false; // Reset flag after speaking
                }

                // Save AI message to history if it's new
                if (!skipTypewriter) {
                    updateChatHistoryEntry(text, isAi);
                }
            }
        } else {
            // Render User messages with marked and KaTeX
            messageDiv.innerHTML = `
                <div class="message-content">${marked.parse(text)}</div>
                <div class="message-actions" style="opacity: 1; align-self: flex-end;">
                     <button class="msg-action-btn copy-btn" title="Copy to clipboard">
                        <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                        </svg>
                    </button>
                </div>
            `;

            // Allow actions to be seen on hover (handled by CSS .message:hover .message-actions)
            // But for user message we need to ensure the CSS selector works.
            // .user-message is now a flex container. .message-actions is inside it.
            // We need to make sure the hover transparency works.

            const contentDiv = messageDiv.querySelector('.message-content');

            // Ensure all links open in a new tab
            contentDiv.querySelectorAll('a').forEach(link => {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
            });

            finalizeUserMessage();

            // Render Math in user message
            if (window.renderMathInElement) {
                renderMathInElement(contentDiv, {
                    delimiters: [
                        { left: "$$", right: "$$", display: true },
                        { left: "$", right: "$", display: false },
                        { left: "\\(", right: "\\)", display: false },
                        { left: "\\[", right: "\\]", display: true }
                    ],
                    throwOnError: false
                });
            }

            // Add Listener for Copy Button
            const copyBtn = messageDiv.querySelector('.copy-btn');
            if (copyBtn) {
                copyBtn.addEventListener('click', () => {
                    const cleanText = contentDiv.innerText;
                    navigator.clipboard.writeText(cleanText);
                    const originalHTML = copyBtn.innerHTML;
                    copyBtn.innerHTML = `
                        <svg viewBox="0 0 24 24" width="14" height="14" stroke="#30d158" stroke-width="2" fill="none"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    `;
                    setTimeout(() => {
                        copyBtn.innerHTML = originalHTML;
                    }, 2000);
                });
            }
        }

        chatContainer.appendChild(messageDiv);
        chatWrapper.scrollTop = chatWrapper.scrollHeight;

        function finalizeUserMessage() {
            // Save to history if it's new
            if (!skipTypewriter) {
                updateChatHistoryEntry(text, isAi);
            }
        }
    }


    async function handleSendMessage() {
        if (isGenerating) return;

        const prompt = userInput.value.trim();
        if (!prompt && !attachedFile) return;

        isGenerating = true;
        updateSendButtonState();

        userInput.value = '';
        const displayPrompt = attachedFile ? (prompt || "Attached File") : prompt;
        addMessage(displayPrompt, false);

        // Hide preview
        filePreviewContainer.classList.add('hidden');
        filePreviewContainer.innerHTML = '';

        const thinkingDiv = document.createElement('div');
        thinkingDiv.classList.add('message', 'ai-message', 'thinking');

        const isMediaGen = /(generate|create|make|draw|paint|animate|genrate|enrate|genrrate|generrate|render|design).*\s+(image|video|photo|picture|clip|masterpiece|illustration|portrait|sketch|motion|movie|avatar|logo)/i.test(prompt) || /animate\s+this/i.test(prompt) || /\blogo\b/i.test(prompt);

        if (isMediaGen) {
            thinkingDiv.innerHTML = `
                <div class="generating-image-indicator">
                    <div class="scan-line"></div>
                    <div class="glow-orb"></div>
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.5;">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <circle cx="8.5" cy="8.5" r="1.5"></circle>
                        <polyline points="21 15 16 10 5 21"></polyline>
                    </svg>
                    <span>Generating your Masterpiece...</span>
                </div>
            `;
        } else {
            thinkingDiv.innerHTML = '<strong>GlobleXGPT</strong> is thinking...';
        }

        chatContainer.appendChild(thinkingDiv);
        chatWrapper.scrollTop = chatWrapper.scrollHeight;

        try {
            const user = JSON.parse(localStorage.getItem('user'));
            const payload = {
                prompt: prompt,
                email: user ? user.email : 'guest',
                file: attachedFile ? {
                    name: attachedFile.name,
                    type: attachedFile.type,
                    data: attachedFile.data
                } : null
            };

            attachedFile = null; // Clear after prep

            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            chatContainer.removeChild(thinkingDiv);

            // Safety check for response text
            let aiResponseText = data.response;
            if (!aiResponseText || typeof aiResponseText !== 'string' || aiResponseText.trim() === "") {
                aiResponseText = "I'm sorry, I'm having trouble processing your request. Please try again.";
            }

            addMessage(aiResponseText, true, data.emotion, false, data.time_taken);

        } catch (error) {
            console.error('Error:', error);
            if (chatContainer.contains(thinkingDiv)) chatContainer.removeChild(thinkingDiv);
            addMessage("I'm sorry, I encountered an internal error. Please check if the server is running.");
        } finally {
            isGenerating = false;
            updateSendButtonState();
        }
    }

    function updateSendButtonState() {
        if (isGenerating) {
            sendBtn.style.opacity = '0.5';
            sendBtn.style.cursor = 'not-allowed';
            sendBtn.disabled = true;
            userInput.placeholder = "GlobleXGPT is thinking...";
        } else {
            sendBtn.style.opacity = '1';
            sendBtn.style.cursor = 'pointer';
            sendBtn.disabled = false;
            userInput.placeholder = "Message GlobleXGPT...";
            userInput.focus();
        }
    }

    sendBtn.addEventListener('click', () => {
        lastInputWasVoice = false;
        handleSendMessage();
    });

    if (micBtn) {
        micBtn.addEventListener('click', () => {
            voiceAssistant.toggle();
        });
    }

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            lastInputWasVoice = false;
            handleSendMessage();
        }
    });

    if (attachBtn && fileAttachInput) {
        attachBtn.addEventListener('click', () => fileAttachInput.click());

        const handleFileChange = async (files) => {
            if (!files || files.length === 0) return;

            // Helper function to get file type icon
            const getFileIcon = (file) => {
                const type = file.type;
                const name = file.name.toLowerCase();

                if (type.startsWith('image/')) return { icon: '🖼️', class: 'image' };
                if (type === 'application/pdf' || name.endsWith('.pdf')) return { icon: '📕', class: 'pdf' };
                if (type.startsWith('video/') || name.match(/\.(mp4|avi|mov|mkv)$/)) return { icon: '🎬', class: 'video' };
                if (type.startsWith('audio/') || name.match(/\.(mp3|wav|ogg|m4a)$/)) return { icon: '🎵', class: 'audio' };
                if (name.match(/\.(zip|rar|7z|tar|gz)$/)) return { icon: '📦', class: 'archive' };
                if (name.match(/\.(js|py|java|cpp|html|css|json|xml)$/)) return { icon: '💻', class: 'code' };
                if (name.match(/\.(doc|docx|txt|rtf)$/)) return { icon: '📄', class: 'document' };
                if (name.match(/\.(xls|xlsx|csv)$/)) return { icon: '📊', class: 'spreadsheet' };
                if (name.match(/\.(ppt|pptx)$/)) return { icon: '📽️', class: 'presentation' };
                return { icon: '📎', class: 'file' };
            };

            // Handle multiple files
            if (files.length > 1) {
                let combinedText = "--- Combined Files (Folder/Multiple) ---\n\n";
                let hasText = false;
                let imageCount = 0;

                for (let i = 0; i < files.length; i++) {
                    const file = files[i];

                    if (file.type.startsWith('image/')) {
                        imageCount++;
                        continue;
                    }

                    try {
                        const text = await file.text();
                        combinedText += `--- File: ${file.name} ---\n${text}\n\n`;
                        hasText = true;
                    } catch (err) {
                        console.warn(`Could not read file ${file.name}`, err);
                    }
                }

                if (hasText || imageCount > 0) {
                    attachedFile = {
                        name: `Batch_Upload_${files.length}_files`,
                        type: 'text/plain',
                        data: combinedText,
                        isText: true,
                        fileCount: files.length
                    };

                    // Show compact icon-only preview
                    filePreviewContainer.classList.remove('hidden');
                    filePreviewContainer.innerHTML = `
                        <div class="file-preview-item" data-filename="${files.length} files attached">
                            <div class="file-icon archive">📦</div>
                            <span class="file-count-badge">${files.length}</span>
                            <button class="file-remove-btn">×</button>
                        </div>
                    `;

                    filePreviewContainer.querySelector('.file-remove-btn').addEventListener('click', () => {
                        attachedFile = null;
                        filePreviewContainer.classList.add('hidden');
                        filePreviewContainer.innerHTML = '';
                        fileAttachInput.value = '';
                        userInput.placeholder = "Message GlobleXGPT...";
                    });

                    userInput.placeholder = "Ask about these files...";
                    userInput.focus();
                    return;
                }
            }

            // Single file processing
            const file = files[0];
            const isImage = file.type.startsWith('image/');
            const fileInfo = getFileIcon(file);
            const reader = new FileReader();

            reader.onload = (event) => {
                attachedFile = {
                    name: file.name,
                    type: file.type,
                    data: event.target.result,
                    isText: !isImage
                };

                // Show compact icon-only preview
                filePreviewContainer.classList.remove('hidden');

                if (isImage) {
                    // For images, show thumbnail with search indicator
                    filePreviewContainer.innerHTML = `
                        <div class="file-preview-item" data-filename="${file.name}">
                            <img src="${event.target.result}" alt="${file.name}">
                            <button class="image-enhance-btn" id="enhance-current-img">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
                                </svg>
                                <span>Enhance</span>
                            </button>
                            <span class="image-search-indicator" title="Visual Search Enabled">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="11" cy="11" r="8"></circle>
                                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                                </svg>
                            </span>
                            <button class="file-remove-btn">×</button>
                        </div>
                    `;

                    // Add listener for Enhance button
                    const enhanceBtn = filePreviewContainer.querySelector('#enhance-current-img');
                    if (enhanceBtn) {
                        enhanceBtn.addEventListener('click', (e) => {
                            e.stopPropagation();
                            handleImageEnhance();
                        });
                    }
                    userInput.placeholder = "Search for similar images or ask about this image...";
                } else {
                    // For other files, show icon only
                    filePreviewContainer.innerHTML = `
                        <div class="file-preview-item" data-filename="${file.name}">
                            <div class="file-icon ${fileInfo.class}">${fileInfo.icon}</div>
                            <button class="file-remove-btn">×</button>
                        </div>
                    `;
                    userInput.placeholder = "Ask about this file...";
                }

                filePreviewContainer.querySelector('.file-remove-btn').addEventListener('click', () => {
                    attachedFile = null;
                    filePreviewContainer.classList.add('hidden');
                    filePreviewContainer.innerHTML = '';
                    fileAttachInput.value = '';
                    userInput.placeholder = "Message GlobleXGPT...";
                });

                userInput.focus();
            };

            if (isImage) {
                reader.readAsDataURL(file);
            } else {
                try {
                    reader.readAsText(file);
                } catch (err) {
                    // If can't read as text, read as data URL
                    reader.readAsDataURL(file);
                }
            }
        };

        fileAttachInput.addEventListener('change', (e) => {
            handleFileChange(e.target.files);
        });

        // drag and drop support
        const inputCapsule = document.querySelector('.input-bar-capsule');
        if (inputCapsule) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                inputCapsule.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                }, false);
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                inputCapsule.addEventListener(eventName, () => {
                    inputCapsule.classList.add('drag-active');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                inputCapsule.addEventListener(eventName, () => {
                    inputCapsule.classList.remove('drag-active');
                }, false);
            });

            inputCapsule.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                const files = dt.files;
                if (files && files.length > 0) {
                    handleFileChange(files);
                }
            });
        }
    }

    async function handleImageEnhance() {
        if (!attachedFile || !attachedFile.data || !attachedFile.type.startsWith('image/')) return;

        const enhanceBtn = document.getElementById('enhance-current-img');
        if (!enhanceBtn) return;

        const originalText = enhanceBtn.querySelector('span').innerText;
        enhanceBtn.querySelector('span').innerText = 'Enhancing...';
        enhanceBtn.classList.add('loading');
        enhanceBtn.disabled = true;

        try {
            const response = await fetch('/enhance_image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: attachedFile.data,
                    target_width: 2048,
                    target_height: 2048
                })
            });

            const data = await response.json();

            if (data.success && data.enhanced_image) {
                // Update attached file and preview
                attachedFile.data = data.enhanced_image;
                const img = filePreviewContainer.querySelector('img');
                if (img) img.src = data.enhanced_image;

                enhanceBtn.querySelector('span').innerText = 'Done!';
                setTimeout(() => {
                    if (enhanceBtn && enhanceBtn.querySelector('span')) {
                        enhanceBtn.querySelector('span').innerText = 'Enhance';
                    }
                }, 2000);
            } else {
                alert(data.error || 'Failed to enhance image');
                enhanceBtn.querySelector('span').innerText = originalText;
            }
        } catch (error) {
            console.error('Enhance error:', error);
            alert('Network error while enhancing image');
            enhanceBtn.querySelector('span').innerText = originalText;
        } finally {
            enhanceBtn.classList.remove('loading');
            enhanceBtn.disabled = false;
        }
    }




    // Auto-collapse sidebar on mobile
    if (window.innerWidth <= 768 && sidebarCloseBtn) {
        sidebarCloseBtn.click();
    }

    // --- Authentication Logic ---
    const authModal = document.getElementById('auth-modal');
    const closeAuthBtn = document.getElementById('close-auth-btn');
    const authMessage = document.getElementById('auth-message');
    const authLoading = document.getElementById('auth-loading');

    // Restored Manual Auth Elements
    const authForm = document.getElementById('auth-form');
    const authTitle = document.getElementById('auth-title');
    const authSubtitle = document.getElementById('auth-subtitle');
    const authSubmitBtn = document.getElementById('auth-submit-btn');
    const toggleAuthModeBtn = document.getElementById('toggle-auth-mode');
    const authSwitchText = document.getElementById('auth-switch-text');
    const nameGroup = document.getElementById('name-group');
    const avatarGroup = document.getElementById('avatar-group');
    const profilePicInput = document.getElementById('profile-pic');
    const avatarBase64Input = document.getElementById('avatar-base64');

    let isLoginMode = true;

    function openAuthModal() {
        authModal.classList.remove('hidden');
        if (authMessage) {
            authMessage.innerText = '';
            authMessage.className = 'auth-message';
        }
        // Reset Google Button if needed, or it stays rendered
    }

    function closeAuthModal() {
        authModal.classList.add('hidden');
    }

    // Google Sign-In Logic (called by index.html global handler)
    window.onGoogleLogin = async function (response) {
        if (response.credential) {
            if (authLoading) authLoading.style.display = 'block';

            try {
                const res = await fetch('/auth/google', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ credential: response.credential })
                });

                const data = await res.json();

                if (authLoading) authLoading.style.display = 'none';

                if (res.ok) {
                    console.log("Google Login Success:", data);
                    // Save user data
                    localStorage.setItem('user', JSON.stringify(data.user));
                    if (data.token) localStorage.setItem('auth_token', data.token);

                    updateUserInterface(data.user);
                    closeAuthModal();

                    // Sync Pro status
                    syncProStatusFromServer(data.user);

                    // Show success toast/message
                    const welcomeUser = document.getElementById('welcome-message');
                    if (welcomeUser) welcomeUser.innerText = `Welcome back, ${data.user.full_name.split(' ')[0]}`;
                } else {
                    if (authMessage) {
                        authMessage.innerText = data.error || 'Login failed';
                        authMessage.classList.add('error');
                    }
                }
            } catch (err) {
                console.error("Login Error:", err);
                if (authLoading) authLoading.style.display = 'none';
                if (authMessage) {
                    authMessage.innerText = 'Network error during login';
                    authMessage.classList.add('error');
                }
            }
        }
    };

    const authTriggerBtns = document.querySelectorAll('.user-profile, #sidebar-login-btn');

    const userMenu = document.getElementById('user-menu');
    const logoutBtn = document.getElementById('logout-btn');

    function verifyProExpiry() {
        try {
            const now = new Date();
            const proExpiry = localStorage.getItem('pro_expiry_at');

            // 1. Check Global Promo Code Expiry
            if (proExpiry) {
                if (now > new Date(proExpiry)) {
                    localStorage.removeItem('pro_unlocked');
                    localStorage.removeItem('pro_expiry_at');
                    console.log("[PRO] Global Pro status (promo code) has expired.");
                }
            }

            // 2. Check Individual Manual Upgrades Expiry
            let manualProData = {};
            try {
                manualProData = JSON.parse(localStorage.getItem('manual_pro_data') || '{}');
            } catch (e) {
                console.error("Error parsing manual_pro_data", e);
                manualProData = {};
            }

            let changed = false;
            for (const email in manualProData) {
                if (now > new Date(manualProData[email])) {
                    delete manualProData[email];
                    changed = true;
                    console.log(`[PRO] Pro status for ${email} has expired.`);
                }
            }
            if (changed) {
                localStorage.setItem('manual_pro_data', JSON.stringify(manualProData));
            }
        } catch (e) {
            console.error("verifyProExpiry failed", e);
        }
    }

    async function syncProStatusFromServer(user) {
        if (!user || !user.email) return;

        try {
            const response = await fetch('/check_pro_status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: user.email })
            });
            const data = await response.json();

            if (data.is_pro) {
                console.log("[PRO] Server confirmed Pro status for:", user.email);
                localStorage.setItem('local_server_pro', 'true');
                // Re-render UI to show pro badge
                updateUserInterface(user);
            } else {
                localStorage.removeItem('local_server_pro');
            }
        } catch (err) {
            console.error("[PRO] Error syncing pro status:", err);
        }
    }

    function updateUserInterface(user) {
        try {
            // Run expiry check whenever UI is updated
            verifyProExpiry();

            const promoUnlocked = localStorage.getItem('pro_unlocked') === 'true';
            const serverPro = localStorage.getItem('local_server_pro') === 'true';
            const userPlanPro = user && user.plan_type === 'Pro';

            // Safe JSON Parse logic
            let manualProEmails = [];
            try {
                manualProEmails = JSON.parse(localStorage.getItem('manual_pro_emails') || '[]');
            } catch (e) { manualProEmails = []; }

            let manualProData = {};
            try {
                manualProData = JSON.parse(localStorage.getItem('manual_pro_data') || '{}');
            } catch (e) { manualProData = {}; }

            const isEmailInManualList = user && Array.isArray(manualProEmails) && manualProEmails.includes(user.email);
            const isEmailInManualData = user && manualProData && manualProData[user.email];

            const isPro = user && (userPlanPro || promoUnlocked || isEmailInManualList || isEmailInManualData || serverPro);

            // Calculate remaining days for pro badge tooltip
            let proExpiryInfo = "";
            if (isPro) {
                if (isEmailInManualData) {
                    const days = Math.ceil((new Date(manualProData[user.email]) - new Date()) / (1000 * 60 * 60 * 24));
                    proExpiryInfo = `Pro Plan expires in ${days} days`;
                } else if (promoUnlocked && localStorage.getItem('pro_expiry_at')) {
                    const days = Math.ceil((new Date(localStorage.getItem('pro_expiry_at')) - new Date()) / (1000 * 60 * 60 * 24));
                    proExpiryInfo = `Promo valid for ${days} days`;
                } else if (serverPro || userPlanPro) {
                    proExpiryInfo = "Pro Sync: Active";
                }
            }

            // 1. Update Sidebar Button
            const sidebarLoginBtn = document.getElementById('sidebar-login-btn');
            if (sidebarLoginBtn) {
                sidebarLoginBtn.innerHTML = ''; // Clear content first

                if (user) {
                    // Show User Name (Used even for Pro as requested)
                    let displayName = user.full_name;
                    if (!displayName || displayName.trim() === "") {
                        // Fallback to email username if name is missing
                        if (user.email) {
                            displayName = user.email.split('@')[0];
                            // Capitalize first letter
                            displayName = displayName.charAt(0).toUpperCase() + displayName.slice(1);
                        } else {
                            displayName = "User";
                        }
                    }

                    // 1. Avatar
                    if (user.avatar_url && user.avatar_url.trim() !== "") {
                        const img = document.createElement('img');
                        img.className = 'user-avatar-tiny';
                        img.src = user.avatar_url;
                        img.alt = "User";
                        sidebarLoginBtn.appendChild(img);
                    } else {
                        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                        svg.setAttribute("viewBox", "0 0 24 24");
                        svg.setAttribute("stroke", "currentColor");
                        svg.setAttribute("stroke-width", "2");
                        svg.setAttribute("fill", "none");
                        svg.style.width = "18px";
                        svg.style.height = "18px";
                        svg.innerHTML = '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>';
                        sidebarLoginBtn.appendChild(svg);
                    }

                    // 2. Name
                    const span = document.createElement('span');
                    span.innerText = displayName;
                    sidebarLoginBtn.appendChild(span);

                    // 3. Pro Badge
                    if (isPro) {
                        const badge = document.createElement('span');
                        badge.className = 'pro-badge';
                        badge.innerText = 'PRO';
                        badge.style.background = 'linear-gradient(135deg, #FFD700, #FFA500)';
                        badge.style.color = '#000';
                        badge.style.fontSize = '10px';
                        badge.style.fontWeight = '800';
                        badge.style.padding = '2px 6px';
                        badge.style.borderRadius = '4px';
                        badge.style.marginLeft = '8px';
                        badge.style.boxShadow = '0 0 10px rgba(255, 215, 0, 0.3)';
                        if (proExpiryInfo) badge.title = proExpiryInfo;
                        sidebarLoginBtn.appendChild(badge);
                    }
                } else {
                    // Not Logged In
                    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                    svg.setAttribute("viewBox", "0 0 24 24");
                    svg.setAttribute("stroke", "currentColor");
                    svg.setAttribute("stroke-width", "2");
                    svg.setAttribute("fill", "none");
                    svg.innerHTML = '<path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />';
                    sidebarLoginBtn.appendChild(svg);

                    const span = document.createElement('span');
                    span.innerText = 'Log In';
                    sidebarLoginBtn.appendChild(span);
                }
            }

            // 2. Update Header Profile Button
            const headerProfileBtns = document.querySelectorAll('.user-profile');
            headerProfileBtns.forEach(btn => {
                const svg = btn.querySelector('svg');
                const img = btn.querySelector('img');

                if (user) {
                    // Add gold border for Pro users in header
                    if (isPro) {
                        btn.style.border = '2px solid #FFD700';
                        btn.style.boxShadow = '0 0 10px rgba(255, 215, 0, 0.4)';
                    } else {
                        btn.style.border = 'none';
                        btn.style.boxShadow = 'none';
                    }

                    if (user.avatar_url && user.avatar_url.length > 50) {
                        if (img) {
                            img.src = user.avatar_url;
                            img.style.display = 'block';
                            if (svg) svg.style.display = 'none';
                        } else {
                            const newImg = document.createElement('img');
                            newImg.style.width = '100%';
                            newImg.style.height = '100%';
                            newImg.style.borderRadius = '50%';
                            newImg.style.objectFit = 'cover';
                            newImg.src = user.avatar_url;
                            if (svg) svg.replaceWith(newImg);
                            else btn.appendChild(newImg);
                        }
                    } else {
                        if (img) img.style.display = 'none';
                        if (svg) svg.style.display = 'block';
                    }
                } else {
                    btn.style.border = 'none';
                    btn.style.boxShadow = 'none';
                    if (img) img.style.display = 'none';
                    if (svg) {
                        svg.style.display = 'block';
                        svg.setAttribute("fill", "currentColor");
                    }
                }
            });

            // 4. Update Upgrade Buttons & Brand Effects
            const headerProBtn = document.getElementById('header-pro-btn');
            const proPlanBtn = document.getElementById('pro-plan-btn');
            const brandDropdown = document.querySelector('.brand-dropdown');
            const topBar = document.querySelector('.top-bar');

            if (headerProBtn) {
                const btnTextLong = headerProBtn.querySelector('.pro-btn-text');
                const btnTextShort = headerProBtn.querySelector('.pro-btn-text-short');

                if (isPro) {
                    // Update text to "Pro" for Pro users
                    if (btnTextLong) btnTextLong.innerText = 'Pro Plan';
                    if (btnTextShort) btnTextShort.innerText = 'Pro';

                    if (headerProBtn) {
                        headerProBtn.style.display = 'flex';
                        headerProBtn.classList.add('pro-status-mode'); // Disable pulsing in CSS
                        headerProBtn.title = 'Active Pro Plan';
                    }

                    // Add premium effects
                    if (brandDropdown) brandDropdown.classList.add('pro-brand-effect');
                    if (topBar) topBar.classList.add('pro-header-glow');
                } else {
                    // Return to "Upgrade" for free users
                    if (btnTextLong) btnTextLong.innerText = 'Upgrade to Pro';
                    if (btnTextShort) btnTextShort.innerText = 'Upgrade Now';

                    headerProBtn.style.display = 'flex';
                    headerProBtn.classList.remove('pro-status-mode');
                    headerProBtn.title = 'Upgrade to Pro';

                    // Remove premium effects
                    if (brandDropdown) brandDropdown.classList.remove('pro-brand-effect');
                    if (topBar) topBar.classList.remove('pro-header-glow');
                }
            }

            if (proPlanBtn) {
                // In the menu, we can hide it if Pro, or change text. User said "not show free user pro"
                // Let's keep hiding it in the sidebar menu to avoid clutter if they are already Pro.
                proPlanBtn.style.display = isPro ? 'none' : 'flex';
            }

            // 3. Update Welcome Screen
            const welcomeMessage = document.getElementById('welcome-message');
            const welcomeAvatar = document.getElementById('welcome-avatar');

            if (welcomeMessage) {
                if (isPro) {
                    // Pro User: Show "GlobleXGPT Pro" and HIDE avatar
                    welcomeMessage.innerHTML = '<div style="display: flex; flex-direction: column; align-items: center; line-height: 1.2;"><span class="welcome-pro-text" style="background: linear-gradient(135deg, #FFD700, #FFA500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem; font-weight: 800; display: inline-flex; align-items: center; gap: 2px;">Globle<span style="-webkit-text-fill-color: initial; color: #FFD700; filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.5)); transform: translateY(-2px); font-size: 1.1em;">★</span>GPT</span><span style="font-size: 1.5rem; font-weight: 600; color: #FFD700; letter-spacing: 4px; text-transform: uppercase; margin-top: 5px; text-shadow: 0 2px 10px rgba(255, 215, 0, 0.3);">Pro</span></div>';
                    if (welcomeAvatar) welcomeAvatar.style.display = 'none';
                } else if (user) {
                    // Free User: Show "Welcome back, Name" and SHOW avatar
                    const name = user.full_name || "User";
                    welcomeMessage.innerHTML = `Welcome back, ${name}`;

                    if (welcomeAvatar) {
                        if (user.avatar_url && user.avatar_url.length > 50) {
                            welcomeAvatar.style.display = 'block';
                            welcomeAvatar.querySelector('img').src = user.avatar_url;
                            welcomeAvatar.classList.remove('pro-border-rainbow');
                        } else {
                            welcomeAvatar.style.display = 'none';
                        }
                    }
                } else {
                    // Not Logged In
                    if (welcomeMessage) welcomeMessage.innerText = 'Where should we begin?';
                    if (welcomeAvatar) {
                        welcomeAvatar.style.display = 'none';
                        welcomeAvatar.classList.remove('pro-border-rainbow');
                    }

                    // Show Upgrade banner for guests
                    const guestBanner = document.getElementById('guest-upgrade-banner');
                    if (guestBanner) guestBanner.style.display = 'block';
                }
            }

            // If user logged in, hide guest banner
            const guestBanner = document.getElementById('guest-upgrade-banner');
            if (guestBanner && user) guestBanner.style.display = 'none';
            // 4. Update Settings Button Visibility
            const settingsTrigger = document.getElementById('settings-trigger');
            if (settingsTrigger) {
                settingsTrigger.style.display = user ? 'flex' : 'none';
            }
        } catch (globalError) {
            console.error("Critical error in updateUserInterface:", globalError);
        }
    }


    // Check login state on load
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
        try {
            const user = JSON.parse(storedUser);
            updateUserInterface(user);
            // Verify Pro with server on load
            syncProStatusFromServer(user);
        } catch (e) {
            console.error("Error parsing user data, clearing storage", e);
            localStorage.removeItem('user');
        }
    }

    const settingsTrigger = document.getElementById('settings-trigger');
    if (settingsTrigger) {
        settingsTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            if (userMenu) {
                const isVisible = userMenu.style.display === 'block';
                userMenu.style.display = isVisible ? 'none' : 'block';
            }
        });
    }

    if (authTriggerBtns.length > 0) {
        authTriggerBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Special handling for sidebar login button
                const isSidebarBtn = btn.id === 'sidebar-login-btn';
                const currentUserJson = localStorage.getItem('user');
                let currentUser = null;
                try {
                    currentUser = currentUserJson ? JSON.parse(currentUserJson) : null;
                } catch (e) {
                    console.error("Invalid user data in click handler", e);
                    localStorage.removeItem('user');
                }

                if (currentUser) {
                    // Mobile fix: If sidebar is collapsed and user clicks top profile, open sidebar
                    // But if checking sidebar button itself, we don't need to force toggle if it's already visible enough to click
                    if (window.innerWidth <= 768 && sidebar.classList.contains('collapsed') && !isSidebarBtn) {
                        toggleSidebar(true);
                    }

                    // Toggle User Menu for both sidebar and header profile buttons
                    if (userMenu) {
                        const isVisible = userMenu.style.display === 'block';
                        userMenu.style.display = isVisible ? 'none' : 'block';
                    }
                } else {
                    openAuthModal();
                }
            });
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            updateUserInterface(null);
            if (userMenu) userMenu.style.display = 'none';
        });
    }

    // Change Name Logic
    const changeNameBtn = document.getElementById('change-name-btn');
    if (changeNameBtn) {
        changeNameBtn.addEventListener('click', () => {
            if (userMenu) userMenu.style.display = 'none';

            const storedUser = localStorage.getItem('user');
            if (!storedUser) return;

            const user = JSON.parse(storedUser);
            const currentName = user.full_name || "User";
            const newName = prompt("Enter your new name:", currentName);

            if (newName && newName.trim() !== "" && newName !== currentName) {
                const updatedName = newName.trim();

                // Update Local UI Immediately
                user.full_name = updatedName;
                localStorage.setItem('user', JSON.stringify(user));
                updateUserInterface(user);

                // Send to Backend
                fetch('/update_profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: user.id,
                        email: user.email,
                        full_name: updatedName
                    })
                })
                    .then(res => res.json())
                    .then(data => {
                        console.log("Name updated on server:", data);
                    })
                    .catch(err => console.error("Error updating name:", err));
            }
        });
    }

    // Change Avatar Logic
    const changeAvatarBtn = document.getElementById('change-avatar-btn');
    const updateAvatarInput = document.getElementById('update-avatar-input');

    if (changeAvatarBtn && updateAvatarInput) {
        changeAvatarBtn.addEventListener('click', () => {
            updateAvatarInput.click();
            // Close menu
            if (userMenu) userMenu.style.display = 'none';
        });

        updateAvatarInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function (event) {
                const img = new Image();
                img.onload = function () {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');

                    // Resize to thumbnail
                    const MAX_SIZE = 150; // Increased resolution slightly
                    let sourceX, sourceY, sourceWidth, sourceHeight;

                    // Calculate crop
                    if (img.width > img.height) {
                        sourceHeight = img.height;
                        sourceWidth = img.height;
                        sourceX = (img.width - img.height) / 2;
                        sourceY = 0;
                    } else {
                        sourceWidth = img.width;
                        sourceHeight = img.width;
                        sourceX = 0;
                        sourceY = (img.height - img.width) / 2;
                    }

                    canvas.width = MAX_SIZE;
                    canvas.height = MAX_SIZE;

                    // Draw cut
                    ctx.drawImage(img, sourceX, sourceY, sourceWidth, sourceHeight, 0, 0, MAX_SIZE, MAX_SIZE);

                    const dataUrl = canvas.toDataURL('image/jpeg', 0.7);

                    // Update Local UI
                    const storedUser = localStorage.getItem('user');
                    if (storedUser) {
                        const user = JSON.parse(storedUser);
                        user.avatar_url = dataUrl;
                        localStorage.setItem('user', JSON.stringify(user));
                        updateUserInterface(user);

                        // Send to Backend
                        fetch('/update_profile', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                user_id: user.id,
                                email: user.email,
                                avatar_url: dataUrl
                            })
                        }).catch(err => console.error("Error updating profile:", err));
                    }
                };
                img.src = event.target.result;
            };
            reader.readAsDataURL(file);
        });
    }

    // Theme Toggle Logic
    const themeToggleBtn = document.getElementById('theme-toggle-btn');

    function applyTheme(isLight) {
        const hljsTheme = document.getElementById('hljs-theme');
        if (isLight) {
            document.body.classList.add('light-mode');
            if (hljsTheme) hljsTheme.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css';
            if (themeToggleBtn) {
                themeToggleBtn.querySelector('span').innerText = 'Dark Mode';
                // Optionally update icon here if you want to swap sun/moon
            }
        } else {
            document.body.classList.remove('light-mode');
            if (hljsTheme) hljsTheme.href = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css';
            if (themeToggleBtn) {
                themeToggleBtn.querySelector('span').innerText = 'Light Mode';
            }
        }
    }

    // Check saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        applyTheme(true);
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const isLight = document.body.classList.toggle('light-mode');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');
            applyTheme(isLight);
            // Close menu
            if (userMenu) userMenu.style.display = 'none';
        });
    }

    // Close menu when clicking outside
    window.addEventListener('click', (e) => {
        // If click is NOT inside sidebar footer or button
        if (!e.target.closest('.sidebar-footer') && userMenu && userMenu.style.display === 'block') {
            userMenu.style.display = 'none';
        }
    });

    if (closeAuthBtn) {
        closeAuthBtn.addEventListener('click', closeAuthModal);
    }

    // Close on click outside
    window.addEventListener('click', (e) => {
        if (e.target === authModal) {
            closeAuthModal();
        }
    });

    // Restored Manual Auth Listeners
    if (toggleAuthModeBtn) {
        toggleAuthModeBtn.addEventListener('click', () => {
            isLoginMode = !isLoginMode;
            if (isLoginMode) {
                if (authTitle) authTitle.innerText = 'Welcome Back';
                if (authSubtitle) authSubtitle.innerText = 'Sign in to continue to GlobleXGPT';
                if (authSubmitBtn) authSubmitBtn.innerText = 'Sign In';
                if (toggleAuthModeBtn) toggleAuthModeBtn.innerText = 'Sign up';
                if (authSwitchText && authSwitchText.firstChild) authSwitchText.firstChild.textContent = "Don't have an account? ";
                if (nameGroup) nameGroup.style.display = 'none';
                if (avatarGroup) avatarGroup.style.display = 'none';
                const fnInput = document.getElementById('full-name');
                if (fnInput) fnInput.removeAttribute('required');
            } else {
                if (authTitle) authTitle.innerText = 'Create Account';
                if (authSubtitle) authSubtitle.innerText = 'Join GlobleXGPT today';
                if (authSubmitBtn) authSubmitBtn.innerText = 'Sign Up';
                if (toggleAuthModeBtn) toggleAuthModeBtn.innerText = 'Sign in';
                if (authSwitchText && authSwitchText.firstChild) authSwitchText.firstChild.textContent = "Already have an account? ";
                if (nameGroup) nameGroup.style.display = 'flex';
                if (avatarGroup) {
                    avatarGroup.style.display = 'flex';
                    avatarGroup.style.flexDirection = 'column';
                }
                const fnInput = document.getElementById('full-name');
                if (fnInput) fnInput.setAttribute('required', 'true');
            }
        });
    }

    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const fullName = document.getElementById('full-name').value;
            const avatarUrl = document.getElementById('avatar-base64') ? document.getElementById('avatar-base64').value : "";

            authSubmitBtn.disabled = true;
            authSubmitBtn.innerText = 'Processing...';
            // authMessage.innerText = 'Processing...'; // Don't show confusing message
            authMessage.className = 'auth-message';

            const endpoint = isLoginMode ? '/login' : '/signup';
            const payload = { email, password };
            if (!isLoginMode) {
                payload.full_name = fullName;
                payload.avatar_url = avatarUrl;
            }

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (response.ok) {
                    authMessage.innerText = data.message || 'Success!';
                    authMessage.className = 'auth-message success';

                    // Store token and user (local DB returns similar structure)
                    if (data.user) {
                        if (data.access_token) localStorage.setItem('access_token', data.access_token);
                        localStorage.setItem('user', JSON.stringify(data.user));
                        syncProStatusFromServer(data.user);
                        updateUserInterface(data.user);

                        setTimeout(() => {
                            closeAuthModal();
                        }, 1000);
                    }
                } else {
                    authMessage.innerText = data.error || 'An error occurred';
                    authMessage.className = 'auth-message error';
                }
            } catch (err) {
                authMessage.innerText = 'Network connection error.';
                authMessage.className = 'auth-message error';
                console.error(err);
            } finally {
                authSubmitBtn.disabled = false;
                authSubmitBtn.innerText = isLoginMode ? 'Sign In' : 'Sign Up';
            }
        });
    }

    // --- Pro Plan Modal Logic ---
    const proModal = document.getElementById('pro-modal');
    const proPlanBtn = document.getElementById('pro-plan-btn');
    const closeProBtn = document.getElementById('close-pro-btn');
    const applyPromoBtn = document.getElementById('apply-promo-btn');
    const promoCodeInput = document.getElementById('promo-code');
    const proMessage = document.getElementById('pro-message');

    if (proPlanBtn) {
        proPlanBtn.addEventListener('click', () => {
            if (userMenu) userMenu.style.display = 'none';
            proModal.classList.remove('hidden');
            if (proMessage) {
                proMessage.innerText = '';
                proMessage.className = 'auth-message';
            }
        });
    }

    // Header Pro button (always visible)
    const headerProBtn = document.getElementById('header-pro-btn');
    if (headerProBtn) {
        headerProBtn.addEventListener('click', () => {
            proModal.classList.remove('hidden');
            if (proMessage) {
                proMessage.innerText = '';
                proMessage.className = 'auth-message';
            }
        });
    }

    if (closeProBtn) {
        closeProBtn.addEventListener('click', () => {
            proModal.classList.add('hidden');
        });
    }

    window.addEventListener('click', (e) => {
        if (e.target === proModal) {
            proModal.classList.add('hidden');
        }
    });


    // --- Promo Code System with Admin Control ---
    const ADMIN_SECRET_CODE = 'Abinav_9009';

    // Initialize default promo code if not set
    if (!localStorage.getItem('active_promo_code')) {
        localStorage.setItem('active_promo_code', 'HimanshuFree');
    }

    if (applyPromoBtn) {
        applyPromoBtn.addEventListener('click', async () => {
            const code = promoCodeInput.value.trim();
            const storedUser = localStorage.getItem('user');

            if (!storedUser) {
                if (proMessage) {
                    proMessage.innerText = 'Please log in to use a promo code.';
                    proMessage.className = 'auth-message error';
                }
                return;
            }

            const user = JSON.parse(storedUser);

            if (!code) {
                if (proMessage) {
                    proMessage.innerText = 'Please enter a promo code.';
                    proMessage.className = 'auth-message error';
                }
                return;
            }

            // Apply valid promo code via backend
            try {
                const response = await fetch('/verify_promo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: code, email: user.email })
                });

                const data = await response.json();

                if (response.ok) {
                    if (proMessage) {
                        proMessage.innerText = 'Success! You are now a PRO member.';
                        proMessage.className = 'auth-message success';
                    }

                    // Update Local Storage Logic for immediate UI feedback
                    localStorage.setItem('pro_unlocked', 'true');
                    const expiryDate = new Date();
                    expiryDate.setDate(expiryDate.getDate() + 30);
                    localStorage.setItem('pro_expiry_at', expiryDate.toISOString());

                    // Refresh UI
                    updateUserInterface(user);

                    setTimeout(() => {
                        proModal.classList.add('hidden');
                    }, 2000);
                } else {
                    if (proMessage) {
                        proMessage.innerText = data.error || 'Invalid promo code.';
                        proMessage.className = 'auth-message error';
                    }
                }
            } catch (err) {
                console.error("Promo Error:", err);
                if (proMessage) {
                    proMessage.innerText = 'Server error. Please try again.';
                    proMessage.className = 'auth-message error';
                }
            }
        });
    }

    // --- Admin: Update Promo Code ---
    const updatePromoBtn = document.getElementById('update-promo-btn');
    const secretCodeInput = document.getElementById('secret-code');
    const newPromoCodeInput = document.getElementById('new-promo-code');
    const adminMessage = document.getElementById('admin-message');

    if (updatePromoBtn) {
        updatePromoBtn.addEventListener('click', async () => {
            const secretCode = secretCodeInput.value.trim();
            const newPromoCode = newPromoCodeInput.value.trim();

            // Clear previous messages
            if (adminMessage) {
                adminMessage.innerText = '';
                adminMessage.className = 'auth-message';
            }

            // Validation
            if (!secretCode || !newPromoCode) {
                if (adminMessage) {
                    adminMessage.innerText = 'Please fill in both fields.';
                    adminMessage.className = 'auth-message error';
                }
                return;
            }

            // Backend Call
            try {
                const response = await fetch('/admin/update_promo', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ secret: secretCode, new_code: newPromoCode })
                });

                const data = await response.json();

                if (response.ok) {
                    if (adminMessage) {
                        adminMessage.innerText = `✅ Success: ${data.message}`;
                        adminMessage.className = 'auth-message success';
                    }
                    // Clear form
                    secretCodeInput.value = '';
                    newPromoCodeInput.value = '';
                } else {
                    if (adminMessage) {
                        adminMessage.innerText = `❌ Error: ${data.error}`;
                        adminMessage.className = 'auth-message error';
                    }
                }
            } catch (err) {
                if (adminMessage) {
                    adminMessage.innerText = 'Network error during update.';
                    adminMessage.className = 'auth-message error';
                }
            }
        });
    }

    // --- Admin: Upgrade Specific User (Manual Paid Upgrade) ---
    const upgradeUserBtn = document.getElementById('upgrade-user-btn');
    const upgradeUserEmailInput = document.getElementById('upgrade-user-email');

    if (upgradeUserBtn) {
        upgradeUserBtn.addEventListener('click', () => {
            const secretCode = secretCodeInput.value.trim();
            const userEmail = upgradeUserEmailInput.value.trim();

            if (!secretCode || !userEmail) {
                if (adminMessage) {
                    adminMessage.innerText = 'Please enter secret code and user email.';
                    adminMessage.className = 'auth-message error';
                }
                return;
            }

            if (secretCode !== ADMIN_SECRET_CODE) {
                if (adminMessage) {
                    adminMessage.innerText = '❌ Invalid secret code.';
                    adminMessage.className = 'auth-message error';
                }
                if (secretCodeInput) secretCodeInput.value = '';
                return;
            }

            // Expiry date (30 days from now)
            const expiryDate = new Date();
            expiryDate.setDate(expiryDate.getDate() + 30);

            // Store in manual_pro_data
            const manualProData = JSON.parse(localStorage.getItem('manual_pro_data') || '{}');
            manualProData[userEmail] = expiryDate.toISOString();
            localStorage.setItem('manual_pro_data', JSON.stringify(manualProData));

            // Sync to Google Sheets via backend
            fetch('/admin_upgrade_user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    secret_code: secretCode,
                    email: userEmail
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (adminMessage) {
                        adminMessage.innerText = `✅ Success: ${data.message}`;
                        adminMessage.className = 'auth-message success';
                    }
                    console.log("[ADMIN] Google Sheets sync:", data.message);
                })
                .catch(err => {
                    if (adminMessage) {
                        adminMessage.innerText = `✅ User upgraded locally, but server sync failed.`;
                        adminMessage.className = 'auth-message warning';
                    }
                    console.error("[ADMIN] Sync error:", err);
                });

            // Clear input
            upgradeUserEmailInput.value = '';
            secretCodeInput.value = '';

            // Update UI if the current user is the one upgraded
            const storedUser = localStorage.getItem('user');
            if (storedUser) {
                const user = JSON.parse(storedUser);
                updateUserInterface(user);
            }

            console.log(`[ADMIN] User ${userEmail} manually upgraded until ${expiryDate.toLocaleDateString()}`);
        });
    }


    // --- Payment Screenshot Preview ---
    const paymentScreenshotInput = document.getElementById('payment-screenshot');
    const screenshotPreview = document.getElementById('screenshot-preview');
    let paymentScreenshotData = null;

    if (paymentScreenshotInput) {
        paymentScreenshotInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    paymentScreenshotData = event.target.result;
                    screenshotPreview.style.display = 'block';
                    screenshotPreview.querySelector('img').src = event.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // --- Submit Payment Details ---
    const submitPaymentBtn = document.getElementById('submit-payment-btn');
    if (submitPaymentBtn) {
        submitPaymentBtn.addEventListener('click', async () => {
            const name = document.getElementById('pro-name').value.trim();
            const phone = document.getElementById('pro-phone').value.trim();
            const email = document.getElementById('pro-email').value.trim();

            // Validation
            if (!name || !phone || !email) {
                proMessage.innerText = 'Please fill in all required fields.';
                proMessage.className = 'auth-message error';
                return;
            }

            if (!paymentScreenshotData) {
                proMessage.innerText = 'Please upload a payment screenshot.';
                proMessage.className = 'auth-message error';
                return;
            }

            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                proMessage.innerText = 'Please enter a valid email address.';
                proMessage.className = 'auth-message error';
                return;
            }

            // Phone validation (basic)
            const phoneRegex = /^[\d\s\+\-\(\)]+$/;
            if (!phoneRegex.test(phone) || phone.length < 10) {
                proMessage.innerText = 'Please enter a valid phone number.';
                proMessage.className = 'auth-message error';
                return;
            }

            // Show loading state
            submitPaymentBtn.disabled = true;
            submitPaymentBtn.innerText = 'Submitting...';
            proMessage.innerText = 'Processing your payment details...';
            proMessage.className = 'auth-message';

            try {
                const response = await fetch('/submit_payment', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: name,
                        phone: phone,
                        email: email,
                        screenshot: paymentScreenshotData,
                        amount: '₹90',
                        timestamp: new Date().toISOString()
                    })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    proMessage.innerText = 'Payment details submitted successfully! You will be contacted shortly.';
                    proMessage.className = 'auth-message success';

                    // Clear form
                    document.getElementById('pro-name').value = '';
                    document.getElementById('pro-phone').value = '';
                    document.getElementById('pro-email').value = '';
                    paymentScreenshotInput.value = '';
                    screenshotPreview.style.display = 'none';
                    paymentScreenshotData = null;

                    // Close modal after 3 seconds
                    setTimeout(() => {
                        proModal.classList.add('hidden');
                    }, 3000);
                } else {
                    proMessage.innerText = data.error || 'Failed to submit payment details. Please try again.';
                    proMessage.className = 'auth-message error';
                }
            } catch (error) {
                console.error('Payment submission error:', error);
                proMessage.innerText = 'Network error. Please check your connection and try again.';
                proMessage.className = 'auth-message error';
            } finally {
                submitPaymentBtn.disabled = false;
                submitPaymentBtn.innerText = 'Submit Payment Details';
            }
        });
    }

    // --- Download App Modal Logic ---
    const downloadModal = document.getElementById('download-modal');
    const downloadAppBtn = document.getElementById('download-app-btn');
    const closeDownloadBtn = document.getElementById('close-download-btn');
    const downloadCards = document.querySelectorAll('.download-card');

    if (downloadAppBtn) {
        downloadAppBtn.addEventListener('click', () => {
            if (userMenu) userMenu.style.display = 'none';
            downloadModal.classList.remove('hidden');
        });
    }

    if (closeDownloadBtn) {
        closeDownloadBtn.addEventListener('click', () => {
            downloadModal.classList.add('hidden');
        });
    }

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === downloadModal) {
            downloadModal.classList.add('hidden');
        }
    });

    // Handle download clicks
    if (downloadCards.length > 0) {
        downloadCards.forEach(card => {
            card.addEventListener('click', async (e) => {
                e.preventDefault();
                const platform = card.getAttribute('data-platform');

                // Special handling for Web App (PWA)
                if (platform === 'web') {
                    alert('To install GlobleXGPT as a web app:\n\n1. Click the menu button (⋮) in your browser\n2. Select "Install GlobleXGPT" or "Add to Home Screen"\n3. Follow the prompts to install');
                    return;
                }

                // For other platforms, attempt download
                try {
                    const response = await fetch(`/download/${platform}`);

                    if (response.ok) {
                        // Check if it's a file download or JSON response
                        const contentType = response.headers.get('content-type');

                        if (contentType && contentType.includes('application/json')) {
                            const data = await response.json();
                            alert(data.message || `Download for ${platform} is not available yet.`);
                        } else {
                            // Trigger file download
                            const blob = await response.blob();
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;

                            // Map extensions correctly
                            const extensions = {
                                'windows': '.zip',
                                'mac': '.dmg',
                                'android': '.apk',
                                'linux': '.AppImage',
                                'ios': '.ipa'
                            };
                            const ext = extensions[platform] || '';
                            a.download = `GlobleXGPT-${platform}${ext}`;

                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                            document.body.removeChild(a);

                            // Show success message
                            alert(`Download started for ${platform}!\n\nCheck your downloads folder.`);
                        }
                    } else {
                        const data = await response.json();
                        alert(data.message || `Download for ${platform} is currently unavailable.`);
                    }
                } catch (error) {
                    console.error('Download error:', error);
                    alert(`Unable to download for ${platform}.\n\nPlease contact support for assistance.`);
                }
            });
        });
    }
    // --- Razorpay Payment System ---
    async function initiateRazorpayPayment() {
        const user = JSON.parse(localStorage.getItem('user'));
        if (!user) {
            // Close pro modal first
            const proModal = document.getElementById('pro-modal');
            if (proModal) proModal.classList.add('hidden');

            // Show auth modal with helpful message
            const authMessage = document.getElementById('auth-message');
            if (authMessage) {
                authMessage.innerText = 'Please sign in or create an account to upgrade to PRO.';
                authMessage.className = 'auth-message info';
            }
            openAuthModal();
            return;
        }

        try {
            // 1. Create Order on Backend
            const orderResponse = await fetch('/create_payment_order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    amount: 9000,
                    email: user.email,
                    name: user.full_name || 'User'
                })
            });

            const orderData = await orderResponse.json();
            if (orderData.error) throw new Error(orderData.error);

            // 2. Open Razorpay Checkout
            const options = {
                "key": window.RAZORPAY_KEY_ID || "YOUR_RAZORPAY_KEY_ID",
                "amount": orderData.amount,
                "currency": "INR",
                "name": "GlobleXGPT Pro",
                "description": "Premium AI Plan",
                "order_id": orderData.order_id,
                "handler": async function (response) {
                    // 3. Verify Payment on Backend
                    const verifyResponse = await fetch('/verify_payment', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            razorpay_order_id: response.razorpay_order_id,
                            razorpay_payment_id: response.razorpay_payment_id,
                            razorpay_signature: response.razorpay_signature,
                            email: user.email,
                            name: user.full_name || 'User',
                            amount: 90
                        })
                    });

                    const verifyData = await verifyResponse.json();
                    if (verifyData.success) {
                        alert('Congratulations! You are now a PRO member.');
                        // Update local state and UI
                        user.plan_type = 'Pro';
                        localStorage.setItem('user', JSON.stringify(user));
                        localStorage.setItem('pro_unlocked', 'true');
                        updateUserInterface(user);
                    } else {
                        alert('Payment verification failed: ' + verifyData.error);
                    }
                },
                "prefill": {
                    "name": user.full_name,
                    "email": user.email
                },
                "theme": { "color": "#AB68FF" }
            };

            const rzp = new Razorpay(options);
            rzp.open();

        } catch (error) {
            console.error('Payment error:', error);
            alert('Could not initiate payment: ' + error.message);
        }
    }

    // Export to global scope for the button
    window.buyProPlan = initiateRazorpayPayment;

    // --- Dynamic UI Updates for PRO Status ---
    // [Duplicate updateUserInterface removed to use the main implementation]

    // Initialize UI
    // const savedUser = JSON.parse(localStorage.getItem('user'));
    // if (savedUser) updateUserInterface(savedUser); // Already handled above in DOMContentLoaded

    // Ensure Logout Logic handles clearing all pro flags
    if (logoutBtn) {
        logoutBtn.onclick = function () {
            localStorage.removeItem('user');
            localStorage.removeItem('auth_token');
            localStorage.removeItem('local_server_pro');
            localStorage.removeItem('pro_unlocked');
            localStorage.removeItem('pro_expiry_at');
            window.location.reload();
        };
    }
});
