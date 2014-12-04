from collections import deque

#TODO: Better way to do this??
#Feedback will just be a signal in the opposite direction
class Signal(object):
  def __init__(self, ID, bias = 0.0):
    self.value = bias
    self.ID = ID

  def __hash__(self):
    return self.ID




#This shit is kinda jank.  I'm storing the signals like 3 times


class SignalLog(object):
  MAXSIZE = 100

  def __init__(self):
    #####################
    #TODO: put in something so that signals relate to an ultimate input and ultimate output, like {ultimateInputID:(Channel, signal)} or something
    #{signalID : {Channel : inSignalValue}  So that we can do updates and feedback 
    self.inSignalLog = {}
    #{signalID : outValue}  So that we can do feedback
    self.outSignalLog = {}
    #deque(signalID)   So that we don't spend forever waiting on feedback
    self.signalDeque = deque()
    #Plan:
    #continously look for signals in
    #when encounter new signal:
    #  continue to look for more signals with the same ID
    #  once we have a signal from all active inputs, broadcast
    #
    #To determine if an input is active:
    #  nodes continuously broadcast an "up" signal.  It only needs to go downstream.
    #  if all of a nodes inputs are down, shut the node down
    #  the bias channel does not need to provide an "up" signal, since it cannot go down.
    #  We can use the same mechanics as the signals for pings!  Just have the top level nodes generate them.
    #####################


  def logIn(self, channel, signal):
    if signal.ID not in inSignalLog:
      self.inSignalLog[signal.ID] = {}
    self.inSignalLog[signal.ID][channel] = signal.value

  def logOut(self, signal):

    self.signalDeque.append(signal.ID)

    self.outSignalLog[signal.ID] = signal.value

    if len(signalDeque) > MAXSIZE:
      deleteSignalID = signalDeque.popleft()
      del self.inSignalLog[deleteSignalID]
      del self.outSignalLog[deleteSignalID]

      
