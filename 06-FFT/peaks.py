import wave, struct
import sys
import numpy as np

window_seconds = 1  # in seconds

filename = sys.argv[1]

with wave.open(filename, mode='rb') as f:
    (nchannels, sample_width, framerate, nframes, _, _) = f.getparams()
    data = f.readframes(nframes)

stereo = True if nchannels == 2 else False
window_frames = int(framerate * window_seconds)
nwindows = nframes // window_frames

def get_window(data, stereo=False):
    counter = 0
    window = []
    data_iterator = struct.iter_unpack('h', data)
    if stereo:
        for integer in data_iterator:
            left = integer[0]
            try:
                right = data_iterator.__next__()[0]
            except StopIteration as si:
                print('Stereo file has odd number of samples!', si)
                break
            window.append((left + right) / 2)
            counter += 1
            if counter == window_frames:
                yield window
                window = []
                counter = 0
    else:
        for integer in data_iterator:
            window.append(integer[0])
            counter += 1
            if counter == window_frames:
                yield window
                window = []
                counter = 0

lowest = np.inf
highest = -np.inf
# c = 1
for window in get_window(data, stereo):
    # print('Processing window {}/{}'.format(c, nwindows))
    amplitudes = np.fft.rfft(window)
    amplitudes = np.abs(amplitudes)
    peaks = np.argwhere(amplitudes >= 20*np.average(amplitudes))
    if len(peaks) > 0:
        if peaks.min() < lowest:    lowest = peaks.min()
        if peaks.max() > highest:   highest = peaks.max()
    # c+=1

if np.isfinite(lowest) and np.isfinite(highest):
    print('low = {}, high = {}'.format(lowest, highest))
else:
    print('no peaks')
