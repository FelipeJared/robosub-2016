'''
Copyright 2014, Austin Owens, All rights reserved.

.. module::DataLogger
   :synopsis: Logs data to CSV File

:Author: Lawrence Erb
:Date: Created on February 23, 2014
:Description: This module will log all the data from the sub and output it into a CSV file.
'''

import os
import time
import datetime
import csv, codecs, cStringIO

class Writer:
    '''
    This class is what writes the rows and columns and outputs to a CSV file "f"
    '''

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        '''
        Initiates the parameters for the CSV Writer.
        
        **Parameters"": \n
        * **f** - The CSV file.
        * **dialect=csv.excel** - Specifies Excel formatting for the output CSV File.
        * **encoding="utf-8"** - Converts data/unicode-characters using one to four 8-bit bytes.
        * ****kwds** - Keyword arguments in a dictionary. Allows the function to accept an arbitrary number of arguments and/or keyword arguments.
        
        **Returns**: \n
        * **No Return.**\n 
        '''
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        '''
        Writes a row to a CSV file. 
        
        **Parameters**: \n
        * **row** - Data as sequence of strings or numbers.
        
        **Returns**: \n
        * **No Return.**\n
        '''
        
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and re-encode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        '''
        Takes a list of rows and calls writerow on each row in the list.
        
        **Parameters**: \n
        * **rows** - Multiple lists of data as sequences of strings or numbers.
        
        **Returns** : \n
        * **No Return.**\n
        '''
        
        for row in rows:
            self.writerow(row)


class DataLog:
    '''
    This class logs all the subs data into a csv file to be used for later external processing.
    '''
    
    def __init__(self):
        '''
        Initiates parameters and formats/writes data for logging.
        
        **Parameters**: \n
        * **iterationsUntilLogging** - The amount of occurrences you want to pass by until you log information into the file
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.ID = 0
        self.append = False
        
        if (os.path.exists("export.csv")):
            if ((time.time() - os.path.getmtime("export.csv")) > 86000):
                os.rename("export.csv", "export-" + datetime.datetime.fromtimestamp(os.path.getmtime("export.csv")).strftime('%Y-%m-%d-%H-%M-%S') + ".csv")
            else:
                self.append = True

        if (self.append):
            self.file = open("export.csv", "ab")
            self.writer = Writer(self.file)
        else:
            self.file = open("export.csv", "wb")
            self.writer = Writer(self.file)
            self.writer.writerow(["ID", "Timestamp", "Name", "Values"])

    def timeStamp(self, format='log'):
        '''
        Generates a timestamp string and returns it.
        
        **Parameters**: \n
        * **format='log'** - Specified formatting for the time on the log file.
        
        **Returns**: \n
        * **st** - Timestamp string.
        '''
        ts = time.time()

        if (format == 'file'):
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
        else:
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S:%f')

        return st

    def logData(self, name, *value):
        '''
        Writes a line of data to a CSV file.
        
        **Parameters**: \n
        * **name** - Specified names for data that is logged. 
        * ***value** - List of data from the sub.
        
        **Returns**: \n
        * **No Return.** \n
        '''
        self.ID += 1
        values = list(value)
        values.insert(0, self.ID)
        values.insert(1, self.timeStamp())
        values.insert(2, name)
        self.writer.writerow(values)

    def changeFile(self):
        '''
        Allows ability to change output CSV file for data logging.
        
        **Parameters**: \n
        * **No Input Parameters.**
        
        **Returns**: \n
        * **No Return.**\n
        '''
        self.ID = 0

        self.file.close()

        if (os.path.exists("export.csv")):
            os.rename("export.csv", "export-" + self.timeStamp(format = 'file') + ".csv")

        self.file = open("export.csv", "wb")
        self.writer = Writer(self.file)

if (__name__ == '__main__'):
    logger = DataLog()
    logger.logData('test', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19)
    logger.logData('depth', 4)
    logger.logData('speed', 100, 200)
    logger.logData('depth', 5)
    logger.logData('depth', 6)
    logger.logData('speed', 50, 600, 50)
    logger.logData('depth', 7.776, 9.002, 5, 4.68)
    logger.logData('test', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)
    logger.logData('test2', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 150, 16, 17, 18, 19)
    logger.logData('test', 1, 2, 3, 4, 5, 6, 7, 888, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19)
    logger.logData('test2', 1, 2, 3, 4, 555, 6, 7, 8, 9, 12, 11, 12, 13, 14, 15, 16, 17, 180, 19)