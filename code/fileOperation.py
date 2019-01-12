import tkinter as tk
from tkinter import filedialog
import time

def openDialogFunction(extension):
    print("Open dialog function")
    root = tk.Tk()
    root.withdraw()

    title = "Open file",
    fileName = 'name',
    dirName = None,
    fileExt = extension,
    asFile = False
    fileTypes = [('text files', extension), ('all files', '.*')]
    # define options for opening
    options = {}
    options['defaultextension'] = fileExt
    options['filetypes'] = fileTypes
    options['initialdir'] = dirName
    options['initialfile'] = fileName
    options['title'] = title

    file_path = filedialog.askopenfile(mode='r', **options)
    if file_path is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        print("No file selected")
        return
    return file_path


def fileSaveWindow(additionalTitle = '',extension = '.csv'):
    print("Save dialog function")
    root = tk.Tk()
    root.withdraw()

    current_time = time.localtime()
    title = "Save radiation data",
    fileName = "RadiationData" + str(current_time[2]) + str(current_time[1]) + str(current_time[0]) + "_" + str(
        current_time[3]) + str(current_time[4]) + str(current_time[5]),
    dirName = None,
    fileExt = extension,
    asFile = False
    fileTypes = [('text files', '.csv'), ('all files', '.*')]
    # define options for opening
    options = {}
    options['defaultextension'] = fileExt
    options['filetypes'] = fileTypes
    options['initialdir'] = dirName
    options['initialfile'] = fileName
    options['title'] = title

    file_path = filedialog.asksaveasfile(mode='w', **options)
    if file_path is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        print("No file selected")
        return
    file_path.close()
    return str(file_path.name)


def fileSavePath(path, toSave, format = ''):
    path_ok = str(path)[:-4] + format
    file_path = open(path_ok, "w+")
    for i1 in range(0, len(toSave)):
        for i2 in range(0, len(toSave[i1])):
            toSave[i1][i2] = str(toSave[i1][i2])
        toSave[i1] = ' '.join(toSave[i1])

    toSave = '\n'.join(toSave)
    file_path.writelines('lat lon high date time uS/h absoluteTime\n')
    file_path.writelines(str(toSave))
    file_path.close()  # `()` was missing.