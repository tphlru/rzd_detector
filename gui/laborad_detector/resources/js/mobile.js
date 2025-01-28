// popup
const popupOverlay = document.getElementById("popup-overlay");
const popup = document.getElementById("popup");

function showPopup() {
    popupOverlay.style.display = "block";
}

function hidePopup() {
    popupOverlay.style.display = "none";
}

popupOverlay.addEventListener("click", hidePopup);
const popupOverlay2 = document.getElementById("popup-overlay-video");
const popup2 = document.getElementById("popup-video");

function showPopupVideo() {
    popupOverlay2.style.display = "block";
}

function hidePopupVideo() {
    popupOverlay2.style.display = "none";
}
popupOverlay2.addEventListener("click", hidePopupVideo);

// Выпадающий список
document.querySelector('.dropdown').addEventListener('click', function(event) {
    this.querySelector('ul').style.display = 'block';
    event.stopPropagation(); // прекращаем дальнейшую передачу события!
});

window.addEventListener('click', function() {
    document.querySelector('.dropdown ul').style.display = 'none';
});

// липкое меню
const menu = document.createElement("nav");
menu.id = "nav-fixed";
menu.align = "center";
menu.innerHTML = `
<form action="index.html#videoPanel"><button id="ne" class="bg-blue-700 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded w-full sm:w-auto">Видео</button></form>
<form action="index.html#data"><button id="ne" class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded w-full sm:w-auto">Данные</button></form>
<form action="index.html#criteriaTable"><button id="ne" class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded w-full sm:w-auto">Таблица</button></form>
<form action="index.html#grafics"><button id="ne" class="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded w-full sm:w-auto">Графики</button></form>`;
document.body.appendChild(menu);


// таблица
// Criteria data
const criteriaData = [{
    category: 'Эмоциональное состояние',
    subcategories: [{
        name: 'Лицо',
        score: 7
    }, {
        name: 'Голос',
        score: 9
    }, {
        name: 'Пульс',
        score: 9
    }],
    totalScore: 25,
    maxScore: 30
}, {
    category: 'Физическое состояние',
    subcategories: [{
        name: 'Частота дыхания',
        score: 9
    }, {
        name: 'Частота моргания',
        score: 9
    }],
    totalScore: 18,
    maxScore: 20
}, {
    category: 'Возраст',
    subcategories: [],
    score: 8,
    totalScore: 8,
    maxScore: 10
}, {
    category: 'Одежда',
    subcategories: [],
    score: 8,
    totalScore: 8,
    maxScore: 10
}, {
    category: 'Общая оценка',
    subcategories: [],
    score: 7,
    totalScore: 7,
    maxScore: 10
}];
// Populate criteria table
function populateCriteriaTable() {
    const tableBody = document.querySelector('#criteriaTableBody');
    tableBody.innerHTML = '';
    criteriaData.forEach(item => {
        if (item.subcategories.length > 0) {
            item.subcategories.forEach((subitem, index) => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap">${index === 0 ? item.category : ''}</td>
                    <td class="px-6 py-4 whitespace-nowrap">${subitem.name}</td>
                    <td class="px-6 py-4 whitespace-nowrap ${getCriteriaClass(subitem.score)}">${subitem.score} / 10</td>
                    <td class="px-6 py-4 whitespace-nowrap">${index === 0 ? `${item.totalScore} / ${item.maxScore}` : ''}</td>
                `;
                tableBody.appendChild(row);
            });
        } else {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">${item.category}</td>
                <td class="px-6 py-4 whitespace-nowrap"></td>
                <td class="px-6 py-4 whitespace-nowrap ${getCriteriaClass(item.score)}">${item.score} / 10</td>
                <td class="px-6 py-4 whitespace-nowrap">${item.totalScore} / ${item.maxScore}</td>
            `;
            tableBody.appendChild(row);
        }
    });
}
// Get CSS class based on criteria score
function getCriteriaClass(score) {
    if (score <= 3) return 'criteria-low';
    if (score <= 7) return 'criteria-medium';
    return 'criteria-high';
}
// Initialize charts
function initializeCharts() {
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false
    };
    // Chart initialization code (unchanged)
    // ...
}
// Event listeners (unchanged)
// ...
// Initialize the application
function init() {
    populateCriteriaTable();
    initializeCharts();
}
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
    }
});

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
    }
});

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