import cv2
import numpy as np
from pydub import AudioSegment
import time, os

# Input video file
video_file = os.path.join(os.path.dirname(__file__), 'space_video.mp4')

#load video
cap = cv2.VideoCapture(video_file)
frame_rate = int(cap.get(cv2.CAP_PROP_FPS))  # Get the frame rate of the video

# Read the first frame to get its shape
ret, frame = cap.read()
if not ret:
    raise ValueError("Failed to read the first frame")

# Get frame dimensions
frame_height, frame_width, _ = frame.shape

#code run time
start_time = time.time()

def alter_data(width,data,direction):
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

def generate_sine_wave(frame_rate, frequency, duration_seconds, amplitude=100):
    angular_frequency = 2 * np.pi * frequency
    num_samples = int(frame_rate * duration_seconds)
    time_points = np.arange(num_samples) / frame_rate  # Generate time points in seconds
    audio_data = np.uint8(amplitude * np.sin(angular_frequency * time_points))
    return AudioSegment(audio_data.tobytes(), frame_rate=frame_rate, sample_width=audio_data.itemsize, channels=1)

def frame_to_audio(data, frame_rate, speed=1.0):
    # Calculate the mean brightness of the frame
    mean_brightness = np.mean(data)
    print(mean_brightness)

    # Define the parameters for the audio segment
    original_duration = 1000 / frame_rate  # Duration in milliseconds (adjust as needed)
    sample_rate = 44100  # Audio sample rate (44.1 kHz is common)

    frequency = int(np.interp(mean_brightness, [0, 255], [100, 1000]))
    audio_segment = generate_sine_wave(sample_rate, frequency, original_duration)


    # Modify the duration to change the speed (speedup/slowdown)
    modified_duration = int(original_duration / speed)
    audio_segment = audio_segment[:modified_duration]  # Slice the audio to change duration

    return audio_segment

# Initialize audio clip
audio_clip_left = None
audio_clip_right = None


# Process each frame
frame_list = []
while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Convert the frame to audio
    blue_channel, green_channel, red_channel = cv2.split(frame)

    red_alter_right = alter_data(frame_width, red_channel,'right')
    red_alter_left = alter_data(frame_width, red_channel,'left')
    audio_segment_red_left = frame_to_audio(red_alter_left, frame_rate)
    audio_segment_red_right = frame_to_audio(red_alter_right, frame_rate)

    green_alter_right = alter_data(frame_width, green_channel,'right')
    green_alter_left = alter_data(frame_width, green_channel,'left')
    audio_segment_green_left = frame_to_audio(green_alter_left, frame_rate)
    audio_segment_green_right = frame_to_audio(green_alter_right, frame_rate)

    blue_alter_right = alter_data(frame_width, blue_channel,'right')
    blue_alter_left = alter_data(frame_width, blue_channel,'left')
    audio_segment_blue_left = frame_to_audio(blue_alter_left, frame_rate)
    audio_segment_blue_right = frame_to_audio(blue_alter_right, frame_rate)

    print(1)

    # Append the segment to the main audio clip
    if audio_clip_left is None:
        audio_clip_left = audio_segment_red_left+audio_segment_blue_left+audio_segment_green_left
    else:
        audio_clip_left = audio_clip_left + audio_segment_red_left+audio_segment_blue_left+audio_segment_green_left
    
    if audio_clip_right is None:
        audio_clip_right = audio_segment_red_right+audio_segment_green_right+audio_segment_blue_right
    else:
        audio_clip_right = audio_clip_right + audio_segment_red_right+audio_segment_green_right+audio_segment_blue_right

    frame_list.append(frame)

# Calculate the duration of the audio clip to match the video length
video_duration = len(frame_list) / frame_rate  # in seconds


# Export the audio clip as an audio file
audio_clip_left.export(out_f='left.wav', format='wav')
audio_clip_right.export(out_f='right.wav',format='wav')

# Close the video file
cap.release()

print(f"\033[0;32mTotal time taken: {time.time() - start_time} seconds\033[0m.")