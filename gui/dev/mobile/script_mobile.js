// Criteria data
const criteriaData = [
    { category: 'Эмоциональное состояние', subcategories: [
        { name: 'Лицо', score: 7 },
        { name: 'Голос', score: 9 },
        { name: 'Пульс', score: 9 }
    ], totalScore: 25, maxScore: 30 },
    { category: 'Физическое состояние', subcategories: [
        { name: 'Частота дыхания', score: 9 },
        { name: 'Частота моргания', score: 9 }
    ], totalScore: 18, maxScore: 20 },
    { category: 'Возраст', subcategories: [], score: 8, totalScore: 8, maxScore: 10 },
    { category: 'Одежда', subcategories: [], score: 8, totalScore: 8, maxScore: 10 },
    { category: 'Общая оценка', subcategories: [], score: 7, totalScore: 7, maxScore: 10 }
];

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