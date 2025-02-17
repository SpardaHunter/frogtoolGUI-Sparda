# frogtoolGUI-Sparda
Frogtool GUI version to update game list on SF2000

Game List Updater


![imagen](https://github.com/user-attachments/assets/9625eeef-a7cd-4475-a509-961189d50096)


Description: Updates the list of games on your SF2000

How it works:

- Select the location where you have the resources folder using the "Browse" button. (If it is a logical drive: D:, E:, etc.).
- Select the system to update the game list (Select "ALL" if you want all of them to be updated).
- Press the "Update Game List" button to start the process.

Additional explanation:
The program automatically checks if you have Foldername.ini or FoldernamX.ini, it will read the number of systems you have selected and it will read the names that each system has.
If the system folder does not exist, it will create a folder with its name and a subfolder with the name "save".
If it has no games it will create a file with 0 roms.
