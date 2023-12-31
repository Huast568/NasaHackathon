import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from pydub import AudioSegment
from pydub.playback import play
from tqdm import tqdm
from scipy.io import wavfile
from scipy.signal import butter, lfilter

class VideotoAudio:
    def __init__(self, video_file, output_audio_file="output_audio.wav", channels=1):
        self.video_file = video_file  # Video file name

        # self.output_video_file = output_video_file  # Output video file name
        self.output_audio_file = output_audio_file  # Output audio file name

        self.cap = cv2.VideoCapture(self.video_file)  # Capture of the video

        self.frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))  # Frame rate of the video
        self.frame_height, self.frame_width, _ = self.get_frame().shape  # Height and width of the video

        self.channels = channels
        self.audio_data = None

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Failed to read the frame")
        return frame
    
    def alter_data(self,data):
        n = self.frame_width
        processed_left = []
        processed_right = []
        for i in range(self.frame_width):
            mean = np.mean(data[:,i])
            processed_right.append(mean*i/self.frame_width)
            processed_left.append(mean*n/self.frame_width)
            n = n-1
        return processed_left,processed_right
    
    def filter_audio(self, audio_segment, cutoff_frequency, fs=44100):
        if audio_segment is None:
            raise ValueError("No audio data available for filtering")

        # Convert the PyDub audio segment to NumPy array
        audio_data = np.array(audio_segment.get_array_of_samples())

        audio_data_normalized = (audio_data.astype(np.float32) - 127.5) / 127.5
        nyquist_frequency = 0.5 * fs
        normal_cutoff = cutoff_frequency / nyquist_frequency
        b, a = butter(4, normal_cutoff, btype='high', analog=False)
        filtered_audio_normalized = lfilter(b, a, audio_data_normalized)
        
        # Convert the filtered audio back to the original data type
        filtered_audio = (filtered_audio_normalized * 127.5 + 127.5).astype(np.uint8)
        
        # Create a new PyDub AudioSegment from the filtered audio data
        filtered_audio_segment = AudioSegment(filtered_audio.tobytes(),
                                              frame_rate=fs,
                                              sample_width=filtered_audio.itemsize,
                                              channels=audio_segment.channels)

        return filtered_audio_segment

    def generate_sine_wave(self, sample_rate, frequency, duration_seconds, amplitude=10):
        angular_frequency = 2 * np.pi * frequency
        num_samples = int(sample_rate * duration_seconds)
        time_points = np.arange(num_samples) / sample_rate
        audio_data = np.uint8(amplitude * np.sin(angular_frequency * time_points))
        return AudioSegment(audio_data.tobytes(), frame_rate=sample_rate, sample_width=audio_data.itemsize, channels=1)
        
    def frame_to_audio(self, mean_brightness, speed=1.0):
        original_duration = 1000 / self.frame_rate
        sample_rate = 44100
        frequency = int(np.interp(mean_brightness, [0, 255], [200, 900]))
        audio_segment = self.generate_sine_wave(sample_rate, frequency, original_duration)
        modified_duration = original_duration // speed
        audio_segment = audio_segment[:modified_duration]
        return audio_segment

    def convert(self, p_bar=True):        
        pbar = tqdm(desc="Processing Audio Frame", total=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)), colour="GREEN", disable=(not p_bar))
        if self.channels == 1:
            self.audio_clip = None
            while True:
                pbar.update(1)
                ret, frame = self.cap.read()
                if not ret:
                    break
                audio_segment = self.frame_to_audio(np.mean(frame))
                if self.audio_clip is None:
                    self.audio_clip = audio_segment
                else:
                    self.audio_clip += audio_segment
            self.audio_clip = self.filter_audio(self.audio_clip, 100)
        elif self.channels == 2:
            self.audio_clip_left_R = None
            self.audio_clip_right_R = None
            self.audio_clip_left_G = None
            self.audio_clip_right_G = None
            self.audio_clip_left_B = None
            self.audio_clip_right_B = None

            while True:
                pbar.update(1)
                ret, frame = self.cap.read()
                if not ret:
                    print("running")
                    self.audio_clip_left_R.export('left_R.wav', format='wav')
                    self.audio_clip_left_G.export(out_f='left_G.wav', format='wav')
                    self.audio_clip_left_B.export(out_f='left_B.wav', format='wav')
                    self.audio_clip_right_R.export(out_f='right_R.wav',format='wav')
                    self.audio_clip_right_G.export(out_f='right_G.wav',format='wav')
                    self.audio_clip_right_B.export(out_f='right_B.wav',format='wav')
                    break

                # Convert the frame to audio
                blue_channel, green_channel, red_channel = cv2.split(frame)

                red_alter_left,red_alter_right = self.alter_data(red_channel)

                audio_segment_red_left = self.frame_to_audio(np.mean(red_alter_left))
                audio_segment_red_right = self.frame_to_audio(np.mean(red_alter_right))

                green_alter_left,green_alter_right = self.alter_data(green_channel)
                audio_segment_green_left = self.frame_to_audio(np.mean(green_alter_left))
                audio_segment_green_right = self.frame_to_audio(np.mean(green_alter_right))

                blue_alter_left,blue_alter_right = self.alter_data(blue_channel)
                audio_segment_blue_left = self.frame_to_audio(np.mean(blue_alter_left))
                audio_segment_blue_right = self.frame_to_audio(np.mean(blue_alter_right))

                left = audio_segment_blue_left.overlay(audio_segment_red_left.overlay(audio_segment_green_left))
                right = audio_segment_blue_right.overlay(audio_segment_red_right.overlay(audio_segment_green_right))

                # Append the segment to the main audio clip
                if self.audio_clip_left_R is None:
                    self.audio_clip_left_R = audio_segment_red_left
                    self.audio_clip_left_G = audio_segment_green_left
                    self.audio_clip_left_B = audio_segment_blue_left
                else:
                    self.audio_clip_left_R = self.audio_clip_left_R + audio_segment_red_left
                    self.audio_clip_left_G = self.audio_clip_left_G + audio_segment_green_left
                    self.audio_clip_left_B = self.audio_clip_left_B + audio_segment_blue_left
                
                if self.audio_clip_right_R is None:
                    self.audio_clip_right_R = audio_segment_red_right
                    self.audio_clip_right_G = audio_segment_green_right
                    self.audio_clip_right_B = audio_segment_blue_right
                else:
                    self.audio_clip_right_R = self.audio_clip_right_R + audio_segment_red_right
                    self.audio_clip_right_G = self.audio_clip_right_G + audio_segment_green_right
                    self.audio_clip_right_B = self.audio_clip_right_B + audio_segment_blue_right

    def plot_audio_clip(self):
        if self.channels == 1:
            if self.audio_clip is not None:
                audio_array = np.array(self.audio_clip.get_array_of_samples())
                plt.figure(figsize=(10, 4))
                plt.plot(audio_array)
                plt.title('Audio Clip')
                plt.xlabel('Sample')
                plt.ylabel('Amplitude')
                plt.ylim(-150, 150)
                plt.xlim(0, 10000)
                plt.grid(True)
                plt.show()
            else:
                print("No audio clip available. Please run the 'convert' method first.")
        if self.channels == 2:
            if self.audio_clip_left is not None and self.audio_clip_right is not None:
                audio_array_left = np.array(self.audio_clip_left.get_array_of_samples())
                audio_array_right = np.array(self.audio_clip_right.get_array_of_samples())
                plt.figure(figsize=(10, 4))
                plt.plot(audio_array_left, label='Left Channel')
                plt.plot(audio_array_right, label='Right Channel')
                plt.title('Audio Clip')
                plt.xlabel('Sample')
                plt.ylabel('Amplitude')
                plt.grid(True)
                plt.show()
            else:
                print("No audio clip available. Please run the 'convert' method first.")

    def save_audio(self):
        if self.channels == 1:
            if self.audio_clip is not None:
                self.audio_clip.export(self.output_audio_file, format='wav')
                self.cap.release()
            else:
                Warning("No audio clip available. Please run the 'convert' method first.")


def main():
    video_file = os.path.join(os.path.dirname(__file__), 'milky_way.mp4')
    vto = VideotoAudio(video_file, output_audio_file='output_audio.wav', channels=2)
    vto.convert()
    vto.save_audio()

if __name__ == "__main__":
    main()
