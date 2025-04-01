from multiprocessing.managers import BaseManager
import sys, os
import time

def read(filename):
    with open(filename) as file:
        lines = [line.rstrip() for line in file]
    return lines

class QueueManager(BaseManager):
    pass


def main(ip, port, nWorkers, mode, infinityMode):
    QueueManager.register('in_queue')
    QueueManager.register('out_queue')

    manager = QueueManager(address=(ip, int(port)), authkey=b'abc')
    manager.connect()

    in_queue = manager.in_queue()
    out_queue = manager.out_queue()

    # wczytanie pliku
    lines = read("test.txt")
         
    # podzielenie pracy na workerow
    nWorkers = int(nWorkers)
    nLines = len(lines)
    linesPerWorker = int(nLines / nWorkers)
    rest = nLines % nWorkers
    result = 0
    packages = []

    start = time.time()
    indices = [0] * (nWorkers+1)
    indices 
    for i in range(1, nWorkers):
        indices[i] = indices[i-1] + linesPerWorker
        if rest > 0:
            indices[i] += 1
            rest -= 1

    for i in range(nWorkers):
        startIndex = indices[i]
        endIndex = indices[i+1]
        chunkOfLines = lines[startIndex:endIndex]
        package = (chunkOfLines)
        packages.append(chunkOfLines)
    
    startKolejka = time.time()
    # wyslanie do kolejki
    for i in range(nWorkers):
        in_queue.put(packages[i])
    print("Czas trwania dodawania do kolejki: ", (time.time() - startKolejka))
    
    for i in range(nWorkers):
        partialResult = out_queue.get()
        result += partialResult


    end = time.time()
    print("Czas wykonywania dla klienta: ", (end-start))
        
    print(result)



if __name__ == '__main__':

    main(*sys.argv[1:])
