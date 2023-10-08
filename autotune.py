import librosa
import numpy as np
from pydub import AudioSegment
import scipy.signal as sig
from functools import partial
from pathlib import Path
import argparse
import soundfile as sf
import psola

SEMITONES_IN_OCTAVE=12

# Taking in an input frequency and returning a corrected frequency adjusted to the closest frequency on a scale
def correct(f0): 
    # Check for NAN (not-a-number) values in the input pitch; if they exist, return them
    if np.isnan(f0):
        return np.nan
    # Define the degrees of the scale and specify in the actual parameter
    c_minor_degrees = librosa.key_to_degrees('B:maj')
    # Duplicate the first degree to complete an octave
    c_minor_degrees = np.concatenate((c_minor_degrees, [c_minor_degrees[0] + 12]))
    # Convert the input pitch to MIDI note value
    midi_note=librosa.hz_to_midi(f0)
    # Calculate/aproximate the degree of the MIDI note in the scale
    degree = midi_note % 12
    # Round the degree to the closest degree in the aforementioned scale
    closest_degree_id = np.argmin(np.abs(c_minor_degrees - degree))
    # Calculate the difference in degrees between the tuned and the original degrees
    degree_difference=degree - c_minor_degrees [closest_degree_id]
    # Adjust the MIDI note to the closest note in the scale
    midi_note -= degree_difference
    # Return the converted MIDI note frequency
    return librosa.midi_to_hz(midi_note)

# Corrects the pitch for an array of pitch values
def correct_pitch(f0):
    # Initialize an array to store corrected frequencies
    corrected_f0 = np.zeros_like(f0)
    # Loop through each pitch value in input array and correct the pitch values
    for i in range (f0.shape[0]):
        corrected_f0[i] = correct(f0[i])
    # Smooth the corrected pitch values with a median filter
    smoothed_corrected_f0=sig.medfilt(corrected_f0, kernel_size=11)
    # Replace NAN values in the smoothed pitch with the original corrected values
    smoothed_corrected_f0[np.isnan (smoothed_corrected_f0)]=corrected_f0[np.isnan (smoothed_corrected_f0)]
    # Return the smoothed and corrected pitch values
    return smoothed_corrected_f0


def autotune(audio, sr):
    # Set some basis parameters: 
    # Length of analysis frame
    frame_length = 2048
    # Number of samples between frames
    hop_length = frame_length // 4
    # Minimum and maximum frequencies (limits)
    fmin = librosa.note_to_hz('C2')
    fmax = librosa.note_to_hz('C7')

    # Pitch tracking using the PYIN algorithm
    f0, voiced_flag, voiced_probabilities = librosa.pyin(audio,
                                                         frame_length=frame_length,
                                                         hop_length=hop_length,
                                                         sr=sr,
                                                         fmin=fmin,
                                                         fmax=fmax)

    # Correct the pitch for f0
    corrected_f0 = correct_pitch(f0)

    # Pitch-shifting using the PSOLA algorithm
    return psola.vocode(audio, sample_rate=int(sr), target_pitch=corrected_f0, fmin=fmin, fmax=fmax)

def main():
    arr = ["left.wav", "right.wav"]
    for i in range (len(arr)):
        filepath = Path(arr[i])

    # Load the audio file.
        y, sr = librosa.load(arr[i], sr=None, mono=False)

    # Only mono-files are handled. If stereo files are supplied, only the first channel is used.
        if y.ndim > 1:
            y = y[0, :]


    # Perform the auto-tuning.
        pitch_corrected_y = autotune(y, sr)

    # Write the corrected audio to an output file.
        output_filepath = filepath.parent / (filepath.stem + '_pitch_corrected' + filepath.suffix)
        sf.write(str(output_filepath), pitch_corrected_y, sr)

    
if __name__=='__main__':
    main()