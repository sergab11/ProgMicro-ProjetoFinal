import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog as filedialog
from PIL import ImageTk, Image
import pygame
import subprocess
import os

window = tk.Tk()
window.title("Bandinha")
pygame.init()

global file_path
file_path = None
playButtonImg = Image.open("Imagens/botao_play.jpg")
playButtonImg = playButtonImg.resize((50, 50), Image.ANTIALIAS) 
playButtonImg = ImageTk.PhotoImage(playButtonImg)

pauseButtonImg = Image.open("Imagens/botao_pause.jpg")
pauseButtonImg = pauseButtonImg.resize((50, 50), Image.ANTIALIAS) 
pauseButtonImg = ImageTk.PhotoImage(pauseButtonImg)

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

def choose_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes= [("Arquivos MP3","*.mp3")])
    play_audio(file_path)

def pause_audio():
    pygame.mixer.music.pause()

def resume_audio():
    pygame.mixer.music.unpause()


def show_message():
    messagebox.showinfo("Mensagem", "Testando123!")


def separate_audio(file_path):
    file_name = os.path.basename(file_path)
    output_dir = "output"
    messagebox.showinfo("Mensagem","Fazendo a separação de faixas, por favor aguarde.")
    cmd = f"spleeter separate -i {file_name} -p spleeter:5stems -o {output_dir} "
    print(cmd)
    subprocess.run(cmd, shell=True)
    messagebox.showinfo("Mensagem", "Separação de faixas concluída!")

def separate_file():
    file_path = filedialog.askopenfilename(filetypes=[("Arquivos MP3", "*.mp3")])
    separate_audio(file_path)

button = tk.Button(window, text = "Clique Aqui para escolher a música", command= choose_file)
button.grid(row=0, column=1, pady=15, padx=100)

button = tk.Button(window, text = "Separar o áudio", command= separate_file)
button.grid(row=4, column=1, pady=15, padx=100)

playButton = tk.Button(window, image= playButtonImg, command= resume_audio)
playButton.grid(row=2, column=0, pady=0, padx=0)

pauseButton = tk.Button(window, image= pauseButtonImg, command= pause_audio)
pauseButton.grid(row=2, column=2, pady=0, padx=20)


#file_path = choose_file()
# play_audio(file_path)

window.mainloop()
