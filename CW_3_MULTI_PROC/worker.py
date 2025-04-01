from multiprocessing.managers import BaseManager
from multiprocessing import Queue, Process
import sys
import time


def countWords(lines):
    count = 0
    for line in lines:
        count += len(line.split())
    return count

class QueueManager(BaseManager):
    pass


def main(ip, port):
    QueueManager.register('in_queue')
    QueueManager.register('out_queue')

    manager = QueueManager(address=(ip, int(port)), authkey=b'abc')
    manager.connect()

    in_queue = manager.in_queue()
    out_queue = manager.out_queue()


    lines = in_queue.get()
    #start = time.time()
    wordsCount = countWords(lines)
    out_queue.put(wordsCount)
    #end = time.time()
    #print("Czas wykonywania dla workera: ", (end-start))

if __name__ == '__main__':
    main(*sys.argv[1:])
