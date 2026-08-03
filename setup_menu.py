import denonavr
import threading
import asyncio
import queue
from tkinter import *

avr = denonavr.DenonAVR('192.168.0.112')

loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()

def run_async(coro):
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    def _report(f):
        try:
            f.result()
        except Exception as e:
            print(f"[async error] {e!r}")
    future.add_done_callback(_report)

gui_queue = queue.Queue()

run_async(avr.async_setup())

async def send_menu_command(command: str):
    reader, writer = await asyncio.open_connection('192.168.0.112', 23)
    writer.write(f"{command}\r".encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()

def setup_page():
    run_async(send_menu_command("MNMEN ON"))

def cursor_up():
    run_async(send_menu_command("MNCUP"))
def cursor_down():
    run_async(send_menu_command("MNCDN"))
def cursor_left():
    run_async(send_menu_command("MNCLT"))
def cursor_right():
    run_async(send_menu_command("MNCRT"))
def cursor_enter():
    run_async(send_menu_command("MNENT"))
def cursor_return():
    run_async(send_menu_command("MNRTN"))
def close_menu():
    run_async(send_menu_command("MNMEN OFF"))

def set_sound_mode(mode):
    run_async(avr.async_set_sound_mode(mode))

async def poll_status():
    while True:
        await avr.async_update()
        gui_queue.put(("sound_mode", avr.sound_mode))
        await asyncio.sleep(2)
def process_queue():
    try:
        while True:
            kind, value = gui_queue.get_nowait()
            if kind == "sound_mode":
                for btn, mode in sound_mode_buttons.items():
                    btn.config(relief=SUNKEN if mode == value else FLAT)
    except queue.Empty:
        pass
    window.after(200, process_queue)

window = Tk()
window.title("Denon AVR Setup")
window.geometry("800x480+0+0")
window.overrideredirect(True)
window.configure(background="black")

exit_button = Button(window, text="Exit", command=window.destroy)
exit_button.config(background="black", fg="Red", font=("Sans Serif", 30, "bold"))
exit_button.place(relx=1.0, rely=0.0, anchor=NE, x=-10, y=10)

setup = Button(window, text='Setup')
setup.config(command=setup_page, bg='black', fg='white', font=('Sans Serif', 12, 'bold'))
setup.pack(pady=10)

NAV_BTN_STYLE = dict(bg="black", fg="white", activebackground="#333",
                      activeforeground="white", font=("Sans Serif", 20, "bold"),
                      relief=FLAT, bd=0, width=3, height=1,
                      highlightbackground="white", highlightthickness=1)

nav_frame = Frame(window, background="black")
nav_frame.pack(pady=10)

Button(nav_frame, text="▲", command=cursor_up, **NAV_BTN_STYLE).grid(row=0, column=1, padx=4, pady=4)
Button(nav_frame, text="◀", command=cursor_left, **NAV_BTN_STYLE).grid(row=1, column=0, padx=4, pady=4)
Button(nav_frame, text="OK", command=cursor_enter, **NAV_BTN_STYLE).grid(row=1, column=1, padx=4, pady=4)
Button(nav_frame, text="▶", command=cursor_right, **NAV_BTN_STYLE).grid(row=1, column=2, padx=4, pady=4)
Button(nav_frame, text="▼", command=cursor_down, **NAV_BTN_STYLE).grid(row=2, column=1, padx=4, pady=4)

bottom_row = Frame(window, background="black")
bottom_row.pack(pady=(0, 10))
Button(bottom_row, text="Back", command=cursor_return, bg="black", fg="white",
       font=("Sans Serif", 14, "bold"), relief=FLAT, highlightbackground="white",
       highlightthickness=1).pack(side=LEFT, padx=10)
Button(bottom_row, text="Exit Menu", command=close_menu, bg="black", fg="red",
       font=("Sans Serif", 14, "bold"), relief=FLAT, highlightbackground="red",
       highlightthickness=1).pack(side=LEFT, padx=10)

sound_mode_frame = Frame(window, background="black")
sound_mode_frame.pack(pady=(30,10))

movie = Button(sound_mode_frame, text="Movie")
movie.config(bg="green", fg="white", font=("Sans Serif", 12, "bold"), command=lambda: set_sound_mode("MOVIE"))
movie.pack(side=LEFT, pady=10)

music = Button(sound_mode_frame, text="Music")
music.config(bg='red', fg='white', font=("Sans Serif", 12, "bold"), command=lambda: set_sound_mode("MUSIC"))
music.pack(side=LEFT, pady=10)

game = Button(sound_mode_frame, text="Game")
game.config(bg='blue', fg='white', font=("Sans Serif", 12, "bold"), command=lambda: set_sound_mode("GAME"))
game.pack(side=LEFT, pady=10)

pure = Button(sound_mode_frame, text="Pure")
pure.config(bg='#d3c300', fg='white', font=("Sans Serif", 12, "bold"), command=lambda: set_sound_mode("DIRECT"))
pure.pack(side=LEFT, pady=10)

other_frame = Frame(window, background="black")
other_frame.pack(pady=0)

mch_stereo = Button(other_frame, text="MCh Stereo")
mch_stereo.config(bg='gray', fg='white', font=("Sans Serif", 12, "bold"), command=lambda: set_sound_mode("MCH STEREO"))
mch_stereo.pack(side=LEFT, pady=0)

dolby = Button(other_frame, text="Dolby Digital")
dolby.config(bg='gray', fg='white', font=("Sans Serif", 12, "bold"), command=lambda: set_sound_mode("DOLBY DIGITAL"))
dolby.pack(side=LEFT, pady=0)

sound_mode_buttons = {
    movie: "MOVIE",
    music: "MUSIC",
    game: "GAME",
    pure: "DIRECT",
    mch_stereo: "MCH STEREO",
    dolby: "DOLBY DIGITAL",
}

run_async(poll_status())
window.after(200, process_queue)

print("sound_mode_list:", avr.sound_mode_list)

window.mainloop()
