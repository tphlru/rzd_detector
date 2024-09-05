let inputs = document.querySelectorAll('input[type=radio], input[type=checkbox]');

// Функция для отправки данных на сервер
function sendData(event) {
    let element = event.target;  // Получаем элемент, вызвавший событие
    let attributes = {};

    // Сохраняем все атрибуты элемента в объект
    for (let attr of element.attributes) {
        attributes[attr.name] = attr.value;
    }
    attributes['checked'] = element.checked;
    attributes['value'] = element.value 

    console.log('Атрибуты элемента:', attributes);

    // Можно использовать эти данные для отправки на сервер
    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(attributes)  // Отправляем все атрибуты на сервер
    })
    .then(response => response.text())
    .then(data => {
        console.log('Ответ сервера:', data);
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}

// Назначаем обработчик на все кнопки и элементы формы
document.querySelectorAll('button, input').forEach(element => {
    element.addEventListener('click', sendData);
});

// Если нужно отслеживать изменения в полях ввода
document.querySelectorAll('input, textarea').forEach(element => {
    element.addEventListener('input', sendData);
});

// Снятие выделения со всех кнопок
for (let i = 0; i < inputs.length; i++) {
    inputs[i].checked = false;
}