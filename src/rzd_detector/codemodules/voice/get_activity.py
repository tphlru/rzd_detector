import webrtcvad
import sys
import os
import sounddevice as sd
import soundfile as sf
import numpy as np
from transformers import HubertForSequenceClassification, Wav2Vec2FeatureExtractor
import torchaudio
import tensorflow as tf

feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(os.path.abspath("../models/hubert-rus/hubert-rus-feature-extractor"), low_cpu_mem_usage=True)
model = HubertForSequenceClassification.from_pretrained(os.path.abspath("../models/hubert-rus/hubert-rus-model"), low_cpu_mem_usage=True)

num2emotion = {0: 'neutral', 1: 'angry', 2: 'positive', 3: 'sad', 4: 'other'}

# The WebRTC VAD only accepts 8000, 16000, 32000 or 48000 Hz sample rate.
# (bits per second)
RATE = 48000

DEVICE_INDEX=18

CHANNELS = 1
mapping = [c - 1 for c in [CHANNELS]]

# A frame must be either 10, 20, or 30 ms in duration (0.010 sec)
FRAME_DURATION = 0.030
CHUNK = int(RATE * FRAME_DURATION + 0.5)

# 48000 (bits/sec) / bits in a chunk = number of chunks to fill 1 second of audio
# Batch duration for the voice emotion recognition model (replace 5 here, in sec)
BATCH_DURATION = int(RATE/CHUNK*5)

# Maximum continuous duration of silence in the batch (replace 0.3 here, in sec)
MAX_CONTIN_SILENCE = int(RATE/CHUNK*0.3)

vad = webrtcvad.Vad(2)

bigauudio = [] # main audio (whole)
batch = [] # Current batch (of audio)
batch_values = [] # Also current batch, but only true/false values
formed_batchs = [] # list of full, generated batchs
new_batch_flag = False # Флаг того, что добавился новый batch

speech_end_count = 0 # Счётчик периодов тишины (если больше 4 - закончили речь)

posneg_list = [] # List to collect pos and neg results of chanks

def issublist(x, y):
    """Check if x is sublist of y"""
    return any(y[idx: idx + len(x)] == x
               for idx in range(len(y) - len(x) + 1))

def voice_activity_detection(audio_data):
    return vad.is_speech(audio_data, RATE)

def predict_hubert(filepath):
    waveform, sample_rate = torchaudio.load(filepath, normalize=True)
    transform = torchaudio.transforms.Resample(sample_rate, 16000)
    waveform = transform(waveform)
    inputs = feature_extractor(
        waveform,
        sampling_rate=16000,
        return_tensors="pt",
        padding=True,
        max_length=16000 * 10,
        truncation=True
    )
    probabilities = tf.nn.softmax(model(inputs['input_values'][0]).logits.detach(), axis=-1).numpy().tolist()[0]
    probabilities = {num2emotion[n]: val for (n, val) in enumerate(probabilities)}
    return dict(sorted(probabilities.items(), key=lambda x: x[1], reverse=True))

def audio_callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    global batch, batch_values, formed_batchs, bigauudio, new_batch_flag, speech_end_count

    if status:
        print(f"Warning:{status}", file=sys.stderr)

    assert frames == CHUNK # Extra check
    audio_data = indata[::1, mapping] # downsample

    audio_data = map(lambda x: (x+1)/2, audio_data) # normalize from [-1,+1] to [0,1]
    audio_data = np.fromiter((x[-1] for x in audio_data), np.float16)
    audio_data = audio_data.tobytes()

    detection = voice_activity_detection(audio_data)

    bigauudio.append(indata.copy())

    batch.append(indata.copy()) # Add frame to our batch
    batch_values.append(detection) # Add detection value of this frame

    if issublist([False]*(MAX_CONTIN_SILENCE+1), batch_values):
        del(batch_values[-MAX_CONTIN_SILENCE:])
        del(batch[-MAX_CONTIN_SILENCE:])
        speech_end_count+=1

    # Duration done or Speech (phrase) ended (max silence)
    # End only when phrase finished
    if (len(batch_values) >= BATCH_DURATION and detection is False) or (speech_end_count >= 4 and True in batch_values[:-(MAX_CONTIN_SILENCE*4)]):
        formed_batchs.append(batch) # Add as formed batch
        batch, batch_values = [], [] # Clear current batch
        new_batch_flag = True # Set flag
        speech_end_count = 0

def writeaudio(audio_filename, audio_data, write_blocks=False, rewrite_all=False):
    """Function to write audio to file. If write_blocks (in this mode send only blocks), will append to fille."""
    m = 'w' if rewrite_all else 'r+'
    if os.path.isfile(audio_filename) or write_blocks is False:
        options = {
            "r+": lambda: sf.SoundFile(audio_filename, mode=m),
            "w": lambda: sf.SoundFile(audio_filename, mode=m, samplerate=RATE, channels=CHANNELS),
        }
        with options[m]() as f:
            f.seek(0, sf.SEEK_END)
            if write_blocks:
                f.write(audio_data)
            else:
                for block in audio_data:
                    f.write(block)
    else:
        sf.write(audio_filename, bigauudio[0], RATE, closefd=True)
stream = sd.InputStream(
device=DEVICE_INDEX,
samplerate=RATE,
channels=CHANNELS,
blocksize=CHUNK,
callback=audio_callback,
)

bigaudio_filename = "bigaudio_0.wav"
while os.path.exists(bigaudio_filename):
    i = int(bigaudio_filename.split("_")[-1].split(".")[0])
    bigaudio_filename = "bigaudio_" + str(i+1) + ".wav"
    
with stream:
        while True:
            if new_batch_flag:
                new_batch_flag = False
                writeaudio("batch.wav", formed_batchs[-1], rewrite_all=True)
                posneg_list.append(predict_hubert("batch.wav"))

            if bigauudio:
                writeaudio(bigaudio_filename, bigauudio[0], write_blocks=True) # Write oldest (first)
                bigauudio.pop(0) # Del oldest (first), now the second one is the oldest