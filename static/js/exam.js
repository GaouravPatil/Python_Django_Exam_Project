document.addEventListener('DOMContentLoaded', function () {
    const sessionId = document.getElementById('session-id').value;
    let totalQuestions = parseInt(document.getElementById('total-questions').value);
    let currentQuestion = 1;

    const isEndless = document.getElementById('is-endless').value === 'true';

    // --- Navigation Logic ---
    window.navigate = function (direction) {
        const newQuestion = currentQuestion + direction;

        if (newQuestion > totalQuestions) {
            if (isEndless) {
                fetchNextQuestion();
            } else {
                // Normal mode end
            }
        } else if (newQuestion >= 1) {
            jumpToQuestion(newQuestion);
        }
    };

    function fetchNextQuestion() {
        const nextBtn = document.getElementById('next-btn');
        nextBtn.disabled = true;
        nextBtn.innerText = 'Loading...';

        fetch('/api/next_question/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ session_id: sessionId })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error loading question: ' + data.error);
                    return;
                }

                // 1. Add Question HTML
                const container = document.getElementById('questions-container');
                const qNum = data.total_questions;

                const div = document.createElement('div');
                div.className = 'question-card';
                div.id = `question-${qNum}`;
                div.style.display = 'none';
                div.innerHTML = `
                <div class="question-text">
                    <h3>Question ${qNum}</h3>
                    <p>${data.text}</p>
                </div>
                <div class="options-list">
                    ${data.options.map(opt => `
                    <label class="option-item">
                        <input type="radio" name="question_${data.id}" value="${opt}" onchange="saveAnswer('${sessionId}', '${data.id}', this.value, ${qNum})">
                        <span class="option-text">${opt}</span>
                    </label>
                    `).join('')}
                </div>
            `;
                container.appendChild(div);

                // 2. Add Nav Button
                const navContainer = document.querySelector('.question-nav');
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'nav-btn';
                btn.id = `nav-btn-${qNum}`;
                btn.innerText = qNum;
                btn.onclick = function () { jumpToQuestion(qNum); };
                navContainer.appendChild(btn);

                // 3. Update State
                totalQuestions = qNum;
                jumpToQuestion(qNum);
            })
            .finally(() => {
                nextBtn.disabled = false;
                nextBtn.innerText = 'Next';
            });
    }

    window.jumpToQuestion = function (questionNumber) {
        questionNumber = parseInt(questionNumber);
        // Hide current
        if (document.getElementById(`question-${currentQuestion}`)) {
            document.getElementById(`question-${currentQuestion}`).style.display = 'none';
            document.getElementById(`nav-btn-${currentQuestion}`).classList.remove('active');
        }

        // Show new
        currentQuestion = questionNumber;
        document.getElementById(`question-${currentQuestion}`).style.display = 'block';
        document.getElementById(`nav-btn-${currentQuestion}`).classList.add('active');

        // Update buttons
        document.getElementById('prev-btn').disabled = (currentQuestion === 1);

        if (currentQuestion === totalQuestions) {
            if (isEndless) {
                document.getElementById('next-btn').style.display = 'inline-block';
                document.getElementById('submit-btn').style.display = 'inline-block'; // Allow submit anytime
                document.getElementById('next-btn').innerText = 'Next Question';
            } else {
                document.getElementById('next-btn').style.display = 'none';
                document.getElementById('submit-btn').style.display = 'inline-block';
            }
        } else {
            document.getElementById('next-btn').style.display = 'inline-block';
            document.getElementById('next-btn').innerText = 'Next';
            document.getElementById('submit-btn').style.display = 'none';
        }
    };

    // --- Answer Saving ---
    window.saveAnswer = function (sessId, qId, answer, qNum) {
        fetch('/api/save_answer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                session_id: sessId,
                question_id: qId,
                selected_answer: answer
            })
        }).then(response => {
            if (response.ok) {
                document.getElementById(`nav-btn-${qNum}`).classList.add('answered');
            }
        });
    };

    // --- Timer ---
    let seconds = 0;
    setInterval(() => {
        seconds++;
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        document.getElementById('timer').innerText =
            `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }, 1000);

    // --- Proctoring: Webcam ---
    const video = document.getElementById('webcam-feed');

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (stream) {
                video.srcObject = stream;

                // Capture snapshot every 30 seconds
                setInterval(() => {
                    captureSnapshot();
                }, 30000);
            })
            .catch(function (error) {
                console.error("Webcam access denied", error);
                logActivity('webcam_denied', 'User denied webcam access');
                alert("Webcam access is required for this exam. Please enable it.");
            });
    }

    function captureSnapshot() {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg', 0.5); // Compress quality

        fetch('/api/upload_snapshot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                session_id: sessionId,
                image_data: imageData
            })
        });
    }

    // --- Proctoring: Anti-Cheating ---

    // 1. Tab Switching
    document.addEventListener('visibilitychange', function () {
        if (document.hidden) {
            logActivity('tab_switch', 'User switched tabs or minimized window');
            alert("Warning: Tab switching is monitored and recorded!");
        }
    });

    // 2. Copy/Paste Block
    document.addEventListener('contextmenu', event => event.preventDefault());
    document.addEventListener('copy', event => event.preventDefault());
    document.addEventListener('paste', event => event.preventDefault());
    document.addEventListener('cut', event => event.preventDefault());

    // 3. Focus Loss (extra layer)
    window.addEventListener('blur', function () {
        logActivity('focus_lost', 'Window lost focus');
    });

    function logActivity(type, details) {
        fetch('/api/log_activity/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                session_id: sessionId,
                event_type: type,
                details: details
            })
        });
    }

    // Helper for CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
