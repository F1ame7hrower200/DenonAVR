from tkinter import *
import denonavr
import queue
import threading
import asyncio
import httpx
import subprocess

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

def db_to_swl_raw(db: float) -> str:
    raw = round((db + 50) * 10)
    return f"PSSWL {raw}"

def power_on_click():
    run_async(avr.async_power_on())

def power_off_click():
    run_async(avr.async_power_off())

def setup_page():
    subprocess.run(["python", 'setup_menu.py'], check=True)

def on_slider_move(value):
    absolute_volume = float(value)
    db_volume = absolute_volume - 80
    run_async(avr.async_set_volume(float(db_volume)))

def on_bass_slider_move(value):
    run_async(send_subwoofer_level(float(value)))

eco_states = ["Off", "On", "Auto"]
eco_colors = {"Off": "gray", "On": "green", "Auto": "orange"}
eco_index = 0

def eco():
    global eco_index
    eco_index = (eco_index + 1) % len(eco_states)
    mode = eco_states[eco_index]
    eco_btn.config(text=f"Eco: {mode}", bg=eco_colors[mode])
    run_async(avr.async_eco_mode(mode))

async def send_subwoofer_level(db: float):
    command = db_to_swl_raw(db)
    url = f"http://192.168.0.112/goform/formiPhoneAppDirect.xml?{command}"
    async with httpx.AsyncClient() as client:
        await client.get(url)

async def send_menu_command(command: str):
    reader, writer = await asyncio.open_connection('192.168.0.112', 23)
    writer.write(f"{command}\r".encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def poll_status():
    while True:
        await avr.async_update()
        gui_queue.put(("power", avr.power))
        gui_queue.put(('volume', avr.volume))
        gui_queue.put(("input", avr.input_func))
        gui_queue.put(("input_list", avr.input_func_list))
        await asyncio.sleep(2)

run_async(poll_status())

def update_buttons(power_state):
    if power_state == "ON":
        poweron.config(font=("Sans Serif",50, 'bold'))
        poweroff.config(font=("Sans Serif",30, 'bold'))
    else:
        poweroff.config(font=("Sans Serif", 50, 'bold'))
        poweron.config(font=("Sans Serif",30, 'bold'))

desired_inputs = ["FATBOY590", "RTX3070", 'Turntable', 'Spotify', 'Bluetooth']

def update_input_menu(input_list):
    menu = input_menu["menu"]
    menu.delete(0, "end")
    available = [name for name in desired_inputs if name in input_list]
    for name in available:
        menu.add_command(label=name, command=lambda n=name: selected_input.set(n))

def process_queue():
    global suppress_input_trace
    try:
        while True:
            kind, value = gui_queue.get_nowait()
            if kind == "power":
                update_buttons(value)
            elif kind == "volume":
                horizontal.set(value + 80)
            elif kind == "input":
                suppress_input_trace = True
                selected_input.set(value)
                suppress_input_trace = False
            elif kind == "input_list":
                update_input_menu(value)
    except queue.Empty:
        pass
    window.after(200, process_queue)

window = Tk()
window.geometry("800x480+0+0")
window.overrideredirect(False)
window.title("Denon AVR Remote")
window.configure(background="black")
window.attributes("-fullscreen", True)

exit_button = Button(window, text="Exit", command=window.destroy)
exit_button.config(background="black", fg="Red", font=("Sans Serif", 30, "bold"))
exit_button.place(relx=1.0, rely=0.0, anchor=NE, x=-10, y=10)

eco_btn = Button(window, text="Eco")
eco_btn.config(bg="green",fg="white",font=("Sans Serif", 30), command=eco)
eco_btn.place(relx=0.0, rely=0.0, anchor=NW, x=10, y=10)

button_frame = Frame(window, background="black")
button_frame.pack(pady=(30,10))

poweron = Button(button_frame,text='On')
poweron.config(command=power_on_click, background="black",fg="white")
poweron.pack(side=LEFT, padx=10)

poweroff = Button(button_frame,text='Off')
poweroff.config(command=power_off_click,background="red",fg="white")
poweroff.pack(side=LEFT, padx=10)

selected_input = StringVar(window)
selected_input.set("Loading...")

input_menu = OptionMenu(window, selected_input, "Loading...")
input_menu.config(background="black", fg="white", font=("Sans Serif", 20))
input_menu.pack(pady=10)

suppress_input_trace = False

def on_input_selected(*args):
    if suppress_input_trace:
        return
    run_async(avr.async_set_input_func(selected_input.get()))

selected_input.trace_add("write", on_input_selected)

setup = Button(window, text='Control Page')
setup.config(command=setup_page, bg='black', fg='white', font=('Sans Serif', 12, 'bold'))
setup.pack(pady=10)

sliders_frame = Frame(window, background="black")
sliders_frame.pack(side=BOTTOM, pady=(5, 5), fill=X)

bass_label = Label(sliders_frame, text="Bass Level", background="black", fg="white", font=("Sans Serif", 14, "bold"))
bass_label.pack()

bass_slider = Scale(sliders_frame, from_=-12, to=12, orient=HORIZONTAL, length=700,
                     width=25, sliderlength=45, showvalue=True,
                     background="black", fg="white", font=("Sans Serif", 12), resolution=0.5)
bass_slider.config(command=on_bass_slider_move)
bass_slider.pack()

volume_label = Label(sliders_frame, text="Volume", background="black", fg="white", font=("Sans Serif", 14, "bold"))
volume_label.pack()

horizontal = Scale(sliders_frame, from_=0, to=98, orient=HORIZONTAL, length=700,
                    width=25, sliderlength=45, showvalue=True,
                    background="black", fg="white", font=("Sans Serif", 12), resolution=0.5)
horizontal.config(command=on_slider_move)
horizontal.pack()

#footer = Label(window, text="Made by Gage and Claude :)", background="black", fg="white", font=("Sans Serif", 10))
#footer.place(relx=0.5, rely=1.0, anchor=S)

window.after(200, process_queue)
window.mainloop()
