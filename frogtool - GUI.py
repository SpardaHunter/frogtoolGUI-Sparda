import os
import re
import binascii
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import psutil

class StopExecution(Exception):
    pass

drive_combobox = None

def browse_drive():
    global drive_combobox
    drives = [drive.device for drive in psutil.disk_partitions()] if os.name == "nt" else [drive.mountpoint for drive in psutil.disk_partitions()]
    drive_combobox['values'] = drives

def int_to_4_bytes_reverse(src_int):
    hex_string = format(src_int, "x").rjust(8, "0")[0:8]
    return binascii.unhexlify(hex_string)[::-1]

def check_file(file_entry, supported_exts):
    file_regex = ".+\\.(" + "|".join(supported_exts) + ")$"
    return file_entry.is_file() and re.search(file_regex, file_entry.name.lower())

def check_rom(file_entry):
    return check_file(file_entry, supported_rom_ext)

try:
    from PIL import Image, ImageDraw
    image_lib_avail = True
except ImportError:
    Image = None
    ImageDraw = None
    image_lib_avail = False

if os.name == "nt":
    import ctypes
    if ctypes.windll:
        ctypes.windll.kernel32.SetConsoleTitleW("frogtool")

systems = {
    "ARCADE": ["mswb7.tax", "msdtc.nec", "mfpmp.bvs"],
    "FC":     ["rdbui.tax", "fhcfg.nec", "nethn.bvs"],
    "GB":     ["vdsdc.tax", "umboa.nec", "qdvd6.bvs"],
    "GBA":    ["vfnet.tax", "htuiw.nec", "sppnp.bvs"],
    "GBC":    ["pnpui.tax", "wjere.nec", "mgdel.bvs"],
    "MD":     ["scksp.tax", "setxa.nec", "wmiui.bvs"],
    "SFC":    ["urefs.tax", "adsnt.nec", "xvb6c.bvs"]
}

supported_rom_ext = [
    "bkp", "zip", "zfc", "zsf", "zmd", "zgb", "zfb", "smc", "fig", "sfc", "gd3", "gd7", "dx2", "bsx", "swc", "nes",
    "nfc", "fds", "unf", "gba", "agb", "gbz", "gbc", "gb", "sgb", "bin", "md", "smd", "gen", "sms"
]

class StopExecution(Exception):
    pass

def strip_file_extension(name):
    parts = name.split(".")
    parts.pop()
    return ".".join(parts)

def sort_normal(unsorted_list):
    return sorted(unsorted_list)

def sort_without_file_ext(unsorted_list):
    stripped_names = list(map(strip_file_extension, unsorted_list))
    sort_map = dict(zip(unsorted_list, stripped_names))
    return sorted(sort_map, key=sort_map.get)

def process_sys(drive, system):
    print(f"Processing {system}")

    if not drive:
        messagebox.showerror("Error", "No se ha seleccionado un dispositivo.")
        return

    roms_path = f"{drive}/{system}"
    if not os.path.isdir(roms_path):
        messagebox.showerror("Error", f"No se encontró la carpeta {roms_path}. Verifique que la ruta proporcionada sea válida.")
        return

    for file_key in range(3):
        index_path = f"{drive}/Resources/{systems[system][file_key]}"
        check_and_back_up_file(index_path)

    print(f"Looking for files in {roms_path}")

    files = [file for file in os.scandir(roms_path) if check_rom(file)]
    no_files = len(files)

    if no_files == 0:
        print("No ROMs found! Type Y to confirm you want to save an empty game list, or anything else to cancel")
        conf = input()
        if conf.upper() != "Y":
            print("Cancelling, game list not modified")
            return
    else:
        print(f"Found {no_files} ROMs")

    filenames = [file.name for file in files]
    stripped_names = [strip_file_extension(name) for name in filenames]

    name_map_files = dict(zip(filenames, filenames))
    name_map_cn = dict(zip(filenames, stripped_names))
    name_map_pinyin = dict(zip(filenames, stripped_names))

    write_index_file(name_map_files, sort_without_file_ext, f"{drive}/Resources/{systems[system][0]}")
    write_index_file(name_map_cn, sort_normal, f"{drive}/Resources/{systems[system][1]}")
    write_index_file(name_map_pinyin, sort_normal, f"{drive}/Resources/{systems[system][2]}")

    print("Done\n")

def check_and_back_up_file(file_path):
    if not os.path.exists(file_path):
        print(f"! Couldn't find game list file {file_path}")
        print("  Check the provided path points to an SF2000 SD card!")
        raise StopExecution

    if not os.path.exists(f"{file_path}_orig"):
        print(f"Backing up {file_path} as {file_path}_orig")
        try:
            shutil.copyfile(file_path, f"{file_path}_orig")
        except (OSError, IOError):
            print("! Failed to copy file.")
            print("  Check the SD card and Resources directory are writable.")
            raise StopExecution

def write_index_file(name_map, sort_func, index_path):
    sorted_filenames = sorted(name_map.keys())
    names_bytes = b""
    pointers_by_name = {}

    for filename in sorted_filenames:
        display_name = name_map[filename]
        current_pointer = len(names_bytes)
        pointers_by_name[display_name] = current_pointer
        names_bytes += display_name.encode('utf-8') + chr(0).encode('utf-8')

    metadata_bytes = int_to_4_bytes_reverse(len(name_map))

    sorted_display_names = sort_func(name_map.values())
    sorted_pointers = map(lambda name: pointers_by_name[name], sorted_display_names)

    for current_pointer in sorted_pointers:
        metadata_bytes += int_to_4_bytes_reverse(current_pointer)

    new_index_content = metadata_bytes + names_bytes

    print(f"Overwriting {index_path}")
    try:
        with open(index_path, 'wb') as file_handle:
            file_handle.write(new_index_content)
    except (IOError, OSError):
        print("! Failed overwriting file.")
        print("  Check the SD card and file are writable, and the file is not open in another program.")
        raise StopExecution

def show_popup():
    messagebox.showinfo("Mensaje", "¡Lista juegos actualizada!")

def run():
    global drive_combobox
    root = tk.Tk()
    root.title("Frogtool GUI")

    def execute_conversion():
        drive = drive_combobox.get()
        system = system_var.get()

        if not drive:
            print("No se ha seleccionado un dispositivo.")
            return

        try:
            keys_to_process = systems.keys() if system == "ALL" else [system]
            for syskey in keys_to_process:
                process_sys(drive, syskey)

            show_popup()

        except StopExecution:
            print("Error al actualizar la lista de juegos.")

    drive_label = tk.Label(root, text="Ubicación de la tarjeta SD SF2000:")
    drive_combobox = ttk.Combobox(root, state="readonly", width=37)
    browse_drive_button = tk.Button(root, text="Refrescar dispositivos", command=browse_drive)

    system_label = tk.Label(root, text="Seleccionar Sistema:")
    system_var = tk.StringVar(root)
    system_var.set("ARCADE")
    system_menu = tk.OptionMenu(root, system_var, *systems.keys())

    execute_button = tk.Button(root, text="Actualizar lista juegos", command=execute_conversion)

    drive_label.pack(pady=5)
    drive_combobox.pack(pady=5)
    browse_drive_button.pack(pady=5)

    system_label.pack(pady=5)
    system_menu.pack(pady=5)

    execute_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run()
