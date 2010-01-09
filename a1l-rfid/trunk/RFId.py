from signal import alarm

def handler(signum, frame):
    raise IOError("Read timed out")

class RFId:
    def __init__(port):
        self.port = port

    def getTag(self):
        tag = None
        signal(signal.SIGALRM, handler)
        alarm(30)
        with open(self.port) as f:
            tag = f.readline()
        alarm(0)
        return tag
        
