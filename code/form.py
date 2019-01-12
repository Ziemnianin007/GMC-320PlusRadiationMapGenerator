import PySide2
import sys
import os.path
import os
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QLineEdit, QListView, QFileDialog, QMainWindow, QLabel
from PySide2.QtCore import QFile, QObject, QStringListModel, QModelIndex
from PySide2.QtGui import QCloseEvent
import time
import datetime
from dataConverter import dataConverter
import fileOperation

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

        self.gpsDateStatus = self.window.findChild(QLabel, 'GPSDate')
        self.radiationDateStatus = self.window.findChild(QLabel, 'radiationDate')
        self.intersectionDateStatus = self.window.findChild(QLabel, 'intersectionDate')

        self.timeZone = self.window.findChild(QLineEdit, 'timeZone')

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
        path = fileOperation.openDialogFunction('.csv')
        radiationDataConverter = dataConverter()
        converted = radiationDataConverter.radiationDataLoad(path)
        self.radiationStatus.setText(converted[1])
        self.radiationDataList = converted[0]

    def gpsData(self):
        path = fileOperation.openDialogFunction('.gpx')
        gpsDataConverter = dataConverter()
        converted = gpsDataConverter.gpsDataLoad(path)
        self.gpsStatus.setText(converted[1])
        self.gpsDataList = converted[0]

    def generate(self):
        if(self.gpsDataList is None):
            print('Load gps data')
            self.generateStatus.setText("First load gps data")
            return
        if(self.radiationDataList is None):
            print('Load radiation data')
            self.generateStatus.setText("First load radiation data")
            return
        self.generatedData = None

        timeZone = int(self.timeZone.text())
        mergeGeneratedData = dataConverter()
        allData = mergeGeneratedData.mergeRadiationWithGps(self.gpsDataList, self.radiationDataList, timeZone)
        self.generatedData = allData[0]
        #return gpsDataList, gpsDateRange, radiationDateRange, intersectionRange
        self.gpsDateStatus.setText(allData[1])
        self.radiationDateStatus.setText(allData[2])
        self.intersectionDateStatus.setText(allData[3])
        #saving data
        if(self.generatedData is not None):
            print('Saving data')
            # return gpsDataList, gpsMin ,gpsMax ,radMin ,radMax ,intersection[0], intersection[1]
            path = fileOperation.fileSaveWindow()
            fileOperation.fileSavePath(path, self.generatedData, '.csv')
            print('Saved properly')
            self.generateStatus.setText('Radiation files saved to ' + path)
        else:
            print('Files dont match, check dates')
            self.generateStatus.setText('Files dont match, check dates')




