import os
import re
import binascii
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class StopExecution(Exception):
    pass

drive_combobox = None
path_entry = None
system_var = None
system_menu = None

def on_drive_selected(event):
    global custom_path_var, systems, system_var, system_menu
    # Reiniciar systems antes de buscar el nuevo Foldername.ini o Foldernamx.ini
    systems = {
        "FC": ["rdbui.tax", "fhcfg.nec", "nethn.bvs"],
        "SFC": ["urefs.tax", "adsnt.nec", "xvb6c.bvs"],
        "MD": ["scksp.tax", "setxa.nec", "wmiui.bvs"],
        "GB": ["vdsdc.tax", "umboa.nec", "qdvd6.bvs"],
        "GBC": ["pnpui.tax", "wjere.nec", "mgdel.bvs"],
        "GBA": ["vfnet.tax", "htuiw.nec", "sppnp.bvs"],
        "ARCADE": ["mswb7.tax", "msdtc.nec", "mfpmp.bvs"],
        "ALL": []  # Placeholder for "ALL" option
    }
    
    check_and_find_ini()

def int_to_4_bytes_reverse(src_int):
    hex_string = format(src_int, "x").rjust(8, "0")[0:8]
    return binascii.unhexlify(hex_string)[::-1]

def find_foldername_ini(path):
    global systems, system_var, system_menu
    ini_path = os.path.join(path, "Resources", "Foldername.ini")
    ini_path_x = os.path.join(path, "Resources", "Foldernamx.ini")
    ini_to_load = None

    # Buscar el archivo Foldername.ini o Foldernamx.ini
    if os.path.exists(ini_path):
        ini_to_load = ini_path
    elif os.path.exists(ini_path_x):
        ini_to_load = ini_path_x

    if not ini_to_load:
        messagebox.showerror("Error", "Neither Foldername.ini nor Foldernamx.ini were found.")
        return

    try:
        with open(ini_to_load, "r", encoding="utf-8") as file:
            lines = file.readlines()

        if len(lines) < 3:
            messagebox.showerror("Error", f"Insufficient lines in {ini_to_load}")
            return

        # Leer el número de sistemas (basado en la antepenúltima línea)
        last_number_line = lines[-3].strip().split()[0]
        try:
            num_lines = int(last_number_line) - 1  
        except ValueError:
            messagebox.showerror("Error", f"Invalid number format in antepenultimate line: {last_number_line}")
            return

        if len(lines) < num_lines + 4:  # Asegurarse de tener suficientes líneas
            messagebox.showerror("Error", f"Not enough lines in {ini_to_load} to process {num_lines}.")
            return

        # Leer las líneas correspondientes a los sistemas, que comienzan en la línea 5 (índice 4)
        new_systems = []
        for line in lines[4:4 + num_lines]:
            parts = line.strip().split(" ", 1)
            # Agregar solo el nombre del sistema (independientemente de lo que diga)
            if len(parts) > 1:
                new_systems.append(parts[1])
            else:
                new_systems.append(parts[0])

        # Limpiar el diccionario de sistemas antes de cargar los nuevos
        systems = {}

        # Si se cargó Foldernamx.ini, actualizar systems con los valores de Foldernamx
        if ini_to_load == ini_path_x:
            systems_data = {
                "FC": ["m01.ta", "m01.ne", "m01.bv"],
                "SFC": ["m02.ta", "m02.ne", "m02.bv"],
                "MD": ["m03.ta", "m03.ne", "m03.bv"],
                "GB": ["m04.ta", "m04.ne", "m04.bv"],
                "GBC": ["m05.ta", "m05.ne", "m05.bv"],
                "GBA": ["m06.ta", "m06.ne", "m06.bv"],
                "ARCADE": ["m07.ta", "m07.ne", "m07.bv"],
                "SEGA": ["m08.ta", "m08.ne", "m08.bv"],
                "ATARI_NGP": ["m09.ta", "m09.ne", "m09.bv"],
                "WONDERSWAN": ["m10.ta", "m10.ne", "m10.bv"],
                "PCE": ["m11.ta", "m11.ne", "m11.bv"],
                "MULTICORE": ["m12.ta", "m12.ne", "m12.bv"]
            }
        else:
            systems_data = {
                "FC": ["rdbui.tax", "fhcfg.nec", "nethn.bvs"],
                "SFC": ["urefs.tax", "adsnt.nec", "xvb6c.bvs"],
                "MD": ["scksp.tax", "setxa.nec", "wmiui.bvs"],
                "GB": ["vdsdc.tax", "umboa.nec", "qdvd6.bvs"],
                "GBC": ["pnpui.tax", "wjere.nec", "mgdel.bvs"],
                "GBA": ["vfnet.tax", "htuiw.nec", "sppnp.bvs"],
                "ARCADE": ["mswb7.tax", "msdtc.nec", "mfpmp.bvs"],
                "ALL": []  # Placeholder for "ALL" option
            }

        # Actualizar los sistemas en el diccionario utilizando los nombres leídos del archivo
        system_keys = list(systems_data.keys())  # Usamos las claves predeterminadas

        # Asegurarse de que la longitud de new_systems y system_keys coincidan
        for idx, system_name in enumerate(new_systems):
            if idx < len(system_keys):
                systems[system_name] = systems_data[system_keys[idx]]

        systems["ALL"] = []

        # Actualizar el menú de selección de sistema
        menu = system_menu["menu"]
        menu.delete(0, "end")
        for key in systems.keys():
            menu.add_command(label=key, command=tk._setit(system_var, key))

        system_var.set("ALL")
        messagebox.showinfo("Success", "Systems updated successfully from Foldername.ini or Foldernamx.ini!")
        print("Updated systems:", systems)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to read or process {ini_to_load}: {e}")


def check_and_find_ini():
    global path_entry, systems
    path = path_entry.get()
    if path:
        find_foldername_ini(path)

def check_file(file_entry, supported_exts):
    file_regex = ".+\\.(" + "|".join(supported_exts) + ")$"
    return file_entry.is_file() and re.search(file_regex, file_entry.name.lower())

def check_rom(file_entry):
    return check_file(file_entry, supported_rom_ext)

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

def process_sys(path, system):
    print(f"Processing {system}")

    if not path:
        messagebox.showerror("Error", "No path has been selected.")
        return

    roms_path = os.path.join(path, system)
    if not os.path.isdir(roms_path):
        os.makedirs(os.path.join(roms_path, "save"), exist_ok=True)

    for file_key in range(3):
        index_path = os.path.join(path, "Resources", systems[system][file_key])
        check_and_generate_file(index_path)

    print(f"Looking for files in {roms_path}")

    files = [file for file in os.scandir(roms_path) if check_rom(file)]
    no_files = len(files)

    filenames = [file.name for file in files] if files else []
    stripped_names = [strip_file_extension(name) for name in filenames] if files else []

    name_map_files = dict(zip(filenames, filenames))
    name_map_cn = dict(zip(filenames, stripped_names))
    name_map_pinyin = dict(zip(filenames, stripped_names))

    write_index_file(name_map_files, sort_without_file_ext, os.path.join(path, "Resources", systems[system][0]))
    write_index_file(name_map_cn, sort_normal, os.path.join(path, "Resources", systems[system][1]))
    write_index_file(name_map_pinyin, sort_normal, os.path.join(path, "Resources", systems[system][2]))

    print(f"Game list for {system} updated with {no_files} ROMs.\n")

def check_and_generate_file(file_path):
    if not os.path.exists(file_path):
        print(f"{file_path} not found. Creating a blank file.")
        try:
            with open(file_path, 'wb') as file_handle:
                file_handle.write(b'')
        except (OSError, IOError):
            print(f"! Failed to create file: {file_path}")
            print("  Check the path and Resources directory are writable.")
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
        print("  Check the path and file are writable, and the file is not open in another program.")
        raise StopExecution

def select_folder():
    folder_selected = filedialog.askdirectory(title="Select Folder")
    if folder_selected:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, folder_selected)
        check_and_find_ini()

def show_popup():
    messagebox.showinfo("Message", "Updated games list!")

def run():
    global path_entry, system_var, system_menu
    root = tk.Tk()
    root.title("Frogtool GUI")

    def execute_conversion():
        path = path_entry.get()

        if not path:
            print("No path has been selected.")
            return

        try:
            system = system_var.get()
            if system == "ALL":
                keys_to_process = [key for key in systems.keys() if key != "ALL"]
            else:
                keys_to_process = [system]

            for syskey in keys_to_process:
                process_sys(path, syskey)

            show_popup()

        except StopExecution:
            print("Error updating game list.")

    path_label = tk.Label(root, text="SF2000 Location:")
    path_entry = ttk.Entry(root, width=40)
    path_button = ttk.Button(root, text="Browse", command=select_folder)

    system_label = tk.Label(root, text="Select System:")
    system_var = tk.StringVar(root)
    system_var.set("ALL")
    system_menu = tk.OptionMenu(root, system_var, *systems.keys())

    execute_button = tk.Button(root, text="Update Games List", command=execute_conversion)

    path_label.pack(pady=5)
    path_entry.pack(pady=5)
    path_button.pack(pady=5)
    system_label.pack(pady=5)
    system_menu.pack(pady=5)
    execute_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    systems = {
        "FC": ["rdbui.tax", "fhcfg.nec", "nethn.bvs"],
        "SFC": ["urefs.tax", "adsnt.nec", "xvb6c.bvs"],
        "MD": ["scksp.tax", "setxa.nec", "wmiui.bvs"],
        "GB": ["vdsdc.tax", "umboa.nec", "qdvd6.bvs"],
        "GBC": ["pnpui.tax", "wjere.nec", "mgdel.bvs"],
        "GBA": ["vfnet.tax", "htuiw.nec", "sppnp.bvs"],
        "ARCADE": ["mswb7.tax", "msdtc.nec", "mfpmp.bvs"],
        "ALL": []  # Placeholder for "ALL" option
    }
    supported_rom_ext = [
        "bkp", "zip", "zfc", "zsf", "zmd", "zgb", "zfb", "smc", "fig", "sfc", "gd3", "gd7", "dx2", "bsx", "swc", "nes",
        "nfc", "fds", "unf", "gba", "agb", "gbz", "gbc", "gb", "sgb", "bin", "md", "smd", "gen", "sms"
    ]
    run()
