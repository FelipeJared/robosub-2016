'''
Copyright 2014, Austin Owens, All rights reserved.

Created on Oct 13, 2014

@author: Austin Owens

In order to run this program, you need to have two cameras accessible by your computer (e.g. A laptop webcam and an external webcam).
'''

import multiprocessing
import cv2

class ImageProcessing:
    
    def imageCreation(self, imagingDeviceNum, *args):
        
        cap1 = cv2.VideoCapture(imagingDeviceNum)
        
        while True:
            
            ret1, rawImg = cap1.read()
            cv2.imshow('rawImg', rawImg)
            
            grayImg = cv2.cvtColor(rawImg, cv2.COLOR_BGR2GRAY)
            cv2.imshow('grayImg', grayImg)

            ch = cv2.waitKey(1)
            if ch == 27:
                if len(args) > 0:
                    if args[0] == "queue":
                        args[1].put([20.278942387, 10.392749, 5.334])        
                    elif args[0] == "pipe":
                        args[1].send(grayImg)
                        args[1].close()
                break
    
        cv2.destroyAllWindows()

ip = ImageProcessing() 

def processesRunningAtSameTimeWithNoSharing():
    '''
    Allows image processing to execute on another process without any sharing between the processes
    '''
    
    p = multiprocessing.Process(target=ip.imageCreation, args=(0,))
    p.start()
   
def queueExample():
    '''
    There are two types of communication channels between processes: Queues and Pipes. Queues are good for communications
    between multiple processes. Any process can put data into the queue or get data from the queue. Pipes have only two 
    end points but have a much better performance speed than queues.
    
    queue.get() retrieves the data after put() is called from an external process. queue.get() uses the join() function so
    nothing under queue.get() will be executed until the external process calls put().
    '''
    
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=ip.imageCreation, args=(0,"queue",queue, ))
    process.start()

    print queue.get()
    
    
    
def pipeExample():
    '''
    There are two types of communication channels between processes: Queues and Pipes. Queues are good for communications
    between multiple processes. Any process can put data into the queue or get data from the queue. Pipes have only two 
    end points but have a much better performance speed than queues.
    
    parent_conn.recv() retrieves the data after close() is called from an external process. parent_conn.recv() uses the join() function so
    nothing under queue.get() will be executed until the external process calls close().
    '''
    
    parent_conn, child_conn = multiprocessing.Pipe()
    p = multiprocessing.Process(target=ip.imageCreation, args=(0,"pipe",child_conn,))
    p.start()
    
    cv2.imshow("last img taken by external process.", parent_conn.recv())

if __name__ == '__main__':
    '''
    Out of:
    
    processesRunningAtSameTimeWithNoSharing()
    queueExample()
    pipeExample()
    
    only uncomment one at a time. Keep the ip.imageCreation(1) function uncommented.
    '''
    
    #processesRunningAtSameTimeWithNoSharing()
    #queueExample()
    pipeExample()
    
    ip.imageCreation(1) #Keep this line uncommented
    
    