from scanf import scanf
import time
import datetime

class dataConverter():
    def radiationDataLoad(self, path):
        print("Loading radiation data from: " + str(path.name))
        file = open(path.name)

        radiationStatus = None
        #checking header
        header = file.readline()
        if not header.__contains__("GMC Data Viewer"):
            print("INCORRECT DATA FILE HEADER, should contain \'GMC Data Viewer\'")
            radiationStatus = 'Wrong header, aborted'
            file.close()
            return (None, radiationStatus)
        else:
            print("Correct header")
        radiationDataList = []

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
            radiationDataList.append(line)
        print('Radiation data loaded')
        print("First data line: " + radiationDataList[0])
        print("Last data line: " + radiationDataList[-1])
        radiationStatus = 'Radiation data loaded, contains: ' + str(len(radiationDataList)) + " lines"
        print(radiationStatus)
        return (radiationDataList, radiationStatus)

    def gpsDataLoad(self, path):
        print("Loading gps data from: " + str(path.name))
        file = open(path.name)

        gpsStatus = None
        #checking header
        header = file.readline()
        if not header.__contains__("GPSLogger"):
            print("INCORRECT DATA FILE HEADER, should contain \'GPSLogger\'")
            gpsStatus = 'Wrong header, aborted'
            file.close()
            return (None, gpsStatus)
        else:
            print("Correct header")
        gpsDataList = []

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
                gpsDataList.append(line[begin:-1])
        print('GPS data loaded')
        print("First data line: " + gpsDataList[0])
        print("Last data line: " + gpsDataList[-1])
        gpsStatus = 'GPS data loaded, contains: ' + str(len(gpsDataList)) + " lines"
        print(gpsStatus)
        return(gpsDataList, gpsStatus)

    def mergeRadiationWithGps(self, gpsData, radiationData, timeZone):
        print('merging radiation with gps')
        #gets lat, lon, day, time, geoidheight\
        gpsDataList = self.convertGPSTextToList(gpsData, timeZone)
        gpsDateRange = 'GPS data from: ' + str(gpsDataList[0][3]) + ' ' + str(gpsDataList[0][4]) + ' to: '+ str(gpsDataList[-1][3]) + ' ' + str(gpsDataList[-1][4])
        print(gpsDateRange)

        # radiation line format = (timeAbsolute, dateS, timeS, howOften, uS, splittedLine[3:])
        radiationDataList = self.convertRadiationTextToList(radiationData)
        radiationDateRange = 'Radiation data from: ' + str(radiationDataList[0][1]) + ' ' + str(radiationDataList[0][2]) + ' to: '+ str(radiationDataList[-1][1]) + ' ' + str(radiationDataList[-1][2])
        print(radiationDateRange)
        gpsMin = gpsDataList[0][6]
        gpsMax = gpsDataList[-1][6]
        radMin = radiationDataList[0][0]
        radMax = radiationDataList[-1][0]
        intersection = self.intersection(gpsMin,gpsMax,radMin,radMax)
        intersectionRange = 'Intersaction range from: ' + str(intersection[0]) + ' to ' + str(intersection[1])
        if(intersection[0] is None):
            return None
        #adding radiation to right time
        searchRange = 90 #in seconds
        indexRadiation = 0
        lastLine = gpsDataList[0]
        for line in gpsDataList:
            #gps line format = (lat,lon,geoidheight,dateL ,timeL, uS, timeAbsolute) gps data
            #radiation line format = (timeAbsolute, dateS, timeS, howOften, uS, splittedLine[3:])
            while True:
                if (line[6] > radiationDataList[indexRadiation][0]):
                    # gps data later than radiation data
                    if (line[6] - searchRange < radiationDataList[indexRadiation][0]):

                        if(line[6] - searchRange > radiationDataList[indexRadiation][0]):
                            #gps data outside range
                            #print('gps data outside range')
                            break
                        else:
                            # gps data in search range
                            #print('gps data in search range, uS added')
                            line[5] = format(radiationDataList[indexRadiation][4], '.15f')  #uS
                            #print('uS: '+ str(line[5])+' GPS: ', line[3], ' ', line[4], ' ', line[6], 'Radiation: ',radiationDataList[indexRadiation][1], ' ', radiationDataList[indexRadiation][2], ' ',radiationDataList[indexRadiation][0])
                            break
                    else:
                        # too much time between dates
                        if(indexRadiation < len(radiationDataList)-1):
                            #print('gps later than radiation data, too much time between dates')
                            indexRadiation += 1
                        else:
                            break
                else:
                    #print('gps data earlier than radiation data')
                    break
                    # gps data earlier than radiation data
            lastLine = line
        #cleaning clear spot
        for i in reversed(range(0 , len(gpsDataList))):
            if(gpsDataList[i][5] is None):
                gpsDataList.pop(i)
        print(gpsDataList)
        print('Matched ' + str(len(gpsDataList)) + ' location')
        return gpsDataList, gpsDateRange, radiationDateRange, intersectionRange





    def convertGPSTextToList(self, gpsData, timeZone):
        print('converting gps text to list')
        generatedData = []
        geoidheight = None
        for line in gpsData:
            sLine = line.split(' ')
            lat = None
            lon = None
            dateL = None
            timeL = None
            uS = None
            timeAbsolute = None
            lat = scanf('lat="%f"', sLine[1])[0]
            lon = scanf('lon="%f">%s', sLine[2])[0]
            dateL = scanf('%s<time>%sT%s', sLine[2])[1]
            timeL = scanf('%s<time>%sT%sZ%s', sLine[2])[2]
            if (sLine[2].__contains__('<geoidheight>')):
                geoidheight = scanf('%s<geoidheight>%f</geoidheight>%s', sLine[2])[1]
            else:
                if(geoidheight is None):
                    geoidheight = 0.0

            dateS = scanf('%d-%d-%d', dateL)
            timeS = scanf('%d:%d:%d.%d', timeL)
            timeS = datetime.datetime(dateS[0], dateS[1], dateS[2], timeS[0], timeS[1], timeS[2], timeS[3])
            timeAbsolute = time.mktime(timeS.timetuple()) + timeZone * 60 * 60
            lLine = [lat,lon,geoidheight,dateL ,timeL, uS, timeAbsolute]
            generatedData.append(lLine)
        print('GPS data dates from: ' + str(generatedData[0][6]) + ' to: ' + str(generatedData[-1][6]))
        return generatedData

    def convertRadiationTextToList(self, radiationData):
        print('converting radiation text to list')
        generatedData = []
        for line in radiationData:
            splittedLine = line.split(',')
            dateL = None
            timeL = None
            timeAbsolute = None
            datatimeSplitted = splittedLine[0].split(' ')
            dateS = scanf('%d-%d-%d', datatimeSplitted[0])
            timeS = scanf('%d:%d', datatimeSplitted[1])
            timeL = datetime.datetime(dateS[0], dateS[1], dateS[2], timeS[0], timeS[1], 30, 0)
            timeAbsolute = time.mktime(timeL.timetuple())
            uS = str(splittedLine[2])
            if('.' in uS):
                uS = float(uS)
            else:
                uS =  int(uS) * 6.49956E-09
            howOften = splittedLine[1]
            lLine = [timeAbsolute, dateS, timeS, howOften, uS, splittedLine[3:]]
            generatedData.append(lLine)
        print('Radiation data dates from: ' + str(generatedData[0][0]) + ' to: ' + str(generatedData[-1][0]))
        return generatedData

    def intersection(self,min1,max1,min2,max2):
        #should be 1 2 3 4
        m1l = min(min1,min2)
        m2l = max(min1,min2)
        m3l = min(max1,max2)
        m4l = max(max1,max2)

        if(m1l < m2l < m3l and m2l < m3l < m4l):
            #okey
            print('Date matched between ', m2l,' to ', m3l)
            return (m2l, m3l)
        else:
            #wrong
            print('date not matched')
            return (None, None)



