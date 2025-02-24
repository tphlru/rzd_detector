var ws = new WebSocket("ws://localhost:8888/ws"); // Инициализируем WebSocket
var isRecording = false;
var mh = null; // Глобальная переменная для MediaHandler

// Функция для переключения записи
function toggleRecord() {
    if (!mh) {
        // Создаём объект MediaHandler при первом запуске
        var processor = new OpusEncoderProcessor(ws);
        mh = new MediaHandler(processor);
    }

    // Начинаем или останавливаем запись в зависимости от текущего состояния
    if (isRecording) {
        stopRecord();
    } else {
        startRecord();
    }
}

// Функция для начала записи
function startRecord() {
    if (!mh.context) {
        console.error("AudioContext не инициализирован");
        return;
    }
    console.log('Начало записи...');
    isRecording = true;
    document.getElementById('record').innerText = "Stop Recording";
}

// Функция для остановки записи
function stopRecord() {
    console.log('Остановка записи...');
    isRecording = false;
    document.getElementById('record').innerText = "Record";
}

// Класс для обработки аудиопроцессора
var OpusEncoderProcessor = function(wsh) {
    this.wsh = wsh;
    this.bufferSize = 4096; // для webaudio script processor
    this.downSample = 2;
    this.opusFrameDur = 60; // msec
    this.opusRate = 24000;
    this.i16arr = new Int16Array(this.bufferSize / this.downSample);
    this.f32arr = new Float32Array(this.bufferSize / this.downSample);
    this.opusEncoder = new OpusEncoder(this.opusRate, 1, 2049, this.opusFrameDur);
};

OpusEncoderProcessor.prototype.onAudioProcess = function(e) {
    if (isRecording) {
        var data = e.inputBuffer.getChannelData(0);
        var i = 0, ds = this.downSample;

        if (encode) {
            for (var idx = 0; idx < data.length; idx += ds) {
                this.f32arr[i++] = data[idx];
            }

            var res = this.opusEncoder.encode_float(this.f32arr);

            for (var idx = 0; idx < res.length; ++idx) {
                this.wsh.send(res[idx]);
            }
        } else {
            for (var idx = 0; idx < data.length; idx += ds) {
                this.i16arr[i++] = data[idx] * 0xFFFF; // int16
            }

            this.wsh.send(this.i16arr);
        }
    }
};

// Класс для управления MediaHandler
var MediaHandler = function(audioProcessor) {
    var AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) {
        alert("Ваш браузер не поддерживает Web Audio API");
        return;
    }

    this.context = new AudioContext();
    this.audioProcessor = audioProcessor;

    // Запрашиваем доступ к микрофону
    navigator.mediaDevices.getUserMedia({ audio: true })
    .then(this.callback.bind(this))
    .catch(this.error);
};

// Callback при успешном получении доступа к микрофону
MediaHandler.prototype.callback = function(stream) {
    console.log('Инициализация микрофона...');
    this.micSource = this.context.createMediaStreamSource(stream);
    this.processor = this.context.createScriptProcessor(this.audioProcessor.bufferSize, 1, 1);
    this.processor.onaudioprocess = this.audioProcessor.onAudioProcess.bind(this.audioProcessor);
    this.micSource.connect(this.processor);
    this.processor.connect(this.context.destination);
    console.log('Микрофон инициализирован');
};

// Обработка ошибок при доступе к микрофону
MediaHandler.prototype.error = function(err) {
    console.error("Ошибка доступа к микрофону", err);
    alert("Проблема при доступе к микрофону: " + err.message);
};
