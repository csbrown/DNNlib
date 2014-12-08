import threading
import Queue
from util import createID
import time
from signaling import Signal
import copy

#this is so that we can broadcast signals in parallel over a network, or however we want.  We define a Channel-like object to implement a send and receive method with the following signatures.  This way, we can bridge two nodes with a channel if we like.  An input node and the send method get from the q, output nodes and receive method will put to the q.

#Example config: Node1 -> Channel -> Node2  (Node1 puts directly to the signalQ, Node2 gets directly from the signalQ, Node2 puts directly to the feedbackQ, Node1 gets directly from the feedbackQ)
#Example config: Node1 -> Channel1 -> Socket -> Channel2 -> Node2 (Node1 puts directly to Channel1 signalQ, Channel1 send method is constantly running and writing signalQ items to a socket, Channel2 receive method is constantly running and reading signalQ items from a socket, Node2 gets directly from Channel2 signalQ.  feedbackQ operates in the other direction
class Channel(object):
  def __init__(self):
    self.DEADTIME = 5 #if we don't hear from a node for self.DEADTIME seconds, assume that it is dead

    #this is just so that we can hash Channels into a dictionary
    self.ID = createID()
    #this should hold incoming signal objects
    self.signalQ = Queue.Queue()
    #this should hold backpropogating feedback objects
    self.feedbackQ = Queue.Queue()
    #this should hold the latest upstream ping
    self.upPing = time.time()
    #this should hold the latest downstream ping
    self.downPing = time.time()

  def _safeGetAll(self, q):
    try:
      signals = []
      while not q.empty():
        signals.append(q.get(False))
        q.task_done()
      return signals
    except Queue.Empty:
      raise Exception("Too many people getting from q: " + str(q))

  def _safePutAll(self, q, signals):
    #make copies of the signals we send in here, since putting them in the Queue will lock them!
    copySignals = copy.deepcopy(signals)
    try:
      while not q.full() and copySignals:
        q.put(copySignals.pop(), False)
    except Queue.Full:
      raise Exception("Too many people putting to q: " + str(q))

  def getSignals(self):
    return self._safeGetAll(self.signalQ)
  def putSignals(self, signals):
    self._safePutAll(self.signalQ, signals)

  def getFeedbacks(self):
    return self._safeGetAll(self.feedbackQ)
  def putFeedbacks(self, signals):
    self._safePutAll(self.feedbackQ, signals)

  #This method says whether the channel is getting a signal from above
  def _getPing(self, currentPing):
    if time.time() - currentPing > self.DEADTIME:
      return False
    return True

  def getUpPing(self): return self._getPing(self.upPing)
  def getDownPing(self): return self._getPing(self.downPing)
  def putUpPing(self): self.upPing = time.time()
  def putDownPing(self): self.downPing = time.time()

  #######
  #These methods are so that a channel can communicate asynchronously over a network or however 
  #######
  def run(self):
    while True:
      self.send()
      self.receive()
      self.ping()

  def receive(self):
    pass

  def send(self):
    pass

  def ping(self):
    pass

  def __hash__(self):
    return self.ID




  
#This class provides a dummy channel for the bias, so that it's weight can be dealt with just like anyone else.
class BiasChannel(object):   
  def __init__(self):
    self.ID = createID()
  def getSignals(self): return [] #return no signals.  We don't know what the signal IDs are gonna be ahead of time
  def putFeedbacks(self, signal): pass #empty function
  def getUpPing(self): return False #Because we don't want this to factor in when we see which channels are up.
  def putUpPing(self): pass #empty function 
  def getFeedbacks(self): self._freakOut()
  def putSignals(self, signal): self._freakOut()
  def putDownPing(self): self._freakOut()
  def getDownPing(self): self._freakOut()
  def _freakOut(self): raise Exception("You can't have a BiasChannel downstream from you!")




