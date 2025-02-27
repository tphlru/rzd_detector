// Add event listeners for checkboxes
document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = ['emotional', 'physical', 'seasonal', 'subjective', 'statistical'];
    
    checkboxes.forEach(id => {
        const checkbox = document.getElementById(id);
        if (checkbox) {
            checkbox.addEventListener('change', function() {
                // Немедленно применяем визуальные изменения
                const rows = document.querySelectorAll(`tr[data-category="${id}"]`);
                rows.forEach(row => {
                    if (!this.checked) {
                        row.classList.add('disabled-row');
                        // Обнуляем отображаемые значения
                        const scoreDiv = row.querySelector('.score-indicator');
                        if (scoreDiv) {
                            const maxScore = scoreDiv.dataset.max;
                            scoreDiv.textContent = `0/${maxScore}`;
                            scoreDiv.dataset.score = 0;
                        }
                    } else {
                        row.classList.remove('disabled-row');
                    }
                });
                
                // Отправляем изменения на сервер
                fetch('/submit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        element: id,
                        value: this.checked
                    })
                });
                
                // Обновляем цвета после изменения
                updateScoreColors();
            });
        }
    });
});

// Переопределяем функцию обновления состояния строк
function updateRowState(row, enabled) {
    row.style.display = 'table-row'; // Форсируем правильное отображение
    row.classList.remove('disabled-row');
    void row.offsetWidth; // Trigger reflow
    if (!enabled) {
        row.classList.add('disabled-row');
    }
}

// Update existing WebSocket handler
socket.on('criteria_updated', function(criteriaData) {
    console.log("CRITERIA UPDATE")
    for (const [category, info] of Object.entries(criteriaData)) {
        const rows = document.querySelectorAll(`tr[data-category="${category}"]`);
        const checkbox = document.getElementById(category);
        
        if (checkbox) {
            checkbox.checked = info.enabled;
        }
        
        rows.forEach(row => {
            updateRowState(row, info.enabled);
            
            const scoreDiv = row.querySelector('.score-indicator');
            if (scoreDiv) {
                const sublevel = row.dataset.sublevel;
                if (sublevel && info.sublevels && info.sublevels[sublevel]) {
                    scoreDiv.textContent = `${info.sublevels[sublevel].score}/${info.sublevels[sublevel].max_score}`;
                    scoreDiv.dataset.score = info.sublevels[sublevel].score;
                } else if (!sublevel) {
                    scoreDiv.textContent = `${info.score}/${info.max_score}`;
                    scoreDiv.dataset.score = info.score;
                }
            }
        });
    }
    updateScoreColors();
});
