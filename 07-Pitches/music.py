import wave, struct
import sys
from math import log2, floor
import numpy as np

window_seconds = 1  # in seconds
# frequency_precision = 1 / window_seconds
window_slide = 0.1  # in seconds

noutputs = 3

standard_pitch = sys.argv[1]
filename = sys.argv[2]

c0 = int(standard_pitch)*(2**(-9/12 - 4))

pitches_names = ["c", "cis", "d", "es", "e", "f", "fis", "g", "gis", "a", "bes", "b"]

with wave.open(filename, mode='rb') as f:
    (nchannels, sample_width, framerate, nframes, _, _) = f.getparams()
    data = f.readframes(nframes)

stereo = True if nchannels == 2 else False
window_frames = int(framerate * window_seconds)
slide_frames = int(framerate * window_slide)
nwindows = nframes // slide_frames
nwindows -= window_seconds // window_slide

def closest_pitch(frequency):
    steps = 12*log2(frequency/c0)
    octave = round(steps) // 12
    note = round(steps) % 12
    cents = round((steps - round(steps)) * 100)
    pitch = pitches_names[note]
    if octave <= 2:
        pitch = pitch.capitalize()
        pitch += ',' * (2 - octave)
    else:
        pitch += "'" * (octave - 3)
    if cents < 0:
        pitch += str(cents)
    else:
        pitch += '+' + str(cents)
    return pitch

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
                window = window[slide_frames:]
                counter -= slide_frames
    else:
        for integer in data_iterator:
            window.append(integer[0])
            counter += 1
            if counter == window_frames:
                yield window
                window = window[slide_frames:]
                counter -= slide_frames

def get_pitches(window):
    amplitudes = np.fft.rfft(window)
    amplitudes = np.abs(amplitudes)
    over_avg = amplitudes >= 20*np.average(amplitudes)
    peaks = np.where(over_avg)[0]
    amps = amplitudes[over_avg]
    peak_amps = sorted(list(zip(peaks, amps)), key=lambda x: x[1], reverse=True)
    n = min(len(peaks), noutputs)
    output = []
    for _ in range(n):
        peak, amp = peak_amps[0]
        ps, center = find_cluster(peak, over_avg)
        if len(peak_amps) < 2:
            output.append(peak)
            break
        npeak, namp = peak_amps[1]
        i = 1
        while namp == amp:
            if npeak not in ps:
                continue
            if abs(center-npeak) < abs(center-peak):
                peak = npeak
            i += 1
            if len(peak_amps) < i+1:
                break
            npeak, namp = peak_amps[i]
        output.append(peak)
        peak_amps = [(peak, amps) for peak, amps in peak_amps if peak not in ps]
    pitches = []
    for p in sorted(output):
        pitches.append(closest_pitch(p))
    return pitches

def find_cluster(peak, peaks):
    ps = [peak]
    center = peak
    found = True
    i = 0
    while found:
        found = False
        i += 1
        if peak-i > 0:
            left = peaks[peak-i]
        else:
            left = False
        if peak+i < len(peaks):
            right = peaks[peak+i]
        else:
            right = False
        if left:
            ps.append(peak-i)
            center -= 0.5
            found = True
        if right:
            ps.append(peak+i)
            center += 0.5
            found = True
    return ps, center

def print_segment(start, end, pitches):
    out = '{:04.2f}-{:04.2f}'.format(start, end)
    for p in pitches:
        out += ' ' + p 
    print(out)

# c = 1
position = 0
segment_start = None
inSegment = False
current_pitches = []
for window in get_window(data, stereo):
    # print('Processing window {}/{}'.format(c, nwindows))
    pitches = get_pitches(window)
    if len(pitches) > 0:
        if not inSegment:
            segment_start = position
            inSegment = True
            current_pitches = pitches
        elif pitches == current_pitches:
            pass
        else:
            print_segment(segment_start, position, current_pitches)
            segment_start = position
            current_pitches = pitches
    elif inSegment:
        print_segment(segment_start, position, current_pitches)
        segment_start = None
        current_pitches = []
    else:
        pass
    # c += 1
    position += window_slide
if inSegment:
    print_segment(segment_start, position, current_pitches)

