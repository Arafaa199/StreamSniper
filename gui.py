import tkinter as tk
from tkinter import ttk, font as tkFont
from functions import browse_download_location, download_video, on_progress, log_download, get_validated_url, get_default_download_path
from PIL import Image, ImageTk


# Helper functions for the GUI
def create_gradient(canvas, width, height):
    top_color = (0, 38, 77)
    bottom_color = (77, 0, 38)
    for y in range(height):
        r = int(top_color[0] * (1 - y / height) + bottom_color[0] * (y / height))
        g = int(top_color[1] * (1 - y / height) + bottom_color[1] * (y / height))
        b = int(top_color[2] * (1 - y / height) + bottom_color[2] * (y / height))
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, y, width, y, fill=color)

def on_resize(event):
    # Redraw the gradient to fit the new window size
    canvas.delete("all")
    create_gradient(canvas, event.width, event.height)
    form_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.8, relheight=0.4)


# Setting up the main window
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Arafa's YouTube Video Downloader")
    window_width = 800
    window_height = 400
    root.geometry(f'{window_width}x{window_height}')
    root.bind('<Configure>', on_resize)

    canvas = tk.Canvas(root, height=window_height, width=window_width)
    canvas.pack(fill='both', expand=True)
    create_gradient(canvas, window_width, window_height)

    label_font = tkFont.Font(family="Arial", size=12, weight="bold")
    button_font = tkFont.Font(family="Arial", size=12, weight="bold")

    form_frame = tk.Frame(root, bg='#9c3d52', bd=0)
    form_frame.place(relx=0.5, rely=0.2, anchor='center', relwidth=0.8, relheight=0.4)

    url_label = tk.Label(form_frame, text="Enter URL:", font=label_font, bg='white', fg='#9c3d52')
    url_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
    url_entry = tk.Entry(form_frame, font=label_font, width=40, bg='#3b0d23')
    url_entry.grid(row=0, column=1, pady=10, padx=10)

    download_type_var = tk.StringVar(value="audio")
    audio_radio = tk.Radiobutton(form_frame, text="Audio", variable=download_type_var, value="audio", font=label_font, bg='white', fg='#9c3d52')
    audio_radio.grid(row=1, column=0, sticky="w", padx=10)
    video_radio = tk.Radiobutton(form_frame, text="Video", variable=download_type_var, value="video", font=label_font, bg='white', fg='#9c3d52')
    video_radio.grid(row=1, column=1, sticky="w")

    download_button = tk.Button(form_frame, text="Download", font=button_font, bg='#0078D7', fg='#9c3d52',command=lambda: download_video(url_entry.get(), download_folder_entry, progress_bar, root, audio_only=(download_type_var.get() == 'audio')))
    download_button.grid(row=0, column=2, rowspan=2, padx=10, pady=10, ipadx=5, ipady=5)

    download_location_label = tk.Label(form_frame, text="Download Location:", font=label_font, bg='white', fg='#9c3d52')
    download_location_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)
    download_folder_entry = tk.Entry(form_frame, font=label_font, width=40, bg='#0e1e3f')
    download_folder_entry.grid(row=2, column=1, pady=10, padx=10)
    download_folder_entry.insert(0, get_default_download_path())  # Initialize with default path


    browse_button = tk.Button(form_frame, text="Browse", font=button_font, command=lambda: browse_download_location(download_folder_entry), fg='#9c3d52')
    browse_button.grid(row=2, column=2, padx=10, pady=10)

    progress_bar = ttk.Progressbar(form_frame, orient='horizontal', length=300, mode='determinate')
    progress_bar.grid(row=3, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

    root.mainloop()
    # TODO:
    #   - Add a "Downloads" tab to the GUI that shows all the downloads that have been completed
    #   - Add a "Settings" tab to the GUI that allows the user to change the download location
    #   - Add a "About" tab to the GUI that shows information about the program
    #   - Add a "Help" tab to the GUI that shows instructions on how to use the program
    #   - Add a "Feedback" tab to the GUI that allows the user to send feedback about the program
    #   - Add a "Support" tab to the GUI that allows the user to contact the developer for support
    #   - Add a "Privacy Policy" tab to the GUI that shows the privacy policy of the program
    #   - Add a "Terms of Service" tab to the GUI that shows the terms of service of the program

