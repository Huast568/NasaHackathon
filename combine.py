from moviepy.editor import VideoFileClip, AudioFileClip

# Input video file
video_file = 'space_video.mp4'

# Load the video clip
video_clip = VideoFileClip(video_file)

# Load the audio clip
audio_clip = AudioFileClip('output_audio.wav')

# Set the video clip's audio to the loaded audio clip
video_clip = video_clip.set_audio(audio_clip)

# Output the final video with combined audio
output_video = 'output_video_with_audio.mp4'
video_clip.write_videofile(output_video, codec='libx264', audio_codec='aac')

# Close the video and audio clips
video_clip.close()
audio_clip.close()
