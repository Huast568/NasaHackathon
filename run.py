import main, autotune
import numpy as np
from pydub import AudioSegment
from scipy.io import wavfile

if __name__ == '__main__':
    channel = 2
    if channel == 1:
        main.main()
        autotune.main()
    if channel == 2:
        main.main()
        autotune.main()
        audio1_L = AudioSegment.from_file("left_R_pitch_corrected.wav", format="wav")
        audio2_L = AudioSegment.from_file("left_G_pitch_corrected.wav", format="wav")
        audio3_L = AudioSegment.from_file("left_B_pitch_corrected.wav", format="wav")

        audio1_R = AudioSegment.from_file("right_R_pitch_corrected.wav", format="wav")
        audio2_R = AudioSegment.from_file("right_G_pitch_corrected.wav", format="wav")
        audio3_R = AudioSegment.from_file("right_B_pitch_corrected.wav", format="wav")

        # Overlay (mix) the audio files
        overlay_audio_L = audio1_L.overlay(audio2_L.overlay(audio3_L))
        overlay_audio_R = audio1_R.overlay(audio2_R.overlay(audio3_R))

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
