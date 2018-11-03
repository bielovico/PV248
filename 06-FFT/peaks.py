import math, wave, array, struct
import numpy as np

frequency = 440  # Hz

window_seconds = 1  # in seconds

with wave.open('06-FFT\\sounds\\Sinus_{}Hz.wav'.format(frequency), mode='rb') as f:
    (nchannels, sample_width, framerate, nframes, _, _) = f.getparams()
    data = f.readframes(nframes)

window_frames = int(framerate * window_seconds)

def get_window(data):
    counter = 0
    window = []
    for integer in struct.iter_unpack('h', data):
        window.append(integer[0])
        counter += 1
        if counter == window_frames:
            yield window
            window = []
            counter = 0

lowest = np.inf
highest = -np.inf
for window in get_window(data):
    amplitudes = np.fft.rfft(window)
    amplitudes = np.abs(amplitudes)
    peaks = np.argwhere(amplitudes >= 20*np.average(amplitudes))
    if peaks.min() < lowest:    lowest = peaks.min()
    if peaks.max() > highest:   highest = peaks.max()

if np.isfinite(lowest) and np.isfinite(highest):
    print('low = {}, high = {}'.format(lowest, highest))
else:
    print('no peaks')
