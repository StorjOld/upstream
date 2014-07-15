#!/usr/bin/python
'''
Created on 2014-07-03
'''

import sys
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from Chunk import Chunk
from Streamer import Streamer

file_list = []

# Extend FileSystemEventHandler to be able to write custom on_any_event method
class MyHandler(FileSystemEventHandler):
    # Overwrite the methods for creation, deletion, modification, and moving
    # to get more information as to what is happening on output
    def on_created(self, event):
        print ("created: " + event.src_path)

        print ("uploading: " + event.src_path)
        stream = Streamer("http://node1.storj.io", 1)
        uploaded = stream.upload(event.src_path)
        
        chunk_list = uploaded[0]
        shredder_data = uploaded[1]

        f = open('info.txt', 'a')
        f.write(shredder_data.filename + "\n")
        for chunk in chunk_list:
            f.write("\t"+chunk.get_uri())
        f.close()
       
        
        print ("uploaded: " + event.src_path)
        
    #def on_deleted(self, event):
    #    print ("deleted: " + event.src_path)
        
    #def on_modified(self, event):
    #    print ("modified: " + event.src_path)
        
    #def on_moved(self, event):
    #    print ("moved/renamed: " + event.src_path + " destination: " + event.dest_path)

# Get watch_directory parameter
watch_directory = sys.argv[1]

event_handler = MyHandler()

observer = Observer()
observer.schedule(event_handler, watch_directory, True)
observer.start()

'''
Keep the script running or else python closes without stopping the observer
thread and this causes an error.
'''
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()