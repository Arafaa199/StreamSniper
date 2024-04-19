import re
from tkinter import messagebox, filedialog
from pytube import YouTube
import os
import random
import string
import datetime

def browse_download_location(download_folder_var):
    download_folder = filedialog.askdirectory()
    if download_folder:
        download_folder_var.set(download_folder)

def get_validated_url(url):
    if not re.match(r'https?://(?:www\.|m\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+', url):
        messagebox.showerror("Error", "Please enter a valid YouTube URL.")
        return None
    return url


def download_video(url, download_folder_var, progress_bar, root, audio_only=False):
    if not url:
        return

    try:
        youtube = YouTube(url, on_progress_callback=lambda stream, chunk, bytes_remaining: on_progress(stream, chunk, bytes_remaining, progress_bar, root))
        if audio_only:
            video = youtube.streams.filter(only_audio=True).first()
        else:
            video = youtube.streams.get_highest_resolution()

        download_folder = download_folder_var.get()
        serial_number = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        filename = f"{serial_number}_{video.default_filename}"
        file_path = video.download(output_path=download_folder, filename=filename)
        messagebox.showinfo("Success", "Download completed successfully!")
        progress_bar['value'] = 0
        log_download(video.title, file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download video: {str(e)}")
        progress_bar['value'] = 0

def on_progress(stream, chunk, bytes_remaining, progress_bar, root):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    progress_bar['value'] = percentage_of_completion
    root.update_idletasks()

def log_download(video_title, file_path):
    log_path = "/Users/arafa/download_history.txt"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    try:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a") as log_file:
            log_file.write(f"{current_time}: {video_title}, {file_path}\n")
    except Exception as e:
        messagebox.showerror("Logging Error", f"Failed to log download: {str(e)}")
