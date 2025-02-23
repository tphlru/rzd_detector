document.addEventListener('DOMContentLoaded', () => {
    // Функции для открытия и закрытия всплывающих окон
    window.showPopup = function() {
        document.getElementById('popup-overlay').classList.remove('hidden');
    };

    window.closePopup = function() {
        document.getElementById('popup-overlay').classList.add('hidden');
    };

    window.showPopupVideo = function() {
        document.getElementById('popup-overlay-video').classList.remove('hidden');
    };

    window.closePopupVideo = function() {
        document.getElementById('popup-overlay-video').classList.add('hidden');
    };

    // Функция для открытия изображения в полноэкранном режиме
    window.openImageFullscreen = function(src) {
        const imgWindow = window.open("", "_blank");
        imgWindow.document.write(`<img src="${src}" style="width:100%;">`);
    };

    // Функция для отправки данных на сервер
    function sendData(element, value) {
        fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ element, value })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    // Обработчики событий для кнопок
    document.getElementById('next').addEventListener('click', () => {
        sendData('next', 'clicked');
    });

    document.getElementById('stop').addEventListener('click', () => {
        sendData('stop', 'clicked');
    });

    document.getElementById('more').addEventListener('click', () => {
        sendData('more', 'clicked');
    });

    document.getElementById('videoBtn').addEventListener('click', () => {
        sendData('videoBtn', 'clicked');
    });

    // Debounce функция для задержки отправки данных
    function debounce(func, delay) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    }

    // Обработчики событий для полей ввода с debounce
    const genderSelect = document.getElementById('genderSelect');
    const ageInput = document.getElementById('ageInput');
    const departureInput = document.getElementById('departureInput');
    const arrivalInput = document.getElementById('arrivalInput');
    const question1 = document.getElementById('question1');

    const debouncedSend = debounce((element, value) => {
        sendData(element, value);
    }, 2000);

    genderSelect.addEventListener('change', (event) => {
        sendData('genderSelect', event.target.value);
    });

    ageInput.addEventListener('input', (event) => {
        debouncedSend('ageInput', event.target.value);
    });

    departureInput.addEventListener('input', (event) => {
        debouncedSend('departureInput', event.target.value);
    });

    arrivalInput.addEventListener('input', (event) => {
        debouncedSend('arrivalInput', event.target.value);
    });

    question1.addEventListener('input', (event) => {
        debouncedSend('question1', event.target.value);
    });

    // Обработчики событий для радиокнопок субъективной оценки
    document.querySelectorAll('input[name="subjective_rating"]').forEach((elem) => {
        elem.addEventListener('change', (event) => {
            sendData('subjective_rating', event.target.value);
        });
    });

    // Обработчики событий для чекбоксов вопросов
    document.querySelectorAll('input[name="question2"]').forEach((checkbox) => {
        checkbox.addEventListener('change', (event) => {
            const selected = Array.from(document.querySelectorAll('input[name="question2"]:checked')).map(cb => cb.value);
            sendData('question2', selected);
        });
    });

    // Обработчики событий для чекбоксов настройки подсчета
    ['emotional', 'physical', 'seasonal', 'subjective', 'statistical'].forEach((id) => {
        const checkbox = document.getElementById(id);
        if (checkbox) {
            checkbox.addEventListener('change', (event) => {
                sendData(id, event.target.checked);
            });
        }
    });

    // Обработчики для кнопки "Показать отчет"
    document.getElementById('reportButton').addEventListener('click', () => {
        sendData('reportButton', 'clicked');
    });
    var img = document.getElementById("video_feed");

    socket.on('connect', function() {
        socket.emit('start_video');
        alert("a2");
    });

    socket.on('video_frame', function(data) {
        console.log("a");
        img.src = "data:image/jpeg;base64," + btoa(String.fromCharCode.apply(null, new Uint8Array(data.frame)));
        
    });
});

const socket = io();
                
function updateScoreColors() {
    document.querySelectorAll('.score-indicator').forEach(indicator => {
        const score = parseInt(indicator.dataset.score);
        const maxScore = parseInt(indicator.dataset.max);
        const percentage = (score / maxScore) * 100;
        
        indicator.classList.remove('score-low', 'score-medium', 'score-high');
        if (percentage < 33) {
            indicator.classList.add('score-low');
        } else if (percentage < 66) {
            indicator.classList.add('score-medium');
        } else {
            indicator.classList.add('score-high');
        }
    });
}
        
socket.on('criteria_updated', function(criteriaData) {
    for (const [category, info] of Object.entries(criteriaData)) {
        // Update main category score
        const categoryRow = document.querySelector(`tr[data-category="${category}"]`);
        if (categoryRow) {
            const scoreDiv = categoryRow.querySelector('.score-indicator');
            scoreDiv.textContent = `${info.score}/${info.max_score}`;
            scoreDiv.dataset.score = info.score;
        }

        if (info.sublevels) {
            for (const [sublevel, subInfo] of Object.entries(info.sublevels)) {
                const sublevelRow = document.querySelector(`tr[data-category="${category}"][data-sublevel="${sublevel}"]`);
                if (sublevelRow) {
                    const scoreDiv = sublevelRow.querySelector('.score-indicator');
                    scoreDiv.textContent = `${subInfo.score}/${subInfo.max_score}`;
                    scoreDiv.dataset.score = subInfo.score;
                }
            }
        }
        }
    updateScoreColors();
});

document.addEventListener('DOMContentLoaded', updateScoreColors);