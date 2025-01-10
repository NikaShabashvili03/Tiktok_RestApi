import os
import uuid
from moviepy.video.io.VideoFileClip import VideoFileClip
from django.core.exceptions import ValidationError
import tempfile

def file_upload(instance, filename, upload_dir):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join(upload_dir, filename)

def validate_file(video, format='mp4', max_size_kb=10240, max_width=1920, max_height=1080):
    if not video.name.lower().endswith(f'.{format}'):
        raise ValidationError(f"Only {format.upper()} video files are allowed.")

    if video.size > max_size_kb * 1024:
        raise ValidationError(f"Video size should not exceed {max_size_kb}KB.")
    
def get_video_duration(video):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file_path = temp_file.name
            for chunk in video.chunks():
                temp_file.write(chunk)

        with VideoFileClip(temp_file_path) as clip:
            duration = clip.duration

        return duration

    except Exception as e:
        raise ValueError(f"Error getting video duration: {str(e)}")