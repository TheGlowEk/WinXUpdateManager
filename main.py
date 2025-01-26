import threading
import pygame
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import winreg

def play_audio_in_loop(audio_file):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    while True:
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

def create_gradient_button_image(width, height, radius, color1, color2):
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for i in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * i / height)
        g = int(color1[1] + (color2[1] - color1[1]) * i / height)
        b = int(color1[2] + (color2[2] - color1[2]) * i / height)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, width, height), radius, fill=255)
    image.putalpha(mask)
    return ImageTk.PhotoImage(image)

def control_windows_update(action):
    try:
        key_path_wuauserv = r"SYSTEM\CurrentControlSet\Services\wuauserv"
        key_path_usosvc = r"SYSTEM\CurrentControlSet\Services\UsoSvc"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path_wuauserv, 0, winreg.KEY_SET_VALUE) as key:
            if action == "start":
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 1)
            elif action == "stop":
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path_usosvc, 0, winreg.KEY_SET_VALUE) as key:
            if action == "start":
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 1)
            elif action == "stop":
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)
        status = "włączona" if action == "start" else "wyłączona"
        messagebox.showinfo("Sukces", f"Usługa Windows Update została {status}.")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się zmienić stanu usługi.\n{e}")

def modify_feature_update(block):
    try:
        key_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
        with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
            if block:
                winreg.SetValueEx(key, "TargetReleaseVersion", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "TargetReleaseVersionInfo", 0, winreg.REG_SZ, "1507")
                messagebox.showinfo("Sukces", "Feature Update został zablokowany.")
            else:
                winreg.SetValueEx(key, "TargetReleaseVersion", 0, winreg.REG_DWORD, 0)
                winreg.DeleteValue(key, "TargetReleaseVersionInfo")
                messagebox.showinfo("Sukces", "Feature Update został odblokowany.")
    except PermissionError:
        messagebox.showerror("Błąd", "Brak uprawnień administracyjnych.")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się zmienić ustawień.\n{e}")

def enable_update():
    control_windows_update("start")

def disable_update():
    control_windows_update("stop")

def block_feature_update():
    modify_feature_update(True)

def unblock_feature_update():
    modify_feature_update(False)

def block_driver_installation():
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\DriverSearching"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "SearchOrderConfig", 0, winreg.REG_DWORD, 0)
        messagebox.showinfo("Sukces", "Instalacja sterowników została zablokowana.")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się zablokować instalacji sterowników.\n{e}")

def unblock_driver_installation():
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\DriverSearching"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "SearchOrderConfig", 0, winreg.REG_DWORD, 1)
        messagebox.showinfo("Sukces", "Instalacja sterowników została odblokowana.")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się odblokować instalacji sterowników.\n{e}")

audio_thread = threading.Thread(target=play_audio_in_loop, args=("audio.opus",), daemon=True)
audio_thread.start()

root = tk.Tk()
root.title("WinXUpdateManager")
root.geometry("500x700")
root.configure(bg="#505050")
root.resizable(False, False)

frame = tk.Frame(root, bg="#505050", padx=10, pady=10)
frame.pack(expand=True)

logo_image = Image.open("logo.png")
logo_image = logo_image.resize((500, 280), Image.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo_image)

logo_label = tk.Label(frame, image=logo_photo, bg="#505050")
logo_label.pack(pady=1)

button_width, button_height, corner_radius = 280, 40, 20
color1 = (70, 130, 180)
color2 = (25, 25, 112)

gradient_img = create_gradient_button_image(button_width, button_height, corner_radius, color1, color2)

enable_button = tk.Button(
    frame,
    text="Włącz Windows Update",
    command=enable_update,
    image=gradient_img,
    compound="center",
    font=("Arial", 10, "bold"),
    fg="white",
    bg="#505050",
    bd=0,
)
enable_button.pack(pady=5)

disable_button = tk.Button(
    frame,
    text="Wyłącz Windows Update",
    command=disable_update,
    image=gradient_img,
    compound="center",
    font=("Arial", 10, "bold"),
    fg="white",
    bg="#505050",
    bd=0,
)
disable_button.pack(pady=5)

separator1 = tk.Frame(frame, height=1, bg="grey", width=280)
separator1.pack(pady=10)

block_button = tk.Button(
    frame,
    text="Zablokuj Feature Update",
    command=block_feature_update,
    image=gradient_img,
    compound="center",
    font=("Arial", 10, "bold"),
    fg="white",
    bg="#505050",
    bd=0,
)
block_button.pack(pady=5)

unblock_button = tk.Button(
    frame,
    text="Odblokuj Feature Update",
    command=unblock_feature_update,
    image=gradient_img,
    compound="center",
    font=("Arial", 10, "bold"),
    fg="white",
    bg="#505050",
    bd=0,
)
unblock_button.pack(pady=5)

separator2 = tk.Frame(frame, height=1, bg="grey", width=280)
separator2.pack(pady=10)

block_driver_button = tk.Button(
    frame,
    text="Zablokuj Instalację Sterowników",
    command=block_driver_installation,
    image=gradient_img,
    compound="center",
    font=("Arial", 10, "bold"),
    fg="white",
    bg="#505050",
    bd=0,
)
block_driver_button.pack(pady=5)

unblock_driver_button = tk.Button(
    frame,
    text="Odblokuj Instalację Sterowników",
    command=unblock_driver_installation,
    image=gradient_img,
    compound="center",
    font=("Arial", 10, "bold"),
    fg="white",
    bg="#505050",
    bd=0,
)
unblock_driver_button.pack(pady=5)

root.mainloop()