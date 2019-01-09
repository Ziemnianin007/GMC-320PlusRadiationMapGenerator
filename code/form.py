import PySide2
import sys
import os.path
import os
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QLineEdit, QListView, QFileDialog, QMainWindow, QLabel
from PySide2.QtCore import QFile, QObject, QStringListModel, QModelIndex
from PySide2.QtGui import QCloseEvent
import tkinter as tk
from tkinter import filedialog
import time
import datetime
from scanf import scanf

class Form(QObject):

    def __init__(self, ui_file, application, parent=None):

        #creating Gui
        super(Form, self).__init__(parent)
        # open UI
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)
        # loading GUI
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        # console displaying things
        self.radiationStatus = self.window.findChild(QLabel, 'radiationStatus')
        self.gpsStatus = self.window.findChild(QLabel, 'gpsStatus')
        self.generateStatus = self.window.findChild(QLabel, 'generateStatus')

        # button action
        btn = self.window.findChild(QPushButton, 'radiationData')
        btn.clicked.connect(self.radiationData)

        btn = self.window.findChild(QPushButton, 'gpsData')
        btn.clicked.connect(self.gpsData)

        btn = self.window.findChild(QPushButton, 'generate')
        btn.clicked.connect(self.generate)

        self.generatedData = None
        self.gpsDataList = None
        self.radiationDataList = None

        self.window.show()

    def radiationData(self):
        path = self.openDialogFunction('.csv')
        print("Loading radiation data from: " + str(path.name))
        file = open(path.name)

        #checking header
        header = file.readline()
        if not header.__contains__("GMC Data Viewer"):
            print("INCORRECT DATA FILE HEADER, should contain \'GMC Data Viewer\'")
            self.radiationStatus.setText('Wrong header, aborted')
            file.close()
            return
        else:
            print("Correct header")
        self.radiationDataList = []

        #searching end of file
        file.seek(0, 2)  # Jumps to the end
        endOfFile = file.tell()  # Give you the end location (characters from start)
        print("file have: " + str(endOfFile) + " character")
        file.seek(0)  # Jump to the beginning of the file again

        #skipping lines, seek seems work randomly here
        file.readline()
        file.readline()
        file.readline()

        #loading data
        while file.tell() != endOfFile:
            line = file.readline()
            self.radiationDataList.append(line)
        print('Radiation data loaded')
        print("First data line: " + self.radiationDataList[0])
        print("Last data line: " + self.radiationDataList[-1])
        self.radiationStatus.setText('Radiation data loaded, contains: ' + str(len(self.radiationDataList)) + " lines")

    def gpsData(self):
        path = self.openDialogFunction('.gpx')
        print("Loading gps data from: " + str(path.name))
        file = open(path.name)

        #checking header
        header = file.readline()
        if not header.__contains__("GPSLogger"):
            print("INCORRECT DATA FILE HEADER, should contain \'GPSLogger\'")
            self.gpsStatus.setText('Wrong header, aborted')
            file.close()
            return
        else:
            print("Correct header")
        self.gpsDataList = []

        #searching end of file
        file.seek(0, 2)  # Jumps to the end
        endOfFile = file.tell()  # Give you the end location (characters from start)
        print("file have: " + str(endOfFile) + " character")
        file.seek(0)  # Jump to the beginning of the file again

        #loading data
        while file.tell() != endOfFile:
            line = file.readline()
            if (line.__contains__('<trkpt ')):
                begin = line.find('<trkpt ')
                self.gpsDataList.append(line[begin:-1])
        print('GPS data loaded')
        print("First data line: " + self.gpsDataList[0])
        print("Last data line: " + self.gpsDataList[-1])
        self.gpsStatus.setText('GPS data loaded, contains: ' + str(len(self.gpsDataList)) + " lines")

    def generate(self):
        if(self.gpsDataList is None):
            print('Load gps data')
            self.generateStatus.setText("First load gps data")
            return
        if(self.radiationDataList is None):
            print('Load radiation data')
            self.generateStatus.setText("First load radiation data")
            return
        #gets lat, lon, day, time, geoidheight
        self.gpsDataList
        geoidheight = None
        for line in self.gpsDataList:
            sLine = line.split(' ')
            lat = None
            lon = None
            date = None
            time = None
            uS = None
            lat = scanf('lat="%f"', sLine[1])[0]
            lon = scanf('lon="%f">%s', sLine[2])[0]
            date = scanf('%s><ele>%f</ele><time>%sT%s', sLine[2])[2]
            time = scanf('%s><ele>%f</ele><time>%sT%sZ%s', sLine[2])[3]
            if (sLine[2].__contains__('<geoidheight>')):
                geoidheight = scanf('%s<geoidheight>%f</geoidheight>%s', sLine[2])[1]
            else:
                if(geoidheight is None):
                    geoidheight = 0.0
            uS = None
            lLine = (lat,lon,geoidheight,date,time, uS)
            self.generatedData.append(lLine)

        #adding radiation to right time
        self.radiationDataList
        

        self.generatedData
        #saving data
        if(self.generatedData is not None):
            print('Saving data')
            path = self.file_save_window()
            self.file_save_path(path, self.generatedData, 'csv', '.csv')
            print('Saved properly')
            self.generateStatus.setText('Radiation files saved to ' + path)
        else:
            print('Files dont match, check dates')
            self.generateStatus.setText('Files dont match, check dates')

    def openDialogFunction(self, extension):
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

    def fileSaveWindow(self):
        print("Save dialog function")
        root = tk.Tk()
        root.withdraw()

        current_time = time.localtime()
        title = "Save radiation data",
        fileName = "RadiationData" + str(current_time[2])+str(current_time[1])+str(current_time[0])+"_"+str(current_time[3])+str(current_time[4])+str(current_time[5]),
        dirName = None,
        fileExt = ".csv",
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


    def file_save_path(self, path, toSave, name, format):
        path_ok = str(path)[:-4] + '_' + str(name) + format
        file_path = open(path_ok, "w+")
        file_path.writelines('\n'.join(toSave))
        file_path.close()  # `()` was missing.


