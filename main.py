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

    def generate_sine_wave(self, sample_rate, frequency, duration_seconds, amplitude=100):
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

    def convert(self, time_taken=False):
        self.frame_list = []
        self.audio_clip = None
        
        pbar = tqdm(desc="Processing Audio Frame", total=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)), colour="GREEN", disable=(not time_taken))
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
            # self.output_video.write(frame)

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
            print("No audio clip available. Please run the 'convert' method first.")

    def save_audio(self):
        if self.audio_clip is not None:
            self.audio_clip.export(self.output_audio_file, format='wav')
            self.cap.release()
            # self.output_video.release()
        else:
            print("No audio clip available. Please run the 'convert' method first.")

def main():
    video_file = os.path.join(os.path.dirname(__file__), 'fireworks.mp4')
    vto = VideotoAudio(video_file, output_video_file='output_video.mp4', output_audio_file='output_audio.wav')
    vto.convert(time_taken=True)
    vto.save_audio()
    play(vto.audio_clip)
    

if __name__ == "__main__":
    main()
