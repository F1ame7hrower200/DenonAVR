from tkinter import *
import denonavr
import queue
import threading
import asyncio

avr = denonavr.DenonAVR('192.168.0.112')

loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()

def run_async(coro):
    asyncio.run_coroutine_threadsafe(coro, loop)

gui_queue = queue.Queue()

run_async(avr.async_setup())

def power_on_click():
    run_async(avr.async_power_on())
def power_off_click():
    run_async(avr.async_power_off())
def on_slider_move(value):
    absolute_volume = float(value)
    db_volume = absolute_volume - 80
    run_async(avr.async_set_volume(float(db_volume)))

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
        poweron.config(font=("Comic Sans MS",50, 'bold'))
        poweroff.config(font=("Comic Sans MS",30, 'bold'))
    else:
        poweroff.config(font=("Comic Sans MS", 50, 'bold'))
        poweron.config(font=("Comic Sans MS",30, 'bold'))

desired_inputs = ["FATBOY590", "RTX3070", 'Turntable']

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
window.geometry("800x480")
window.title("Denon AVR Remote")
window.configure(background="black")
window.attributes("-fullscreen", True)

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
input_menu.config(background="black", fg="white", font=("Comic Sans", 20))
input_menu.pack(pady=10)

suppress_input_trace = False

def on_input_selected(*args):
    if suppress_input_trace:
        return
    run_async(avr.async_set_input_func(selected_input.get()))

selected_input.trace_add("write", on_input_selected)

horizontal = Scale(window, from_=0, to=98, orient=HORIZONTAL, length=700, width=40, sliderlength=60)
horizontal.config(command=on_slider_move,background="black",fg="white",font=("Comic Sans MS",30,'bold'))
horizontal.pack(side=BOTTOM, pady=(30, 10), padx=40)

horizontal.get()

footer = Label(window, text="Made by Gage and Claude :)", background="black", fg="white", font=("Arial", 10))
footer.place(relx=0.5, rely=1.0, anchor=S)

window.after(200, process_queue)
window.mainloop()