const changer = document.getElementById("cameraChanger");
alert("1");
changer.addEventListener('cameraChanger', changer1);


// Попапы
const popupOverlay = document.getElementById("popup-overlay");
const popup = document.getElementById("popup");
const popupOverlay2 = document.getElementById("popup-overlay-video");
const popup2 = document.getElementById("popup-video");

// Статистические данные
const CRIME_STATS = {
    cities: {
        'Ярославль': {
            total: 41.18,
            property: 51.47,
            violent: 22.06
        },
        'Москва': {
            total: 34.34,
            property: 40.88,
            violsent: 28.39
        },
        'Самара': {
            total: 31.58,
            property: 44.08,
            violent: 22.37
        },
        'Архангельск': {
            total: 45.83,
            property: 62.50,
            violent: 33.33
        },
        'Пермь': {
            total: 48.57,
            property: 55.71,
            violent: 41.43
        },
        'Волгоград': {
            total: 50.00,
            property: 63.33,
            violent: 45.00
        }
    },
    ageGroups: {
        '14-17': 0.03,
        '18-24': 0.15,
        '25-29': 0.17,
        '30-49': 0.56,
        '50+': 0.10
    },
    gender: {
        'Мужской': 0.85,
        'Женский': 0.15
    }
};

const MAX_VALUES = {
    total: 50,
    property: 65,
    violent: 45
};
const criteriaData = [{
    category: 'Эмоциональное состояние',
    subcategories: [{
        name: 'Лицо',
        score: 0
    }, {
        name: 'Эмоциональность голоса',
        score: 0
    }, {
        name: 'Искажения голоса',
        score: 0
    }, {
        name: 'Пульс',
        score: 0
    }],
    totalScore: 0,
    maxScore: 30
}, {
    category: 'Физическое состояние',
    subcategories: [{
        name: 'Частота дыхания',
        score: 0
    }, {
        name: 'Частота моргания',
        score: 0
    }],
    totalScore: 0,
    maxScore: 20
}, {
    category: 'Сезонность одежды',
    subcategories: [],
    score: 0, // было 2
    totalScore: 0,
    maxScore: 10
}, {
    category: 'Субъективная оценка',
    subcategories: [],
    score: 2,
    totalScore: 2,
    maxScore: 3
}, {
    category: 'Статистическая оценка',
    subcategories: [],
    score: 0,
    totalScore: 0,
    maxScore: 10
}, {
    category: 'Общая оценка',
    subcategories: [],
    score: 0,
    totalScore: 0,
    maxScore: 10
}];

function calculateTotalScore() {
    const weights = [0.3, 0.2, 0.15, 0.15, 0.1, 0.05];

    let totalScore = 0;
    for (let i = 0; i < criteriaData.length - 1; i++) {
        // Для статистической оценки (i == 5) используем инвертированное значение
        const score = (i === 5) ?
            (criteriaData[i].totalScore / criteriaData[i].maxScore) * 10 :
            (criteriaData[i].totalScore / criteriaData[i].maxScore) * 10;

        totalScore += score * weights[i];
    }

    const totalIndex = criteriaData.length - 1;
    criteriaData[totalIndex].score = totalScore;
    criteriaData[totalIndex].totalScore = totalScore;
}


// Функции для попапов
function showPopup() {
    popupOverlay.style.display = "block";
}

function hidePopup() {
    popupOverlay.style.display = "none";
}

function showPopupVideo() {
    popupOverlay2.style.display = "block";
}

function hidePopupVideo() {
    popupOverlay2.style.display = "none";
}

// Обработчики для попапов
popupOverlay.addEventListener("click", hidePopup);
popupOverlay2.addEventListener("click", hidePopupVideo);

// Выпадающий список
document.querySelector('.dropdown') ? .addEventListener('click', function(event) {
    this.querySelector('ul').style.display = 'block';
    event.stopPropagation();
});

window.addEventListener('click', function() {
    const dropdownUl = document.querySelector('.dropdown ul');
    if (dropdownUl) {
        dropdownUl.style.display = 'none';
    }
});

// Редирект для мобильных устройств
document.addEventListener("DOMContentLoaded", function() {
    if (window.matchMedia("(pointer: coarse)").matches &&
        Math.max(window.innerWidth, window.innerHeight) / Math.min(window.innerWidth, window.innerHeight) > 2) {
        window.location.replace("mobile.html");
    } else if (window.matchMedia("(pointer: coarse)").matches && window.innerWidth < window.innerHeight) {
        window.location.replace("tablet.html");
    }
});

// Функции для обработки формы статистики
const SUBMIT_DELAY = 3000;
let submitTimeout = null;

const formElements = {
    gender: document.getElementById('genderSelect'),
    age: document.getElementById('ageInput'),
    departure: document.getElementById('departureInput'),
    arrival: document.getElementById('arrivalInput'),
    nextButton: document.getElementById('next')
};

function getAgeGroup(age) {
    age = parseInt(age);
    if (age >= 14 && age <= 17) return '14-17';
    if (age >= 18 && age <= 24) return '18-24';
    if (age >= 25 && age <= 29) return '25-29';
    if (age >= 30 && age <= 49) return '30-49';
    if (age >= 50) return '50+';
    return null;
}

function convertToTenScale(value, maxValue) {
    return (value / maxValue) * 10;
}

// Обновляем функцию calculateStats для умножения на 10
function calculateStats(data) {
    console.log("Входные данные:", data);
    const depCity = Object.keys(CRIME_STATS.cities).find(city => {
        console.log("Сравниваем:", city, "с", data.departure);
        return data.departure.toLowerCase().includes(city.toLowerCase())
    });
    console.log("Найденный город:", depCity);

    if (!depCity) return null;

    const cityStats = CRIME_STATS.cities[depCity];
    const ageGroup = getAgeGroup(data.age);
    if (!ageGroup) return null;

    // Тут ageMultiplier и genderMultiplier - это коэффициенты распределения статистики
    const ageMultiplier = CRIME_STATS.ageGroups[ageGroup];
    const genderMultiplier = CRIME_STATS.gender[data.gender];

    // Используем их для взвешенной оценки риска
    return {
        total: 10 - ((cityStats.total / MAX_VALUES.total) * ageMultiplier * genderMultiplier * 100),
        property: 10 - ((cityStats.property / MAX_VALUES.property) * ageMultiplier * genderMultiplier * 100),
        violent: 10 - ((cityStats.violent / MAX_VALUES.violent) * ageMultiplier * genderMultiplier * 100)
    };
}

// Добавляем функцию обновления субъективной оценки
function updateSubjectiveRating(rating) {
    const subjectiveIndex = 3; // индекс субъективной оценки в массиве
    const ratingMap = {
        '-2': 2.5,
        '-1': 5,
        '0': 7.5,
        '1': 10
    };

    const score = ratingMap[rating] || 2;
    criteriaData[subjectiveIndex].score = score;
    criteriaData[subjectiveIndex].totalScore = score;

    calculateTotalScore();
    populateCriteriaTable();
}

// Функции для работы с таблицей
function getCriteriaClass(score) {
    if (score <= 3) return 'criteria-low';
    if (score <= 7) return 'criteria-medium';
    return 'criteria-high';
}

function populateCriteriaTable() {
    const tableBody = document.querySelector('#criteriaTableBody');
    if (!tableBody) return;

    tableBody.innerHTML = '';
    criteriaData.forEach(item => {
        if (item.subcategories.length > 0) {
            item.subcategories.forEach((subitem, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap">${index === 0 ? item.category : ''}</td>
                    <td class="px-6 py-4 whitespace-nowrap">${subitem.name}</td>
                    <td class="px-6 py-4 whitespace-nowrap ${getCriteriaClass(subitem.score)}">${subitem.score.toFixed(1)} / 10</td>
                    <td class="px-6 py-4 whitespace-nowrap">${index === 0 ? `${item.totalScore.toFixed(1)} / ${item.maxScore}` : ''}</td>
                `;
                tableBody.appendChild(row);
            });
        } else {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">${item.category}</td>
                <td class="px-6 py-4 whitespace-nowrap"></td>
                <td class="px-6 py-4 whitespace-nowrap ${getCriteriaClass(item.score)}">${item.score.toFixed(1)} / 10</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.totalScore.toFixed(1)} / ${item.maxScore}</td>
            `;
            tableBody.appendChild(row);
        }
    });
    toggleCriteriaVisibility();
}

function updateStatisticalData(stats) {
    if (!stats) return;

    const average = ((stats.total + stats.property + stats.violent) / 3);
    const statIndex = 4; // индекс статистической оценки
    criteriaData[statIndex].score = average;
    criteriaData[statIndex].totalScore = average;

    calculateTotalScore(); // добавляем расчет общей оценки после обновления статистической
    populateCriteriaTable();
}
// <<<<<<< HEAD

function isFormValid() {
    return (
        formElements.gender.value &&
        formElements.gender.value !== 'Выберите...' &&
        formElements.age.value &&
        formElements.departure.value &&
        formElements.arrival.value
    );
}

function collectFormData() {
    return {
        gender: formElements.gender.value,
        age: formElements.age.value,
        departure: formElements.departure.value,
        arrival: formElements.arrival.value
    };
}

function submitForm() {
    if (isFormValid()) {
        const data = collectFormData();
        const stats = calculateStats(data);
        console.log('Данные формы:', data);
        console.log('Статистическая оценка (10-балльная шкала):', stats);
        updateStatisticalData(stats);
        //=======
        // Run initialization when the DOM is fully loaded
        document.addEventListener('DOMContentLoaded', init);
        const barColors = ["green", "orange", "blue", "red", "brown", "purple", "black", "yellow"];
        const xValuesEV = ["Нейтраль", "Радость", "Грусть", "Гнев", "Отвращение", "Страх", "Удивление"];
        var yValuesEV = [50, 15, 11, 1, 2, 5, 10];
        new Chart("emotionsChart", {
            type: "pie",
            data: {
                labels: xValuesEV,
                datasets: [{
                    backgroundColor: barColors,
                    data: yValuesEV
                }]
            },
        });

        var xValuesVzdoh = [16, 14, 12, 10, 8, 6, 4, 2, 0];
        var yValuesVzdoh = [73, 75, 69, 83, 85, 98, 111, 115, 110];
        new Chart("breathingChart", {
            type: "line",
            data: {
                labels: xValuesVzdoh,
                datasets: [{
                    backgroundColor: "rgba(0,255,0,1.0)",
                    borderColor: "rgba(0,255,0,0.7)",
                    data: yValuesVzdoh
                }]
            },
            options: {
                plugins: {
                    legend: false,
                }
                // >>>>>>> 22a5b70e272cf1700ecf5ce0dd7845d96fedb6b8
            }
        });

        //<<<<<<< HEAD
        function handleFormChange() {
            if (submitTimeout) {
                clearTimeout(submitTimeout);
            }
        }
        //=======
        const xValuesPulse = ["Сейчас", "Максимум", "Минимум"];
        var yValuesPulse = [73, 105, 69];
        const barColorsPulse = ["red", "green", "blue"];
        new Chart("pulseChart", {
            type: "bar",
            data: {
                labels: xValuesPulse,
                datasets: [{
                    backgroundColor: barColorsPulse,
                    data: yValuesPulse
                }]
            },
            options: {
                plugins: {
                    legend: false,
                }
                // >>>>>>> 22a5b70e272cf1700ecf5ce0dd7845d96fedb6b8
            }
            //submitTimeout = setTimeout(submitForm, SUBMIT_DELAY);
        });

        // <<<<<<< HEAD
        function resetForm() {
            formElements.gender.selectedIndex = 0;
            formElemens.age.value = '';
            formElements.departure.value = '';
            formElements.arrival.value = '';

            const statItem = criteriaData[criteriaData.length - 1];
            statItem.score = 0;
            statItem.totalScore = 0;
            populateCriteriaTable();
        }

        function addNoise(values) {
            return values.map(value => {
                const noise = (Math.random() - 0.5) * 0.05; // шум ±2.5%
                return Math.max(0, Math.min(1, value + noise)); // ограничиваем значения от 0 до 1
            });
        }

        // Инициализация графиков
        function initializeCharts() {
            const xValuesEF = ["Отвращение", "Нейтраль", "Радость", "Грусть", "Страх", "Испуг", "Злость"];
            const yValuesEF = [0.35, 0.25, 0.15, 0.15, 0.05, 0.03, 0.02];
            const barColors = ["#8B4513", "#808080", "#FFD700", "#4682B4", "#800080", "#FFA07A", "#FF0000"];

            const voiceEmotions = ["Спокойный", "Радостный", "Грустный", "Взволнованный"];
            const voiceValues = [45, 25, 20, 10];
            const voiceColors = ["#4CAF50", "#FFC107", "#2196F3", "#FF5722"];

            new Chart("voiceChart", {
                type: "pie",
                data: {
                    labels: voiceEmotions,
                    datasets: [{
                        backgroundColor: voiceColors,
                        data: voiceValues
                    }]
                },
            });

            new Chart("emotionsChart", {
                type: "pie",
                data: {
                    labels: xValuesEF,
                    datasets: [{
                        backgroundColor: barColors,
                        data: yValuesEF
                    }]
                },
            });

            const xValuesMorganie = [16, 14, 12, 10, 8, 6, 4, 2, 0];
            const yValuesMorganie = [73, 75, 69, 83, 85, 98, 111, 115, 110];
            new Chart("blinkingChart", {
                type: "line",
                data: {
                    labels: xValuesMorganie,
                    datasets: [{
                        backgroundColor: "rgba(0,0,255,1.0)",
                        borderColor: "rgba(0,0,255,0.7)",
                        data: yValuesMorganie
                    }]
                },
                options: {
                    plugins: {
                        legend: false,
                    }
                }
            });
        }

        function openImageFullscreen(src) {
            const overlay = document.createElement('div');
            overlay.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); display: flex; justify-content: center; align-items: center; z-index: 1000;';

            const img = document.createElement('img');
            img.src = src;
            img.style.cssText = 'max-width: 90%; max-height: 90%; object-fit: contain;';

            overlay.appendChild(img);
            overlay.onclick = () => overlay.remove();
            document.body.appendChild(overlay);
        }

        function toggleCriteriaVisibility() {
            const tableBody = document.querySelector('#criteriaTableBody');
            if (!tableBody) return;

            const checkboxMap = {
                'emotional': 0, // Эмоциональное состояние
                'physical': 1, // Физическое состояние
                'seasonal': 2, // Сезонность одежды (индекс правильный)
                'subjective': 3, // Субъективная оценка (был неверный индекс)
                'statistical': 4 // Статистическая оценка (был неверный индекс)
            };

            Object.entries(checkboxMap).forEach(([checkboxId, criteriaIndex]) => {
                const checkbox = document.getElementById(checkboxId);
                if (!checkbox) return;

                const rows = tableBody.querySelectorAll('tr');
                const item = criteriaData[criteriaIndex];

                if (item.subcategories && item.subcategories.length > 0) {
                    // Для критериев с подкатегориями
                    let count = item.subcategories.length;
                    let found = false;

                    rows.forEach((row) => {
                        if (row.cells[0].textContent === 'Общая оценка') {
                            return; // Пропускаем строку общей оценки
                        }

                        if (row.cells[0].textContent === item.category) {
                            found = true;
                            row.style.display = checkbox.checked ? '' : 'none';
                        } else if (found && count > 0) {
                            row.style.display = checkbox.checked ? '' : 'none';
                            count--;
                        }
                    });
                } else {
                    // Для критериев без подкатегорий
                    rows.forEach((row) => {
                        if (row.cells[0].textContent === 'Общая оценка') {
                            return; // Пропускаем строку общей оценки
                        }

                        if (row.cells[0].textContent === item.category) {
                            row.style.display = checkbox.checked ? '' : 'none';
                        }
                    });
                }
            });
        }

        // Горячие клавиши
        document.addEventListener('keydown', function(event) {
            if (event.key == "v") {
                window.location.replace("index.html#videoPanel");
            } else if (event.key == "d") {
                window.location.replace("index.html#dataPanel");
            } else if (event.key == "p" || event.key == "m") {
                window.location.replace("index.html#managementConsole");
            } else if (event.key == "t") {
                window.location.replace("index.html#criteriaTable");
            } else if (event.key == "g") {
                window.location.replace("index.html#grafics");
            }
        });


        // Основная инициализация
        document.addEventListener('DOMContentLoaded', () => {
                    const blinkingValues = [0, 5, 12, 16, 18, 80, 17, 15, 17, 16, 18, 17, 16, 17, 18, 17, 17];

                    let currentIndex = 0;
                    let blinkingInterval;

                    const video = document.querySelector('video');

                    const breathingStatus = document.getElementById('breathingStatus');
                    const breathingImage = document.getElementById('breathingImage');

                    // Сброс состояния
                    breathingStatus.textContent = '-';
                    breathingImage.classList.add('hidden');

                    // Находим элемент с графиком голосовых эмоций
                    const voiceChartCanvas = document.getElementById('voiceChart');
                    const voiceChartContainer = voiceChartCanvas.parentElement;
                    // Создаем элемент для текста "Подождите"
                    const waitingText = document.createElement('div');
                    waitingText.textContent = '-';
                    waitingText.className = 'text-2xl text-center';
                    waitingText.id = 'voiceWaitingText';

                    // Скрываем график и показываем текст
                    voiceChartCanvas.style.display = 'none';
                    voiceChartContainer.insertBefore(waitingText, voiceChartCanvas);

                    const stopButton = document.getElementById('stop');
                    stopButton.addEventListener('click', () => {
                        video.pause(); // Останавливаем воспроизведение
                        video.currentTime = 0; // Возвращаем видео в начало (опционально)
                    });

                    video.addEventListener('play', () => {

                        // Показываем график с задержкой и обновляем его
                        setTimeout(() => {
                            emotionsChartCanvas.style.display = 'block';

                            // Создаем интервал обновления с шумами
                            const updateInterval = setInterval(() => {
                                const noisyValues = addNoise(targetEmotions.values);
                                new Chart(emotionsChartCanvas, {
                                    type: "pie",
                                    data: {
                                        labels: targetEmotions.labels,
                                        datasets: [{
                                            backgroundColor: ["#8B4513", "#808080", "#FFD700", "#4682B4", "#800080", "#FFA07A", "#FF0000"],
                                            data: noisyValues
                                        }]
                                    }
                                });
                            }, 4000);

                            // Через 23 секунды показываем финальные значения и останавливаем обновление
                            setTimeout(() => {
                                clearInterval(updateInterval);
                                new Chart(emotionsChartCanvas, {
                                    type: "pie",
                                    data: {
                                        labels: targetEmotions.labels,
                                        datasets: [{
                                            backgroundColor: ["#8B4513", "#808080", "#FFD700", "#4682B4", "#800080", "#FFA07A", "#FF0000"],
                                            data: targetEmotions.values
                                        }]
                                    }
                                });
                            }, 23000);
                        }, 5000);

                        // Скрываем график эмоций лица при старте
                        const emotionsChartCanvas = document.getElementById('emotionsChart');
                        emotionsChartCanvas.style.display = 'none';

                        // Целевые значения эмоций
                        const targetEmotions = {
                            labels: ["Отвращение", "Нейтраль", "Радость", "Грусть", "Страх", "Испуг", "Злость"],
                            values: [0.35, 0.25, 0.15, 0.15, 0.05, 0.03, 0.02]
                        };

                        setTimeout(() => {
                            // Добавляем значение 9 в строку пульса
                            criteriaData[0].subcategories[3].score = 9;
                            populateCriteriaTable();
                            calculateTotalScore();
                        }, 29880); // Используем тот же таймаут, что и для других измерений

                        setTimeout(() => {
                            // Находим индекс первой подкатегории (Лицо) в первом критерии (Эмоциональное состояние)
                            criteriaData[0].subcategories[0].score = 6;
                            populateCriteriaTable();
                            calculateTotalScore();
                        }, 23000);

                        setTimeout(() => {
                            // Находим индекс "Эмоциональность голоса" во второй подкатегории первого критерия (Эмоциональное состояние)
                            criteriaData[0].subcategories[1].score = 9;
                            populateCriteriaTable();
                            calculateTotalScore();
                        }, 18000); // 18 секунд - момент появления блока Эмоциональность голоса

                        // Находим элемент с графиком голосовых эмоций
                        const voiceChartCanvas = document.getElementById('voiceChart');
                        const voiceChartContainer = voiceChartCanvas.parentElement;

                        // Создаем элемент для текста "Подождите"
                        const waitingText = document.createElement('div');
                        waitingText.textContent = 'Подождите ...';
                        waitingText.className = 'text-2xl text-center';
                        waitingText.id = 'voiceWaitingText';

                        // Скрываем график и показываем текст
                        voiceChartCanvas.style.display = 'none';
                        voiceChartContainer.insertBefore(waitingText, voiceChartCanvas);

                        // Через 22.4 секунды показываем график и убираем текст
                        setTimeout(() => {
                            waitingText.remove();
                            voiceChartCanvas.style.display = 'block';
                        }, 22400);

                        // Показываем "определение"
                        setTimeout(() => {
                            breathingStatus.textContent = 'Подождите ...';
                        }, 0);

                        setTimeout(() => {
                            breathingStatus.classList.add('hidden');
                            breathingImage.classList.remove('hidden');
                        }, 26300);

                        setTimeout(() => {
                            // Добавляем значение 10 в строку частоты дыхания
                            criteriaData[1].subcategories[0].score = 10;
                            populateCriteriaTable();
                            calculateTotalScore();
                        }, 26300); // Используем тот же таймаут, что и для изображения

                        setTimeout(() => {
                            // Находим индекс сезонности одежды (после удаления возраста это индекс 2)
                            criteriaData[2].score = 2.4;
                            criteriaData[2].totalScore = 2.4;
                            populateCriteriaTable();
                            calculateTotalScore();
                        }, 3000);

                        // Добавляем таймер для обновления частоты моргания
                        setTimeout(() => {
                            criteriaData[1].subcategories[1].score = 10;
                            populateCriteriaTable();
                            calculateTotalScore();
                        }, 25000);

                        // Обновление значения моргания каждые 2 секунды
                        const valueDisplay = document.getElementById('blinkingValue');
                        const chartDiv = document.getElementById('blinkingChart');
                        const medianDiv = document.getElementById('blinkingMedian');

                        currentIndex = 0;
                        clearInterval(blinkingInterval);

                        blinkingInterval = setInterval(() => {
                            if (currentIndex < blinkingValues.length) {
                                valueDisplay.textContent = blinkingValues[currentIndex];
                                currentIndex++;
                            }
                        }, 2000);

                        // Показ графика через 25 секунд
                        setTimeout(() => {
                            console.log("Show моргание")
                            clearInterval(blinkingInterval);

                            valueDisplay.style.display = 'none';
                            chartDiv.style.display = 'block';

                            // Удаляем старый canvas и создаем новый
                            chartDiv.remove();
                            const newCanvas = document.createElement('canvas');
                            newCanvas.id = 'blinkingChart';
                            document.querySelector('#grafics div:nth-child(3)').appendChild(newCanvas);

                            // Создаем новый график
                            blinkingChart = new Chart(newCanvas, {
                                type: "line",
                                data: {
                                    labels: Array.from({
                                        length: blinkingValues.length
                                    }, (_, i) => i * 2),
                                    datasets: [{
                                        backgroundColor: "rgba(0,0,255,1.0)",
                                        borderColor: "rgba(0,0,255,0.7)",
                                        data: blinkingValues
                                    }]
                                },
                                options: {
                                    plugins: {
                                        legend: false
                                    }
                                }
                            });

                            // Вычисляем и показываем медиану
                            const sortedValues = [...blinkingValues].sort((a, b) => a - b);
                            const median = sortedValues.length % 2 === 0 ?
                                (sortedValues[sortedValues.length / 2 - 1] + sortedValues[sortedValues.length / 2]) / 2 :
                                sortedValues[Math.floor(sortedValues.length / 2)];

                            medianDiv.textContent = `Медиана: ${median}`;

                            // Обновляем значение в таблице
                            criteriaData[1].subcategories[1].score = 10;
                            populateCriteriaTable();
                            calculateTotalScore();
                        }, 25000);

                        setTimeout(() => {
                            pulseStatus2.textContent = 'Пульс 76 уд/мин'; // Добавьте эту строку
                            pulseStatus2.classList.remove('hidden'); // Добавьте эту строку
                        }, 26300);

                        setTimeout(() => {
                            pulseStatus.classList.add('hidden');
                            pulseImage.classList.remove('hidden');
                        }, 26300);

                        const voiceDistortionBlock = document.getElementById('voiceDistortion');
                        voiceDistortionBlock.classList.add('hidden');

                        // Показываем блок через 18 секунд
                        setTimeout(() => {
                            voiceDistortionBlock.classList.remove('hidden');
                            // Обновляем значение для "Искажения голоса"
                            criteriaData[0].subcategories[2].score = 6.8;
                            populateCriteriaTable();
                            calculateTotalScore();
                        }, 18000);
                    });

                    const ratingInputs = document.getElementsByName('rating');
                    ratingInputs.forEach(input => {
                        input.addEventListener('change', (e) => {
                            updateSubjectiveRating(e.target.value);
                        });
                    });

                    populateCriteriaTable();
                    initializeCharts();

                    // Инициализация обработчиков формы
                    Object.values(formElements).forEach(element => {
                        if (element instanceof HTMLElement && element !== formElements.nextButton) {
                            element.addEventListener('input', handleFormChange);
                            element.addEventListener('change', handleFormChange);
                        }
                    });

                    formElements.nextButton.addEventListener('click', resetForm);
                    // В конец addEventListener('DOMContentLoaded', ...)
                    const checkboxes = document.querySelectorAll('.dropdown input[type="checkbox"]');
                    checkboxes.forEach(checkbox => {
                        checkbox.addEventListener('change', toggleCriteriaVisibility);
                    });
                    //=======
                    const xValuesMorganie = [16, 14, 12, 10, 8, 6, 4, 2, 0];
                    var yValuesMorganie = [73, 75, 69, 83, 85, 98, 111, 115, 110];
                    new Chart("blinkingChart", {
                        type: "line",
                        data: {
                            labels: xValuesMorganie,
                            datasets: [{
                                backgroundColor: "rgba(0,0,255,1.0)",
                                borderColor: "rgba(0,0,255,0.7)",
                                data: yValuesMorganie
                            }]
                        },
                        options: {
                            plugins: {
                                legend: false,
                            }
                        }
                    });
                    // >>>>>>> 22a5b70e272cf1700ecf5ce0dd7845d96fedb6b8