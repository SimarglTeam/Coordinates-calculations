UTC_TIME = 3
SATELLITE_NAMES = ["ISS (ZARYA)", "CALSPHERE 1", "NOAA 19"]
WEBSITE = "https://celestrak.com/NORAD/elements/active.txt"
LAT = '60.0066 N'
LON = '30.3784 E'
OBSERVATION_TIME = 1
DATA_UPDATE_INTERVAL = 120
fileOut = "out.txt"

from skyfield.api import load, Topos
from datetime import timedelta
import pathlib
import os

def get_tle(site):
    sattelites = load.tle(site)
    return sattelites

def satellite_location_relative_antenna(satellite, currTime):
    location = Topos(LAT, LON)
    difference = satellite - location
    topocentric = difference.at(currTime)
    alt, az, distance = topocentric.altaz()
    return alt, az

def curr_time(timescale):
    instant_time = timescale.now()
    return instant_time

def main_func(site, satellite, utcTime, interval, obsTimeInit, filePathOut):
    outputList = []
    dataList = []
    outputList1 = []

    satellites = get_tle(site)
    ts = load.timescale()

    for satName in satellite:
        time = curr_time(ts)
        obsTime = obsTimeInit * 24 * 3600

        if (outputList != None):
            outputList.append('\n' + satName)
        else:
            outputList.append(satName)

        while obsTime > 0:
            alt, az = satellite_location_relative_antenna(satellites[satName], time)
            if alt.degrees > 0:
                outputList.append('Time:' + str(time.utc_datetime() + timedelta(hours=utcTime)) + ' ' + ':Azimuth'+ "%16s" % str(az) +' '+ 'Elevation:' + "%16s" % str(alt))
                dataList.append([satName, time.utc_datetime() + timedelta(hours=utcTime), az, alt])
            obsTime = obsTime - interval
            time = ts.utc(time.utc_datetime() + timedelta(seconds=interval))

    sortedList = sort_sat(dataList, interval)
    for i in range(0, len(sortedList)):
        outputList1.append('SatName:' + str(sortedList[i][0]) + ' ' + 'Time:' + str(sortedList[i][1]) + ' ' + 'Azimuth:' + '%16s'%str(sortedList[i][2]) + ' ' + 'Elevation:' + '%16s'%str(sortedList[i][3]))

    generate_txt_file(filePathOut, outputList1)
    return


def generate_txt_file(filePathOut, outputList):
    strBuf = ""
    for txtRecord in outputList:
        if (txtRecord != None):
            strBuf += str(txtRecord) + '\n'
    file_write_buf(filePathOut, strBuf)
    return

def file_write_buf(filePath, strBuf):
    encodingFile = 'windows-1251'
    outDir = os.path.split(filePath)[0]
    pathlib.Path(outDir).mkdir(parents=True, exist_ok=True)
    fo = open(filePath, "w+", encoding=encodingFile)
    fo.write(strBuf)
    fo.close()
    return

def sort_sat(dataList, interval):
    sortedList = []
    while (len(dataList)!= 0):
        counter = 0
        find = False
        out = False

        if (len(sortedList) != 0 and (len(dataList) != 0)):
            earlistFlight = min(dataList, key= lambda x: x[1])
            if (earlistFlight[1] <= sortedList[len(sortedList) - 1][1]):
                while counter < (len(dataList) - 1) and out == False:
                    if (dataList[counter] == earlistFlight and find == False):
                        find = True
                        while find == True:
                            if ((dataList[counter + 1][1] - dataList[counter][1]) == timedelta(seconds=interval)):
                                dataList.pop(counter)
                            else:
                                dataList.pop(counter)
                                out = True
                                find = False
                    else:
                        counter += 1

        counter = 0
        find = False
        out = False
        if (len(dataList) != 0):
            earlistFlight = min(dataList, key= lambda x: x[1])
            while counter < (len(dataList) - 1) and out == False:
                if (dataList[counter] == earlistFlight and find == False):
                    sortedList.append(earlistFlight)
                    find = True
                    while counter < (len(dataList) - 1) and find == True:
                        a = timedelta(seconds=interval)
                        if ((dataList[counter+1][1] - dataList[counter][1]) == timedelta(seconds=interval)):
                            sortedList.append(dataList[counter + 1])
                            counter += 1
                        else:
                            out = True
                            find = False
                counter +=1

        if (len(sortedList) != 0):
            k = 0
            while k < len(dataList):
                for l in range(0, len(sortedList)):
                    if (dataList[k] == sortedList[l]):
                        dataList.pop(k)
                k += 1

    return sortedList

main_func(WEBSITE, SATELLITE_NAMES, UTC_TIME, DATA_UPDATE_INTERVAL, OBSERVATION_TIME, fileOut)