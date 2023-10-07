import cv2
import numpy as np
from pydub import AudioSegment

def generate_sine_wave(frame_rate, frequency, duration_seconds, amplitude=100):
    angular_frequency = 2 * np.pi * frequency
    num_samples = int(frame_rate * duration_seconds)
    time_points = np.arange(num_samples) / frame_rate  # Generate time points in seconds
    audio_data = np.uint8(amplitude * np.sin(angular_frequency * time_points))
    return audio_data


def frame_to_audio(frame, frame_rate, speed=1.0):
    # Calculate the mean brightness of the frame
    mean_brightness = np.mean(frame)

    # Define the parameters for the audio segment
    original_duration = 1000 / frame_rate  # Duration in milliseconds (adjust as needed)
    sample_rate = 44100  # Audio sample rate (44.1 kHz is common)

    frequency = int(np.interp(mean_brightness, [0, 255], [100, 1000]))
    audio_data = generate_sine_wave(sample_rate, frequency, original_duration)

    # Create an audio segment with the audio data
    audio_segment = AudioSegment(
        audio_data.tobytes(), frame_rate=sample_rate, sample_width=audio_data.itemsize, channels=1
    )

    # Modify the duration to change the speed (speedup/slowdown)
    modified_duration = int(original_duration / speed)
    audio_segment = audio_segment[:modified_duration]  # Slice the audio to change duration

    return audio_segment

# Input video file
video_file = 'space_video.mp4'

# Load the video
cap = cv2.VideoCapture(video_file)
frame_rate = int(cap.get(cv2.CAP_PROP_FPS))  # Get the frame rate of the video

# Initialize audio clip
audio_clip = None

# Read the first frame to get its shape
ret, frame = cap.read()
if not ret:
    raise ValueError("Failed to read the first frame")

# Get frame dimensions
frame_height, frame_width, _ = frame.shape

# Create a VideoWriter to write the output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for the output video
output_video = cv2.VideoWriter('output_video.mp4', fourcc, frame_rate, (frame_width, frame_height))

# Process each frame
frame_list = []
while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Convert the frame to audio
    audio_segment = frame_to_audio(frame, frame_rate)

    # Append the segment to the main audio clip
    if audio_clip is None:
        audio_clip = audio_segment
    else:
        audio_clip = audio_clip + audio_segment

    frame_list.append(frame)
    output_video.write(frame)

# Calculate the duration of the audio clip to match the video length
video_duration = len(frame_list) / frame_rate  # in seconds

# Release the video writer
output_video.release()

# Export the audio clip as an audio file
audio_clip.export(out_f='output_audio.wav', format='wav')

# Close the video file
cap.release()