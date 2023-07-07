#============ imports ===========
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pygame
from pygame import mixer
import os
import shutil
from natsort import natsorted
import ntr
from PIL import ImageTk, Image

#===============================

import pydub
import speech_recognition as sr
import numpy as np
from censoredzz import profanity
from pydub import AudioSegment


def audio_converter(src):
    dst = "soundCheck.wav"
    # Create an AudioSegment object
    sound = AudioSegment.from_file(src, format='mp3')
   # Check if the audio is in MP3 format    
    is_mp3 = sound.export(format='mp3')[-3:] == b'MP3'
    if is_mp3:
        sound.export(dst, format="wav")
        return True
    else:
        print("Format not supported")
        return False
        
def load_audio(src):
    # Load the audio file
    # if audio_converter(src):
    #     return pydub.AudioSegment.from_wav("./soundCheck.wav")
    audio_path = src
    return pydub.AudioSegment.from_wav(audio_path)


output_folder = "chunk"
# Apply speech detection
silence_threshold = -87  # Adjust the threshold value as needed

def show_popup():
    popup = tk.Toplevel(window)
    popup.title("Success")
    popup.geometry("300x100")
    popup.attributes("-topmost", True)
     # Configure the background color of the root frame
    popup.configure(bg="#2B851F")


    label = tk.Label(popup, text="Audio Censored successfully !",  fg="white", bg="#2B851F")
    label.config(font=("Arial", 12, "bold"))
    label.pack(pady=20)

    # Close the popup after 1 second
    popup.after(5000, popup.destroy)


def remove_chunk():
    try:
        shutil.rmtree('./chunk/')
        # print(f"All files and directories inside '{directory_path}' have been removed.")
    except OSError as e:
        print(f"Error occurred while removing files and directories: {e}")

def split_audio(audio):
    # Split audio into speech segments based on silence
    segment_start = 0
    speech_segments = []
    for i in range(len(audio)):
        if audio[i].dBFS < silence_threshold:
            if segment_start < i:
                segment = audio[segment_start:i]
                speech_segments.append(segment)
            segment_start = i + 1
    return speech_segments

def process_speech_segments(speech_segments):
    # Directory path to create new folder
    directory_path = "./chunk"
    # Create the new folder
    os.makedirs(directory_path, exist_ok=True)

    # Process speech segments
    for i, segment in enumerate(speech_segments):
        # Convert the segment to pydub's AudioSegment format
        audio_segment = pydub.AudioSegment.from_mono_audiosegments(segment.split_to_mono()[0])
        # Apply audio processing techniques (e.g., pitch shifting)
        shifted_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': int(audio_segment.frame_rate * 1)})
        shifted_segment = shifted_segment.set_frame_rate(audio_segment.frame_rate)
        shifted_segment.export(f"{output_folder}/segment{i}.wav", format="wav")

def update_profane_flag(speech_segments):
    profane_speech_flag = []
    for i, segment in enumerate(speech_segments):
        # Perform speech-to-text transcription
        r = sr.Recognizer()
        with sr.AudioFile(f"{output_folder}/segment{i}.wav") as speech_file:
            audio_data = r.record(speech_file)
            try:
                text = r.recognize_google(audio_data, language='ne')
                print(ntr.nep_to_rom(text))
                # check for profanity in each segment
                if profanity.has_profanity(ntr.nep_to_rom(text)):
                    print('-',end='')
                    profane_speech_flag.append(1)
                else:
                    profane_speech_flag.append(0)
            except:
                profane_speech_flag.append(2)
                # print('-', end='')
    return profane_speech_flag

def audio_beep(profane_speech_flag):
    print('beeep------>')
    # Directory path
    directory_path = "./chunk/"
    # Get all files in the directory
    file_list = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    # Sort the file list naturally
    audio_list = natsorted(file_list)
    # Initialize the combined audio
    combined_audio = AudioSegment.empty()
    print('=====>')
    print(profane_speech_flag)
    print('=====>')
    # Iterate over the files in the directory
    for i, filename in enumerate(audio_list):
        if  profane_speech_flag[i]==1:
            print('BEEEEEP')
            beep_path = "./squeak.wav"
            beep = AudioSegment.from_file(beep_path, format="wav")
            combined_audio += beep
        else:
            file_path = os.path.join(directory_path, filename)
            segment = AudioSegment.from_file(file_path, format="wav")
            combined_audio += segment
    # remove censored audio
    try:
        os.remove("censored_audio.wav")
        print(f"File '{file_path}' has been removed.")
    except OSError as e:
        print(f"Error occurred while removing the file: {e}")

    # Export the combined audio as a single file
    combined_audio.export("censored_audio.wav", format="wav")
    print('cool')
    show_popup()
    return 
#============ methods ===========
def browse_file():
    filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*")])
    input_field.delete(0, tk.END)
    input_field.insert(tk.END, filepath)

def censor_audio():
     # Disable the button during processing
    censor_button.config(state="disabled")
    # Show the processing spinner
    # spinner.start()
    try:
        filepath = input_field.get()
        remove_chunk()
        audio = load_audio(filepath)
        speech_segments = split_audio(audio)
        process_speech_segments(speech_segments)
        profane_speech_flag = update_profane_flag(speech_segments)
        audio_beep(profane_speech_flag)
    except:
        pass
    finally:
        # Hide the processing spinner
        # spinner.stop()
        # Enable the button after processing
        censor_button.config(state="normal")

    # Add code to convert the audio file

def play_audio():
    filepath = input_field.get()
    pygame.mixer.init()
    pygame.mixer.music.load(filepath)
    pygame.mixer.music.play()

def download_audio():
    filepath = input_field.get()
    # Add code to enable downloading the audio file


#============= window ===========
window = tk.Tk()
window.geometry("500x500")
# Change the background color
window.configure(bg="#1C2025")


# Elements -------------------->>

# TITLE image
#  Load the image
image = Image.open("title11.jpg")
# Resize the image
resized_image = image.resize((500, 125),  Image.LANCZOS)
photo = ImageTk.PhotoImage(resized_image)
# Create a label to display the image
image_label = tk.Label(window, image=photo,  bd=0, highlightthickness=0)
image_label.pack(pady=100)


# Create a frame to hold the widgets
frame = tk.Frame(window, width=400, height=100)
frame.configure(bg="#1C2025")
frame.pack(pady=50)


# Create the input field
input_field = tk.Entry(frame, width=30, font=("Arial", 14))
input_field.grid(row=1, column=0,)

browse_button = tk.Button(frame, text="Browse", command=browse_file, relief=tk.RAISED, padx=10, pady=2, bg="lightblue", fg="black",  bd=0, highlightthickness=0)
browse_button.config(font=("Roboto", 15))
browse_button.grid(row=1, column=1)



# Create the button
censor_button = tk.Button(frame, text="Censor", command=censor_audio, relief=tk.RAISED, bg="#B01F2A", fg="white",  bd=0, highlightthickness=0)
censor_button.config(font=("Arial", 15, "bold"))
censor_button.grid(row=2, column=0, columnspan=2, pady=10)

# # Create a separate frame for the progress bar
# progress_frame = tk.Frame(frame,  width=100, height=50)
# progress_frame.configure(bg="#1C2025")
# progress_frame.grid(row=3, column=0, columnspan=2, pady=10)

# # Create a progress bar widget
# style = ttk.Style()
# style.configure("TProgressbar", thickness=30)
# spinner = ttk.Progressbar(progress_frame, style="TProgressbar", mode="indeterminate")




# Center-align the widgets in the frame
frame.pack_propagate(0)
frame.place(relx=0.5, rely=0.5, anchor="center")



window.mainloop()
