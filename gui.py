import tkinter as tk
from tkinter import ttk, font as tkFont
from functions import browse_download_location, download_video, on_progress, log_download, get_validated_url
from PIL import Image, ImageTk

def create_gradient(canvas, width, height):
    """Paint a gradient from dark blue to dark burgundy on a canvas."""
    top_color = (0, 38, 77)  # Dark blue in RGB
    bottom_color = (77, 0, 38)  # Dark burgundy in RGB

    for y in range(height):
        r = int(top_color[0] * (1 - y / height) + bottom_color[0] * (y / height))
        g = int(top_color[1] * (1 - y / height) + bottom_color[1] * (y / height))
        b = int(top_color[2] * (1 - y / height) + bottom_color[2] * (y / height))
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, y, width, y, fill=color)

root = tk.Tk()
root.title("Arafa's YouTube Video Downloader")
window_width = 800
window_height = 400
root.geometry(f'{window_width}x{window_height}')

root.attributes('-alpha', 0.85)

canvas = tk.Canvas(root, height=window_height, width=window_width)
canvas.pack(fill='both', expand=True)
create_gradient(canvas, window_width, window_height)

title_font = tkFont.Font(family='Arial', size=24, weight='bold')
label_font = tkFont.Font(family='Arial', size=12, weight='bold')  # Enhanced visibility
button_font = tkFont.Font(family='Arial', size=12, weight='bold')

title_label = tk.Label(root, text="Arafa's YouTube Video Downloader", font=title_font, fg="white", bg="#004060")  # Adjusted background color
title_label.pack(fill=tk.BOTH, padx=20, pady=20)

form_frame = tk.Frame(root, bg='#004060')  # Adjusted to a darker background for contrast
form_frame.pack(fill=tk.BOTH, expand=True, padx=20)

url_label = tk.Label(form_frame, text="Enter URL:", font=label_font, fg='white', bg='#004060')
url_label.grid(row=0, column=0, sticky="w", pady=(10, 0))
url_entry = tk.Entry(form_frame, width=50)
url_entry.grid(row=0, column=1, pady=(10, 0))

download_type_var = tk.StringVar(value="audio")
audio_radio = tk.Radiobutton(form_frame, text="Audio", variable=download_type_var, value="audio", font=label_font, fg='white', bg='#004060')
audio_radio.grid(row=1, column=0, sticky="w")
video_radio = tk.Radiobutton(form_frame, text="Video", variable=download_type_var, value="video", font=label_font, fg='white', bg='#004060')
video_radio.grid(row=1, column=1, sticky="w")

download_button = tk.Button(form_frame, text="Download", font=button_font, fg='white', bg='#0078D7')
download_button.grid(row=0, column=2, rowspan=2, padx=10, ipadx=5, ipady=5)

download_location_label = tk.Label(form_frame, text="Download Location:", font=label_font, fg='white', bg='#004060')
download_location_label.grid(row=2, column=0, sticky="w")
download_folder_var = tk.StringVar(value="/Users/arafa/Desktop")
download_folder_entry = tk.Entry(form_frame, width=50)
download_folder_entry.grid(row=2, column=1)

browse_button = tk.Button(form_frame, text="Browse", font=button_font, fg='white', bg='#0078D7')
browse_button.grid(row=2, column=2, padx=5)

progress_bar = ttk.Progressbar(form_frame, orient='horizontal', length=400, mode='determinate')
progress_bar.grid(row=3, column=0, columnspan=3, padx=5, pady=10, sticky="we")

root.mainloop()
