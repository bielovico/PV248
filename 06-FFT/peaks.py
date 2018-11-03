import math, wave, array, struct
import numpy as np

frequency = 440  # Hz

window_length = 0.1  # in seconds


with wave.open('06-FFT\\sounds\\Sinus_{}Hz.wav'.format(frequency), mode='rb') as f:
    (nchannels, sample_width, framerate, nframes, _, _) = f.getparams()
    data = f.readframes(nframes)

samples = []
for integer in struct.iter_unpack('h', data):
    samples.append(integer[0])

amplitudes = np.fft.rfft(samples)
amplitudes = np.abs(amplitudes)

peaks = np.argwhere(amplitudes >= 20*np.average(amplitudes))


print(peaks)





