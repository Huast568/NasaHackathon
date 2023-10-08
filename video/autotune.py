import librosa
import numpy as np
import scipy.signal as sig
from pathlib import Path
import soundfile as sf
import psola

class Autotuner:
    def __init__(self, scale):
        self.scale = scale

    # Taking in an input frequency and returning a corrected frequency adjusted to the closest frequency on a scale
    def correct(self, f0): 
        if np.isnan(f0):
            return np.nan
        #degrees = librosa.key_to_degrees(self.scale)
        #pentatonic degrees
        degrees = [6, 8, 10, 1, 3]
        degrees = np.concatenate((degrees, [degrees[0] + 12]))
        midi_note=librosa.hz_to_midi(f0)
        degree = midi_note % 12
        closest_degree_id = np.argmin(np.abs(degrees - degree))
        degree_difference=degree - degrees [closest_degree_id]
        midi_note -= degree_difference
        return librosa.midi_to_hz(midi_note)

    # Corrects the pitch for an array of pitch values
    def correct_pitch(self):
        # Initialize an array to store corrected frequencies
        corrected_f0 = np.zeros_like(self.f0)
        # Loop through each pitch value in input array and correct the pitch values
        for i in range (self.f0.shape[0]):
            corrected_f0[i] = self.correct(self.f0[i])
        # Smooth the corrected pitch values with a median filter
        smoothed_corrected_f0=sig.medfilt(corrected_f0, kernel_size=11)
        # Replace NAN values in the smoothed pitch with the original corrected values
        smoothed_corrected_f0[np.isnan (smoothed_corrected_f0)]=corrected_f0[np.isnan (smoothed_corrected_f0)]
        # Return the smoothed and corrected pitch values
        return smoothed_corrected_f0

    def autotune(self, audio, sr):

        frame_length = 2048
        # Number of samples between frames
        hop_length = frame_length // 4
        # Minimum and maximum frequencies (limits)
        fmin = librosa.note_to_hz('C0')
        fmax = librosa.note_to_hz('B8')

        # Pitch tracking using the PYIN algorithm
        self.f0, voiced_flag, voiced_probabilities = librosa.pyin(audio,
                                                            frame_length=frame_length,
                                                            hop_length=hop_length,
                                                            sr=sr,
                                                            fmin=fmin,
                                                            fmax=fmax)

        # Correct the pitch for f0
        corrected_f0 = self.correct_pitch()

        # Pitch-shifting using the PSOLA algorithm
        return psola.vocode(audio, sample_rate=int(sr), target_pitch=corrected_f0, fmin=fmin, fmax=fmax)

def main():

    autotune = Autotuner(scale='F#:maj')

    # Load and process the input audio

    arr = ["left_R.wav", "left_G.wav", "left_B.wav", "right_R.wav", "right_R.wav", "right_G.wav", "right_B.wav"]
    for i in range (len(arr)):
        input_filepath = Path(arr[i])
        y, sr = librosa.load(arr[i], sr=None, mono=True)

        if y.ndim > 1:
            y = y[0, :]

        pitch_corrected_y = autotune.autotune(y, sr)

    # Specify the output file path and write the corrected audio
        output_filepath = input_filepath.parent / (input_filepath.stem + '_pitch_corrected' + input_filepath.suffix)
        sf.write(output_filepath, pitch_corrected_y, sr)
        

if __name__=='__main__':
    main()