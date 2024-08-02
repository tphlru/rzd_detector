# импорты
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import librosa
import pyworld as pw
import amfm_decompy.basic_tools as basic
import amfm_decompy.pYAAPT as pYAAPT


# функции
def get_midpoints(seq):
    win_size = 2
    wins = []
    for i in range(len(seq) - win_size + 1):
        wins.append(seq[i : i + win_size])
    return [(f + s) / 2 for f, s in wins]


def get_top_values_n(raw_data, n):
    tops_values = raw_data
    for _ in range(n):
        midpoints = get_midpoints(tops_values)
        tops = get_plot_tops(midpoints, tops_values)
        tops_values = [i[1] for i in tops]
    return midpoints, tops


def get_plot_tops(dividing_line, seq):
    win_size = 2
    tops = []
    for n, (i, v) in enumerate(zip(range(len(dividing_line) - win_size + 2), seq)):
        if v > (max(list(dividing_line[i : i + win_size]))):
            tops.append([n, v])
    return tops


def get_trend(x):
    y = list(range(len(x)))
    result = np.polyfit(y, x, 1)
    plt.plot(result, list(range(len(result))), color="brown")
    plt.scatter(tnums, tvals, marker="o", color="g", zorder=2)
    plt.grid(True)
    plt.show()


# чтение записи
raw_rec, fs = librosa.load(r"c:\Users\Georges\Downloads\voice7.wav", dtype=np.float64)
# первичная обработка
f0, sp, ap = pw.wav2world(raw_rec, fs)
new_zapis = pw.synthesize(f0, sp, ap, fs, pw.default_frame_period)
# вторичная обработка
signal = basic.SignalObj(new_zapis, fs)
pitchY = pYAAPT.yaapt(
    signal,
    median_value=3,  # 23
    bp_forder=160,
    shc_numharms=3,
    nccf_maxcands=4,
    nccf_thresh2=1,
    nlfer_thresh1=0.26,  # voiced / unvoiced 0.26
    shc_thresh1=12,
    shc_thresh2=0.7,
    dp_w2=2.5,
    dp_w4=0.3,
)
x = pitchY.samp_values
# выявление средних и максимальных точек
for iteration in range(1, 8):
    mids, tops = get_top_values_n(x, iteration)
    tvals = [i[1] for i in tops]
    tnums = [i[0] for i in tops]
    if len(tops) < 50:
        break

get_trend(tvals)
print(tvals)
# for i in mids:
#     if i == mids[0]:
#         pastvalue = i
#         pastchange = 1
#         continue
#     else:
#         changes.append(i)
#         avr += i
#         pastvalue = i
# avr = avr/len(changes)


# plt.plot(list([(i+1 + i) / 2 for i in range(len(mids))]), mids, marker="x", color='r', zorder=1)
# plt.grid(True)
