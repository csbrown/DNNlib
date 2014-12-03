import threading
import Queue
import util
import signaling

#this is so that we can broadcast signals in parallel over a network, or however we want.  We define a Channel-like object to implement a send and receive method with the following signatures.  This way, we can bridge two nodes with a channel if we like.  An input node and the send method get from the q, output nodes and receive method will put to the q.

#Example config: Node1 -> Channel -> Node2  (Node1 puts directly to the signalQ, Node2 gets directly from the signalQ, Node2 puts directly to the feedbackQ, Node1 gets directly from the feedbackQ)
#Example config: Node1 -> Channel1 -> Socket -> Channel2 -> Node2 (Node1 puts directly to Channel1 signalQ, Channel1 send method is constantly running and writing signalQ items to a socket, Channel2 receive method is constantly running and reading signalQ items from a socket, Node2 gets directly from Channel2 signalQ.  feedbackQ operates in the other direction
class Channel(object):
  def __init__(self):
    self.ID = createID()
    #this should hold incoming signal objects
    self.signalQ = Queue.Queue()
    #this should hold backpropogating feedback objects
    self.feedbackQ = Queue.Queue()

  def _safeGet(self, q):
    try:
      if not q.isempty():
        signal = q.get(False)
        return signal
    except Queue.Empty:
      raise Exception("Too many people getting from q: " + str(q))

  def _safePut(self, q, signal):
    try:
      if not q.isfull():
        q.put(signal, False)
    except Queue.Full:
      raise Exception("Too many people putting to q: " + str(q))

  def getSignal(self):
    return self._safeGet(self.signalQ)
  def putSignal(self, signal):
    self._safePut(self.signalQ, signal)

  def getFeedback(self):
    return self._safeGet(self.feedbackQ)
  def putFeedback(self, signal):
    self._safePut(self.feedbackQ, signal)


  def receive(self):
    pass

  def send(self):
    pass

  def __hash__(self):
    return self.ID




  
#This class provides an endless stream of ones, and just discards feedback
class BiasChannel(object):   
  def __init__(self):
    self.ID = createID()
  def getSignal(self): return 1
  def putFeedback(self, signal): pass #empty function
  def getFeedback(self): self.freakOut()
  def putSignal(self, signal): self.freakOut()
  def freakOut(self): raise Exception("You can't have a BiasChannel downstream from you!")




