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

    self.receiver = None #threading.Thread(target = self.receive)
    self.sender = None #threading.Thread(target = self.send)
  def receive(self):
    pass

  def send(self):
    pass

  def __hash__(self):
    return self.ID




  
        




