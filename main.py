import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from pydub import AudioSegment
from pydub.playback import play
from tqdm import tqdm

class VideotoAudio:
    def __init__(self, video_file, output_video_file="output_video.mp4", output_audio_file="output_audio.wav"):
        self.video_file = video_file  # Video file name

        # self.output_video_file = output_video_file  # Output video file name
        self.output_audio_file = output_audio_file  # Output audio file name

        self.cap = cv2.VideoCapture(self.video_file)  # Capture of the video

        self.frame_rate = int(self.cap.get(cv2.CAP_PROP_FPS))  # Frame rate of the video
        self.frame_height, self.frame_width, _ = self.get_frame().shape  # Height and width of the video

        # self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Fourcc code of the video
        # self.output_video = cv2.VideoWriter(self.output_video_file, self.fourcc, self.frame_rate, (self.frame_width, self.frame_height))

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Failed to read the frame")
        return frame

    def alter_data(self, width, data, direction):
        n = width
        processed_x = []
        if (direction == 'right'):
            for i in range(width):
                processed_x.append(np.mean(data[:,i])*i/width)
        else:
            for i in range(width):
                processed_x.append(np.mean(data[:,i])*n/width)
                n = n-1
        return processed_x
    
    def generate_sine_wave(self, sample_rate, frequency, duration_seconds, amplitude=10):
        angular_frequency = 2 * np.pi * frequency
        num_samples = int(sample_rate * duration_seconds)
        time_points = np.arange(num_samples) / sample_rate
        audio_data = np.uint8(amplitude * np.sin(angular_frequency * time_points))
        return AudioSegment(audio_data.tobytes(), frame_rate=sample_rate, sample_width=audio_data.itemsize, channels=1)

    def frame_to_audio(self, frame, speed=1.0):
        mean_brightness = np.mean(frame)
        original_duration = 1000 / self.frame_rate
        sample_rate = 48000
        frequency = int(np.interp(mean_brightness, [0, 255], [100, 1000]))
        audio_segment = self.generate_sine_wave(sample_rate, frequency, original_duration)
        modified_duration = original_duration // speed
        audio_segment = audio_segment[:modified_duration]
        return audio_segment

    def convert(self, channels=1):
        self.frame_list = []
        self.audio_clip = None
        
        pbar = tqdm(desc="Processing Audio Frame", total=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)), colour="GREEN")
        if channels == 1:
            while True:
                pbar.update(1)
                ret, frame = self.cap.read()
                if not ret:
                    break
                audio_segment = self.frame_to_audio(frame)
                if self.audio_clip is None:
                    self.audio_clip = audio_segment
                else:
                    self.audio_clip += audio_segment
                self.frame_list.append(frame)

        elif channels == 2:
            self.audio_clip_left = None
            self.audio_clip_right = None

            while True:
                pbar.update(1)
                ret, frame = self.cap.read()
                if not ret:
                    break
                # Convert the frame to audio
                blue_channel, green_channel, red_channel = cv2.split(frame)

                red_alter_right = self.alter_data(self.frame_width, red_channel,'right')
                red_alter_left = self.alter_data(self.frame_width, red_channel,'left')
                audio_segment_red_left = self.frame_to_audio(red_alter_left, self.frame_rate)
                audio_segment_red_right = self.frame_to_audio(red_alter_right, self.frame_rate)

                green_alter_right = self.alter_data(self.frame_width, green_channel,'right')
                green_alter_left = self.alter_data(self.frame_width, green_channel,'left')
                audio_segment_green_left = self.frame_to_audio(green_alter_left, self.frame_rate)
                audio_segment_green_right = self.frame_to_audio(green_alter_right, self.frame_rate)

                blue_alter_right = self.alter_data(self.frame_width, blue_channel,'right')
                blue_alter_left = self.alter_data(self.frame_width, blue_channel,'left')
                audio_segment_blue_left = self.frame_to_audio(blue_alter_left, self.frame_rate)
                audio_segment_blue_right = self.frame_to_audio(blue_alter_right, self.frame_rate)

                # Append the segment to the main audio clip
                if self.audio_clip_left is None:
                    self.audio_clip_left = audio_segment_red_left + audio_segment_blue_left+audio_segment_green_left
                else:
                    self.audio_clip_left = self.audio_clip_left + audio_segment_red_left+audio_segment_blue_left+audio_segment_green_left
                
                if self.audio_clip_right is None:
                   self.audio_clip_right = audio_segment_red_right+audio_segment_green_right+audio_segment_blue_right
                else:
                    self.audio_clip_right = self.audio_clip_right + audio_segment_red_right+audio_segment_green_right+audio_segment_blue_right
                self.frame_list.append(frame)

    def plot_audio_clip(self):
        audio_array = np.array(self.audio_clip.get_array_of_samples())
        if self.audio_clip is not None:
            plt.figure(figsize=(10, 4))
            plt.plot(audio_array)
            plt.title('Audio Clip')
            plt.xlabel('Sample')
            plt.ylabel('Amplitude')
            plt.grid(True)
            plt.show()
        else:
            Warning("No audio clip available. Please run the 'convert' method first.")

    def save_audio(self, channels=1):
        if channels == 1:
            if self.audio_clip is not None:
                self.audio_clip.export(self.output_audio_file, format='wav')
                self.cap.release()
            else:
                Warning("No audio clip available. Please run the 'convert' method first.")
        elif channels == 2:
            if self.audio_clip_left is not None and self.audio_clip_right is not None:
                self.audio_clip_left.export("left.wav", format='wav')
                self.audio_clip_right.export("right.wav", format='wav')
                self.cap.release()
            else:
                Warning("No left, right audio clips available. Please run the 'convert' method first.")


def main():
    video_file = os.path.join(os.path.dirname(__file__), 'space_video.mp4')
    vto = VideotoAudio(video_file, output_video_file='output_video.mp4', output_audio_file='output_audio.wav')
    vto.convert(channels=1)
    vto.save_audio(channels=1)
    # play(vto.audio_clip)
    

if __name__ == "__main__":
    main()
