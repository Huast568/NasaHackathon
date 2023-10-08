from main import VideotoAudio
from autotune import Autotuner
import numpy as np
from pydub import AudioSegment
from scipy.io import wavfile
import librosa
from tqdm import tqdm

def pydub_to_np(audio: AudioSegment) -> (np.ndarray, int):
    # Convert AudioSegment to raw audio data (bytes)
    audio_data = audio.raw_data
    # Convert raw audio data to NumPy array with dtype int16
    audio_np = np.frombuffer(audio_data, dtype=np.int16)
    # Normalize audio data to the range [-1.0, 1.0]
    audio_np = audio_np / (2**15)
    return audio_np, audio.frame_rate

def main(video_file, channel=2, scale="F#:maj"):
    if channel == 1:
        ### Video to Audio
        vto = VideotoAudio(video_file, output_audio_file='output_audio.wav', channels=1)
        vto.convert()
        vto.save_audio()
        vto.plot_audio_clip()
        ### Autotuner
        autotune = Autotuner(scale=scale)

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
    if channel == 2:
        ### Video to Audio
        vto = VideotoAudio(video_file, output_audio_file='output_audio.wav', channels=2)
        arr = vto.convert()
        vto.save_audio()
        # vto.plot_audio_clip()
        ### Autotuner
        autotune = Autotuner(scale=scale)

        # Load and process the input audio        
        for i in tqdm(range(len(arr))):
            new_sound, sample_rate = pydub_to_np(arr[i])
            arr[i] = AudioSegment(autotune.autotune(new_sound, sample_rate))

        # Overlay (mix) the audio files
        overlay_audio_L = arr[0].overlay(arr[1].overlay(arr[2]))
        overlay_audio_R = arr[3].overlay(arr[4].overlay(arr[5]))

        # Export the overlaid audio to a new WAV file
        overlay_audio_L.export("left_pitch_corrected.wav", format="wav")
        overlay_audio_R.export("right_pitch_corrected.wav", format="wav")

        sample_rate, left_audio = wavfile.read('left_pitch_corrected.wav')
        sample_rate, right_audio = wavfile.read('right_pitch_corrected.wav')
        stereo_audio = np.column_stack((left_audio, right_audio))
        wavfile.write('stereo_audio.wav', sample_rate, stereo_audio)
        sample_rate, stereo_audio = wavfile.read('stereo_audio.wav')
        left_ear_gain = 0.1
        stereo_audio[:, 1] = (stereo_audio[:, 1] * left_ear_gain).astype(np.uint8)
        wavfile.write('stereo_adjusted.wav', sample_rate, stereo_audio)

if __name__ == '__main__':
    main('explosion.mp4')