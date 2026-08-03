from tkinter import *
import subprocess

def spotify_click():
    print("Opening Spotify...")
    subprocess.Popen(["/usr/bin/chromium", "--kiosk", "https://open.spotify.com"])
def remoteclick():
    print("Opening Remote...")
    subprocess.run(["python", 'remote.py'], check=True)

window = Tk()
window.geometry("800x480+0+0")
window.overrideredirect(False)
window.title("Denon AVR")
window.configure(background="black")
window.attributes("-fullscreen", True)

exit_button = Button(window, text="Exit", command=window.destroy)
exit_button.config(background="black", fg="Red", font=("Sans Serif", 30, "bold"))
exit_button.place(relx=1.0, rely=0.0, anchor=NE)

button_frame = Frame(window, background="black")
button_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

spotify = Button(button_frame, text="Spotify")
spotify.config(command=spotify_click, background="black",fg="green",font=("Sans Serif", 30, "bold"))
spotify.pack(side=LEFT, padx=10)

remote = Button(button_frame,text='Denon Remote')
remote.config(command=remoteclick, background="black",fg="blue", font=("Sans Serif", 30, "bold"))
remote.pack(side=LEFT, padx=10)

ryan = Label(window, text="Ryan bonesmashing", bg="black", fg="white", font=("Sans Serif", 10, "bold"))
ryan.pack(side=TOP, padx=10)

footer = Label(window, text="Made by Gage and Claude :)", background="black", fg="white", font=("Sans Serif", 10))
footer.place(relx=0.5, rely=1.0, anchor=S)

print('Hello world!')

window.mainloop()