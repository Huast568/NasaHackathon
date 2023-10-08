import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from pydub import AudioSegment
from pydub.playback import play
from tqdm import tqdm
from scipy.io import wavfile

class VideotoAudio:
    def __init__(self, video_file, output_audio_file="output_audio.wav", channels=1):
        self.video_file = video_file  # Video file name

        # self.output_video_file = output_video_file  # Output video file name
        self.output_audio_file = output_audio_file  # Output audio file name

        self.cap = cv2.VideoCapture(self.video_file)  # Capture of the video

        self.frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))  # Frame rate of the video
        self.frame_height, self.frame_width, _ = self.get_frame().shape  # Height and width of the video

        self.channels = channels
    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Failed to read the frame")
        return frame
    
    def alter_data(self,data):
        n = self.frame_rate
        processed_left = []
        processed_right = []
        for i in range(self.frame_rate):
            mean = np.mean(data[:,i])
            processed_right.append(mean*i/self.frame_rate)
            processed_left.append(mean*n/self.frame_rate)
            n = n-1
        return processed_left,processed_right

    def generate_sine_wave(self, sample_rate, frequency, duration_seconds, amplitude=10):
        angular_frequency = 2 * np.pi * frequency
        num_samples = int(sample_rate * duration_seconds)
        time_points = np.arange(num_samples) / sample_rate
        audio_data = np.uint8(amplitude * np.sin(angular_frequency * time_points))
        return AudioSegment(audio_data.tobytes(), frame_rate=sample_rate, sample_width=audio_data.itemsize, channels=1)

    def frame_to_audio(self, mean_brightness, speed=1.0):
        original_duration = 1000 / self.frame_rate
        sample_rate = 48000
        frequency = int(np.interp(mean_brightness, [0, 20*255], [65.4, 2093]))
        audio_segment = self.generate_sine_wave(sample_rate, frequency, original_duration)
        modified_duration = original_duration // speed
        audio_segment = audio_segment[:modified_duration]
        return audio_segment

    def convert(self, p_bar=True):
        self.frame_list = []

        #audio clips that will turn into stereo and the final clip
        self.audio_clip_left = None
        self.audio_clip_right = None
        self.audio_clip = None
        
        pbar = tqdm(desc="Processing Audio Frame", total=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)), colour="GREEN", disable=(not p_bar))
        if self.channels == 1:
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
                self.frame_list.append(frame)
        if self.channels == 2:
            self.audio_clip_left = None
            self.audio_clip_right = None

            while True:
                pbar.update(1)
                ret, frame = self.cap.read()
                if not ret:
                    break
                # Convert the frame to audio
                blue_channel, green_channel, red_channel = cv2.split(frame)

                red_alter_left,red_alter_right = self.alter_data(red_channel)

                audio_segment_red_left = self.frame_to_audio(5*np.mean(red_alter_left))
                audio_segment_red_right = self.frame_to_audio(5*np.mean(red_alter_right))

                green_alter_left,green_alter_right = self.alter_data(green_channel)
                audio_segment_green_left = self.frame_to_audio(10*np.mean(green_alter_left))
                audio_segment_green_right = self.frame_to_audio(10*np.mean(green_alter_right))

                blue_alter_left,blue_alter_right = self.alter_data(blue_channel)
                audio_segment_blue_left = self.frame_to_audio(20*np.mean(blue_alter_left))
                audio_segment_blue_right = self.frame_to_audio(20*np.mean(blue_alter_right))

                left = audio_segment_blue_left.overlay(audio_segment_red_left.overlay(audio_segment_green_left))
                right = audio_segment_blue_right.overlay(audio_segment_red_right.overlay(audio_segment_green_right))

                # Append the segment to the main audio clip
                if self.audio_clip_left is None:
                    self.audio_clip_left = left
                else:
                    self.audio_clip_left = self.audio_clip_left + left
                
                if self.audio_clip_right is None:
                   self.audio_clip_right = right
                else:
                    self.audio_clip_right = self.audio_clip_right + right
                self.frame_list.append(frame)


    def plot_audio_clip(self, channel=1):
        if self.channels == 1:
            if self.audio_clip is not None:
                audio_array = np.array(self.audio_clip.get_array_of_samples())
                plt.figure(figsize=(10, 4))
                plt.plot(audio_array)
                plt.title('Audio Clip')
                plt.xlabel('Sample')
                plt.ylabel('Amplitude')
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
        sample_rate, left_audio = wavfile.read('left.wav')
        sample_rate, right_audio = wavfile.read('right.wav')

            # Duplicate the mono audio to create a stereo signal
        stereo_audio = np.column_stack((left_audio, right_audio))

            # Save the stereo audio as a WAV file
        wavfile.write('stereo_audio.wav', sample_rate, stereo_audio)
            # self.output_video.release()
        sample_rate, stereo_audio = wavfile.read('stereo_audio.wav')

        # Define a gain factor for the left ear (0.5 for half volume)
        left_ear_gain = 0.1

        # Apply the gain to the left channel while keeping the right channel unchanged
        stereo_audio[:, 1] = (stereo_audio[:, 1] * left_ear_gain).astype(np.uint8)

        # Save the modified stereo audio as a new WAV file
        wavfile.write('stereo_adjusted.wav', sample_rate, stereo_audio)
    def save_audio(self):
        if self.channels == 1:
            if self.audio_clip is not None:
                self.audio_clip.export(self.output_audio_file, format='wav')
                self.cap.release()
            else:
                Warning("No audio clip available. Please run the 'convert' method first.")
        elif self.channels == 2:
            if self.audio_clip_left is not None and self.audio_clip_right is not None:
                self.audio_clip_left.export("left.wav", format='wav')
                self.audio_clip_right.export("right.wav", format='wav')
                self.cap.release()
            else:
                Warning("No left, right audio clips available. Please run the 'convert' method first.")


def main():
    video_file = os.path.join(os.path.dirname(__file__), 'space_video.mp4')
    vto = VideotoAudio(video_file, output_audio_file='output_audio.wav', channels=2)
    vto.convert(p_bar=True)
    vto.save_audio()
    

if __name__ == "__main__":
    main()
