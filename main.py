from tkinter import *
from selenium import webdriver
import subprocess
import webbrowser

def spotify_click():
    driver = webdriver.Chrome()
    driver.get('https://open.spotify.com')
    driver.fullscreen_window()
    print("Opening Spotify...")

def remoteclick():
    subprocess.run(["python", 'remote.py'], check=True)
    print("Opening Remote...")

window = Tk()
window.geometry("800x480")
window.title("Denon AVR")
window.configure(background="black")
window.attributes("-fullscreen", True)

button_frame = Frame(window, background="black")
button_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

spotify = Button(button_frame, text="Spotify")
spotify.config(command=spotify_click, background="black",fg="green",font=("Comic Sans MS", 50, "bold"))
spotify.pack(side=LEFT, padx=10)

remote = Button(button_frame,text='Remote')
remote.config(command=remoteclick, background="black",fg="white", font=("Comic Sans MS", 50, "bold"))
remote.pack(side=LEFT, padx=10)

footer = Label(window, text="Made by Gage and Claude :)", background="black", fg="white", font=("Arial", 10))
footer.place(relx=0.5, rely=1.0, anchor=S)

window.mainloop()