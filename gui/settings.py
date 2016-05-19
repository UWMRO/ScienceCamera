
#from photoAcquisitionGUI import CallbackEvaluator
from Queue import Queue
import signal
from uuid import uuid4
import threading


class CallbackEvaluator():
    def __init__(self):
        print "made CallbackEvaluator"
        self.active_threads = {}

    def put(self, d, results):
        # get id
        tid = str(uuid4())
        print tid

        # start new thread on target callback
        t = threading.Thread(target=self.startCallback, args=(d, results), name=tid)
        #t.daemon = True
        self.active_threads[tid] = t
        t.start()

    def startCallback(self, d, results):
        print "starting callback"
        d.callback(results)

    def stopThread(self, IDqueue):
        currentID = IDqueue.get()
        print "stopping thread"
        print currentID
        t = self.active_threads.pop(currentID)
        t.join()



def handler(signum, frame):
    print "Signal handler called with signal", signum
    callback_evaluator.stopThread(done_ids)

def init():
    global callback_evaluator, done_ids
    callback_evaluator = CallbackEvaluator()
    done_ids = Queue()
    signal.signal(signal.SIGALRM, handler)
