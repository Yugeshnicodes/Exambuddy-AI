// =========================================================
// ELEMENTS
// =========================================================

const chatContainer =
    document.getElementById("chat-container");

const messageInput =
    document.getElementById("message-input");

const sendButton =
    document.getElementById("send-btn");

const voiceButton =
    document.getElementById("voice-btn");

const voiceStatus =
    document.getElementById("voice-status");


// =========================================================
// VOICE VARIABLES
// =========================================================

let recognition = null;

let isListening = false;

let voiceFinalText = "";


// =========================================================
// VOICE RECOGNITION SETUP
// =========================================================

if (
    "SpeechRecognition" in window ||
    "webkitSpeechRecognition" in window
) {


    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    recognition =
        new SpeechRecognition();


    // Keep listening until speech ends

    recognition.continuous = false;


    // Show speech while speaking

    recognition.interimResults = true;


    // Indian English

    recognition.lang = "en-IN";


    // =====================================================
    // VOICE START
    // =====================================================

    recognition.onstart = function () {


        isListening = true;


        voiceFinalText = "";


        if (voiceButton) {

            voiceButton.classList.add(
                "listening"
            );

        }


        if (voiceStatus) {

            voiceStatus.textContent =
                "🎙 Listening... Speak your question";

        }

    };



    // =====================================================
    // VOICE RESULT
    // =====================================================

    recognition.onresult = function (event) {


        let finalTranscript = "";

        let interimTranscript = "";


        for (
            let i = event.resultIndex;
            i < event.results.length;
            i++
        ) {


            const transcript =
                event.results[i][0].transcript;


            if (
                event.results[i].isFinal
            ) {

                finalTranscript +=
                    transcript;

            }

            else {

                interimTranscript +=
                    transcript;

            }

        }



        // Store final speech

        if (
            finalTranscript.trim()
        ) {

            voiceFinalText +=
                finalTranscript + " ";

        }



        // Combine final + live speech

        const displayText =
            (
                voiceFinalText +
                interimTranscript
            ).trim();



        // Show speech inside textarea

        if (displayText) {


            messageInput.value =
                displayText;



            // Resize textarea

            messageInput.style.height =
                "auto";


            messageInput.style.height =
                Math.min(
                    messageInput.scrollHeight,
                    120
                ) + "px";


        }



        // Show live voice status

        if (voiceStatus) {


            if (displayText) {

                voiceStatus.textContent =
                    "🎙 Hearing: " + displayText;

            }

            else {

                voiceStatus.textContent =
                    "🎙 Listening...";

            }

        }

    };



    // =====================================================
    // VOICE END
    // =====================================================

    recognition.onend = function () {


        isListening = false;


        if (voiceButton) {

            voiceButton.classList.remove(
                "listening"
            );

        }



        const finalMessage =
            messageInput.value.trim();



        // =================================================
        // AUTOMATICALLY SEND VOICE MESSAGE
        // =================================================

        if (finalMessage) {


            if (voiceStatus) {

                voiceStatus.textContent =
                    "✓ Voice captured. Getting answer...";

            }


            // Small delay so user can see captured text

            setTimeout(
                function () {

                    sendMessage();

                },
                300
            );


        }

        else {


            if (voiceStatus) {

                voiceStatus.textContent =
                    "Voice input ready.";

            }

        }

    };



    // =====================================================
    // VOICE ERROR
    // =====================================================

    recognition.onerror = function (event) {


        console.error(
            "Voice Recognition Error:",
            event.error
        );


        isListening = false;


        if (voiceButton) {

            voiceButton.classList.remove(
                "listening"
            );

        }



        if (voiceStatus) {


            if (
                event.error === "not-allowed"
            ) {

                voiceStatus.textContent =
                    "❌ Microphone permission denied.";

            }


            else if (
                event.error === "no-speech"
            ) {

                voiceStatus.textContent =
                    "No speech detected. Please try again.";

            }


            else if (
                event.error === "audio-capture"
            ) {

                voiceStatus.textContent =
                    "Microphone could not be accessed.";

            }


            else {

                voiceStatus.textContent =
                    "Voice input error. Please try again.";

            }

        }

    };

}


// =========================================================
// BROWSER SUPPORT CHECK
// =========================================================

else {


    console.warn(
        "Speech Recognition is not supported by this browser."
    );


    if (voiceButton) {

        voiceButton.disabled = true;

        voiceButton.title =
            "Voice input is not supported in this browser.";

    }


    if (voiceStatus) {

        voiceStatus.textContent =
            "Voice input is not supported in this browser.";

    }

}


// =========================================================
// START / STOP VOICE INPUT
// =========================================================

function startVoiceInput() {


    if (!recognition) {


        alert(
            "Voice input is not supported. Please use Google Chrome."
        );


        return;

    }



    // Stop if already listening

    if (isListening) {


        recognition.stop();


        return;

    }



    // Clear previous voice text

    voiceFinalText = "";


    messageInput.value = "";


    messageInput.style.height =
        "auto";



    try {


        recognition.start();


    }

    catch (error) {


        console.error(
            "Voice Start Error:",
            error
        );

    }

}


// =========================================================
// SEND MESSAGE
// =========================================================

async function sendMessage() {


    const message =
        messageInput.value.trim();



    if (!message) {

        return;

    }



    // Stop voice recognition

    if (
        recognition &&
        isListening
    ) {

        recognition.stop();

    }



    // Remove welcome screen

    const currentWelcome =
        document.getElementById(
            "welcome-screen"
        );



    if (currentWelcome) {

        currentWelcome.remove();

    }



    // Show user's message

    addMessage(
        message,
        "user"
    );



    // Clear input

    messageInput.value = "";


    messageInput.style.height =
        "auto";



    // Disable send button

    sendButton.disabled = true;



    // Show typing animation

    const typingId =
        addTypingIndicator();



    try {


        const response =
            await fetch(
                "/api/chat",
                {

                    method: "POST",


                    headers: {

                        "Content-Type":
                            "application/json"

                    },


                    body: JSON.stringify({

                        message: message

                    })

                }
            );



        const data =
            await response.json();



        // Remove typing indicator

        removeTypingIndicator(
            typingId
        );



        // =================================================
        // SUCCESS
        // =================================================

        if (data.success) {


            addMessage(
                data.answer,
                "ai"
            );


            if (voiceStatus) {

                voiceStatus.textContent =
                    "Voice input ready.";

            }

        }


        // =================================================
        // ERROR
        // =================================================

        else {


            addMessage(

                data.error ||
                "Something went wrong.",

                "ai"

            );

        }


    }


    catch (error) {


        removeTypingIndicator(
            typingId
        );


        addMessage(

            "Unable to connect to ExamBuddy AI. Please check whether the Flask server is running.",

            "ai"

        );


        console.error(
            "Chat Error:",
            error
        );

    }



    sendButton.disabled = false;


    messageInput.focus();

}


// =========================================================
// ADD MESSAGE
// =========================================================

function addMessage(
    text,
    sender
) {


    const row =
        document.createElement("div");


    row.className =
        `message-row ${sender}`;



    const avatar =
        document.createElement("div");


    avatar.className =
        "message-avatar";


    avatar.textContent =
        sender === "user"
            ? "👤"
            : "🎓";



    const bubble =
        document.createElement("div");


    bubble.className =
        "message-bubble";


    // Safe text rendering

    bubble.textContent =
        text;



    row.appendChild(
        avatar
    );


    row.appendChild(
        bubble
    );


    chatContainer.appendChild(
        row
    );


    scrollToBottom();

}


// =========================================================
// TYPING INDICATOR
// =========================================================

function addTypingIndicator() {


    const id =
        "typing-" +
        Date.now();



    const row =
        document.createElement("div");


    row.className =
        "message-row ai";


    row.id =
        id;



    const avatar =
        document.createElement("div");


    avatar.className =
        "message-avatar";


    avatar.textContent =
        "🎓";



    const bubble =
        document.createElement("div");


    bubble.className =
        "message-bubble";


    bubble.innerHTML = `
        <div class="typing">

            <span></span>
            <span></span>
            <span></span>

        </div>
    `;



    row.appendChild(
        avatar
    );


    row.appendChild(
        bubble
    );


    chatContainer.appendChild(
        row
    );


    scrollToBottom();



    return id;

}


// =========================================================
// REMOVE TYPING INDICATOR
// =========================================================

function removeTypingIndicator(id) {


    const element =
        document.getElementById(id);



    if (element) {

        element.remove();

    }

}


// =========================================================
// SCROLL TO BOTTOM
// =========================================================

function scrollToBottom() {


    chatContainer.scrollTop =
        chatContainer.scrollHeight;

}


// =========================================================
// KEYBOARD
// =========================================================

function handleKeyDown(event) {


    if (

        event.key === "Enter" &&

        !event.shiftKey

    ) {


        event.preventDefault();


        sendMessage();

    }

}


// =========================================================
// AUTO RESIZE TEXTAREA
// =========================================================

messageInput.addEventListener(
    "input",
    function () {


        this.style.height =
            "auto";


        this.style.height =
            Math.min(
                this.scrollHeight,
                120
            ) + "px";

    }
);


// =========================================================
// NEW CHAT
// =========================================================

function newChat() {

    location.reload();

}


// =========================================================
// SUGGESTION
// =========================================================

function sendSuggestion(text) {


    messageInput.value =
        text;


    messageInput.focus();


    messageInput.style.height =
        "auto";


    messageInput.style.height =
        Math.min(
            messageInput.scrollHeight,
            120
        ) + "px";


    sendMessage();

}


// =========================================================
// TOOL PROMPT
// =========================================================

function usePrompt(text) {


    messageInput.value =
        text;


    messageInput.focus();



    // Put cursor at end

    messageInput.selectionStart =
        messageInput.value.length;


    messageInput.selectionEnd =
        messageInput.value.length;



    messageInput.style.height =
        "auto";


    messageInput.style.height =
        Math.min(
            messageInput.scrollHeight,
            120
        ) + "px";

}


// =========================================================
// CLEAR FIREBASE CHAT HISTORY
// =========================================================

async function clearHistory() {


    const confirmed =
        confirm(
            "Are you sure you want to clear the chat history?"
        );



    if (!confirmed) {

        return;

    }



    try {


        const response =
            await fetch(
                "/api/history",
                {

                    method: "DELETE"

                }
            );



        const data =
            await response.json();



        if (data.success) {


            alert(
                "Chat history cleared successfully."
            );


            location.reload();

        }


        else {


            alert(
                data.error ||
                "Unable to clear history."
            );

        }

    }


    catch (error) {


        alert(
            "Server connection failed."
        );


        console.error(
            "Clear History Error:",
            error
        );

    }

}


// =========================================================
// LOGOUT
// =========================================================

function logoutUser() {


    const confirmed =
        confirm(
            "Do you want to logout from ExamBuddy AI?"
        );



    if (!confirmed) {

        return;

    }



    window.location.href =
        "/";

}