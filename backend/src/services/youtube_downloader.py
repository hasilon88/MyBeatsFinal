import imageio_ffmpeg as ffmpeg
import yt_dlp
import os

def download_youtube_mp3(url, title="%(title)s", output_folder="/tmp/downloads"):
    os.makedirs(output_folder, exist_ok=True)

    output_template = f"{output_folder}/{title}.%(ext)s"

    ydl_opts = {
        'ffmpeg_location': ffmpeg.get_ffmpeg_exe(),
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_title = info.get('title', 'unknown')
        file_path = os.path.join(output_folder, f"{file_title}.mp3")
        return file_path
