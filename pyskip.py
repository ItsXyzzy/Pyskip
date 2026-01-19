import tkinter as tk
from tkinter import filedialog, ttk
import pygame
import os
from mutagen.mp3 import MP3

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("500x300")
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Track info
        self.current_song = None
        self.paused = False
        self.song_length = 0
        
        # UI Elements
        self.song_label = tk.Label(root, text="No song loaded", font=("Arial", 12))
        self.song_label.pack(pady=20)
        
        # Time labels
        time_frame = tk.Frame(root)
        time_frame.pack(pady=5)
        
        self.current_time_label = tk.Label(time_frame, text="0:00", font=("Arial", 10))
        self.current_time_label.grid(row=0, column=0, padx=5)
        
        self.total_time_label = tk.Label(time_frame, text="0:00", font=("Arial", 10))
        self.total_time_label.grid(row=0, column=1, padx=5)
        
        # Progress bar
        self.progress_bar = ttk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, 
                                      length=400, command=self.seek_song)
        self.progress_bar.pack(pady=10)
        
        # Volume control
        volume_frame = tk.Frame(root)
        volume_frame.pack(pady=10)
        
        tk.Label(volume_frame, text="Volume:", font=("Arial", 10)).grid(row=0, column=0, padx=5)
        
        self.volume_slider = ttk.Scale(volume_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                       length=200, command=self.set_volume)
        self.volume_slider.set(70)  # Default volume
        self.volume_slider.grid(row=0, column=1, padx=5)
        
        self.volume_label = tk.Label(volume_frame, text="70%", font=("Arial", 10))
        self.volume_label.grid(row=0, column=2, padx=5)
        
        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        
        self.load_btn = tk.Button(button_frame, text="Load Song", command=self.load_song, width=10)
        self.load_btn.grid(row=0, column=0, padx=5)
        
        self.play_btn = tk.Button(button_frame, text="Play", command=self.play_song, width=10, state=tk.DISABLED)
        self.play_btn.grid(row=0, column=1, padx=5)
        
        self.pause_btn = tk.Button(button_frame, text="Pause", command=self.pause_song, width=10, state=tk.DISABLED)
        self.pause_btn.grid(row=0, column=2, padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="Stop", command=self.stop_song, width=10, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=3, padx=5)
        
        # Update progress bar periodically
        self.update_progress()
        
    def load_song(self):
        song = filedialog.askopenfilename(
            title="Choose a song",
            filetypes=(("MP3 Files", "*.mp3"), ("All Files", "*.*"))
        )
        if song:
            self.current_song = song
            song_name = os.path.basename(song)
            self.song_label.config(text=song_name)
            pygame.mixer.music.load(song)
            
            # Get song length
            try:
                audio = MP3(song)
                self.song_length = int(audio.info.length)
                self.total_time_label.config(text=self.format_time(self.song_length))
                self.progress_bar.config(to=self.song_length)
            except:
                self.song_length = 0
                self.total_time_label.config(text="0:00")
            
            # Enable play button
            self.play_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
    
    def play_song(self):
        if self.current_song:
            if self.paused:
                pygame.mixer.music.unpause()
                self.paused = False
            else:
                pygame.mixer.music.play()
            
            # Update button states
            self.play_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
    
    def pause_song(self):
        if pygame.mixer.music.get_busy() and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            
            # Update button states
            self.pause_btn.config(state=tk.DISABLED)
            self.play_btn.config(state=tk.NORMAL)
    
    def stop_song(self):
        pygame.mixer.music.stop()
        self.paused = False
        self.progress_bar.set(0)
        self.current_time_label.config(text="0:00")
        
        # Update button states
        self.play_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
    
    def set_volume(self, val):
        volume = float(val) / 100
        pygame.mixer.music.set_volume(volume)
        self.volume_label.config(text=f"{int(float(val))}%")
    
    def seek_song(self, val):
        # Only seek if user is dragging the slider (not during auto-update)
        if pygame.mixer.music.get_busy() or self.paused:
            pygame.mixer.music.set_pos(float(val))
    
    def update_progress(self):
        if pygame.mixer.music.get_busy() and not self.paused:
            # Get current position in milliseconds, convert to seconds
            current_pos = pygame.mixer.music.get_pos() / 1000
            
            # pygame.mixer.music.get_pos() resets when looping, so we need to track manually
            # For simplicity, we'll use a rough estimate
            if hasattr(self, 'start_time'):
                import time
                elapsed = time.time() - self.start_time
                if elapsed <= self.song_length:
                    self.progress_bar.set(elapsed)
                    self.current_time_label.config(text=self.format_time(int(elapsed)))
            else:
                import time
                self.start_time = time.time()
        elif not pygame.mixer.music.get_busy() and not self.paused and self.current_song:
            # Song finished
            self.stop_song()
            if hasattr(self, 'start_time'):
                delattr(self, 'start_time')
        
        # Schedule next update
        self.root.after(100, self.update_progress)
    
    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}:{secs:02d}"

# Run the app
root = tk.Tk()
app = MusicPlayer(root)
root.mainloop()