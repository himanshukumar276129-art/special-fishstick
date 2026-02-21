class VoiceAssistant {
    constructor(callbacks) {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isRecording = false;
        this.shouldRestart = false;
        this.callbacks = callbacks || {};
        this.voices = [];
        this.currentUtterance = null;

        // Bind methods
        this.toggle = this.toggle.bind(this);
        this.start = this.start.bind(this);
        this.stop = this.stop.bind(this);
        this.speak = this.speak.bind(this);
        this.cleanText = this.cleanText.bind(this);

        this.initRecognition();
        this.initSynthesis();
    }

    initRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.error("VoiceAssistant: Speech Recognition API not supported.");
            if (this.callbacks.onError) this.callbacks.onError("Speech recognition not supported in this browser.");
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            console.log("VoiceAssistant: Recognition started");
            this.isRecording = true;
            if (this.callbacks.onStart) this.callbacks.onStart();
        };

        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            if (finalTranscript) {
                console.log("VoiceAssistant: Final Transcript received:", finalTranscript);
                if (this.callbacks.onResult) {
                    this.callbacks.onResult(finalTranscript.trim());
                }

                // Stop after final result to process command
                this.stop();
            } else if (interimTranscript) {
                if (this.callbacks.onInterim) {
                    this.callbacks.onInterim(interimTranscript);
                }
            }
        };

        this.recognition.onerror = (event) => {
            if (event.error === 'no-speech' || event.error === 'aborted') {
                return;
            }
            console.error("VoiceAssistant Recognition Error:", event.error);
            this.isRecording = false;
            if (this.callbacks.onError) this.callbacks.onError(event.error);
        };

        this.recognition.onend = () => {
            console.log("VoiceAssistant: Recognition ended");
            this.isRecording = false;
            if (this.shouldRestart) {
                this.start();
            } else {
                if (this.callbacks.onEnd) this.callbacks.onEnd();
            }
        };
    }

    initSynthesis() {
        if (!this.synthesis) {
            console.warn("VoiceAssistant: Text-to-Speech not supported.");
            return;
        }

        const loadVoices = () => {
            this.voices = this.synthesis.getVoices();
            if (this.voices.length > 0) {
                console.log(`VoiceAssistant: Found ${this.voices.length} voices.`);
            }
        };

        loadVoices();
        if (this.synthesis.onvoiceschanged !== undefined) {
            this.synthesis.onvoiceschanged = loadVoices;
        }
    }

    cleanText(text) {
        if (!text) return "";
        // Remove accidental JSON fragments/metadata leaks
        text = text.replace(/\{"response":\s*"|"?,?\s*"emotion":\s*"[^"]*"\s*\}+$/gi, '');

        // Remove markdown formatting and improve flow for better speech
        return text
            .replace(/\*\*(.*?)\*\*/g, '$1') // Bold
            .replace(/\*(.*?)\*/g, '$1')     // Italic
            .replace(/`(.*?)`/g, '$1')       // Code
            .replace(/#+\s+(.*?)\n/g, '$1. ') // Headers as sentences
            .replace(/\[(.*?)\]\((.*?)\)/g, '$1') // Links
            .replace(/\n+/g, ' ')            // Newlines to spaces
            .replace(/- /g, '')              // List dashes
            .replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '') // Remove Emojis
            .replace(/:\)/g, 'smiling face')
            .replace(/:\(/g, 'sad face')
            .replace(/ {2,}/g, ' ')          // Collapse spaces
            .trim();
    }

    toggle() {
        if (this.isRecording) {
            this.stop();
        } else {
            this.start();
        }
    }

    start() {
        if (!this.recognition) return;
        if (this.isRecording) return;

        try {
            this.shouldRestart = false;
            this.recognition.start();
        } catch (e) {
            console.error("VoiceAssistant: Failed to start recognition:", e);
        }
    }

    stop() {
        if (!this.recognition) return;
        this.shouldRestart = false;
        try {
            this.recognition.stop();
        } catch (e) {
            // Silently fail if already stopped
        }
    }

    speak(text) {
        if (!this.synthesis) {
            console.error("VoiceAssistant: Synthesis not available");
            return;
        }

        // Cancel any ongoing speech
        this.synthesis.cancel();

        if (!text) {
            console.warn("VoiceAssistant: No text to speak");
            return;
        }

        const cleanedText = this.cleanText(text);
        console.log("VoiceAssistant: Preparing to speak:", cleanedText.substring(0, 50) + "...");

        const utterance = new SpeechSynthesisUtterance(cleanedText);

        // Ensure voices are loaded
        if (this.voices.length === 0) {
            this.voices = this.synthesis.getVoices();
        }

        const preferredEnglishVoices = [
            'Microsoft Aria Online (Natural)',
            'Microsoft Jenny Online (Natural)',
            'Google US English',
            'Google UK English Female',
            'Google English (India)',
            'Microsoft Neerja Online (Natural)',
            'Samantha',
            'Microsoft Zira'
        ];

        const preferredHindiVoices = [
            'Microsoft Swara Online (Natural)',
            'Google Hindi',
            'Microsoft Madhur Online (Natural)',
            'hi-IN',
            'Hindi India'
        ];

        // Simple check: if text contains Hindi characters, use Hindi voice
        const isHindi = /[\u0900-\u097F]/.test(cleanedText);
        let selectedVoice = null;

        if (isHindi) {
            console.log("🇮🇳 Hindi text detected, searching for Hindi voice...");
            for (const name of preferredHindiVoices) {
                selectedVoice = this.voices.find(v => v.name.includes(name) || v.lang.includes('hi-IN'));
                if (selectedVoice) break;
            }
            utterance.lang = 'hi-IN';
        } else {
            // Try to find the best English voice
            for (const name of preferredEnglishVoices) {
                selectedVoice = this.voices.find(v => v.name.includes(name));
                if (selectedVoice) break;
            }
            utterance.lang = 'en-US';
        }

        // Fallback: search for any "Natural" or "Female" voice if still no match
        if (!selectedVoice) {
            selectedVoice = this.voices.find(v =>
                (v.lang.startsWith('en') || v.lang.startsWith('hi')) &&
                (v.name.includes('Natural') || v.name.includes('Online') || v.name.includes('Female'))
            );
        }

        if (!selectedVoice) {
            selectedVoice = this.voices.find(v => v.lang.startsWith(isHindi ? 'hi' : 'en'));
        }

        if (selectedVoice) {
            utterance.voice = selectedVoice;
            console.log(`✅ VoiceAssistant: Using ${isHindi ? 'Hindi' : 'English'} voice:`, selectedVoice.name);
        } else {
            console.warn("VoiceAssistant: No matching voice found, using default");
        }

        // Smooth and pleasant voice settings
        if (isHindi) {
            utterance.rate = 0.9;  // Hindi sounds better slightly slower
            utterance.pitch = 1.0; // Keep natural pitch for Hindi
        } else {
            utterance.rate = 0.95;
            utterance.pitch = 1.15;
        }
        utterance.volume = 1.0;

        utterance.onstart = () => {
            console.log("VoiceAssistant: Speaking started...");
        };

        utterance.onend = () => {
            console.log("VoiceAssistant: Speaking finished.");
            this.currentUtterance = null;
        };

        utterance.onerror = (e) => {
            console.error("VoiceAssistant: Synthesis Error:", e);
        };

        // Important: keep a reference to prevent garbage collection
        this.currentUtterance = utterance;

        // Use a small timeout to ensure cancel() has taken effect in some browsers
        setTimeout(() => {
            this.synthesis.speak(utterance);
        }, 50);
    }
}
