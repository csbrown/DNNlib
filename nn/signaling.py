

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
  MAXSIZE = 10

  def __init__(self):
    #TODO: The only thing we need from the inSignals is the ID... Fix that.
    #[(Channel, inSignal)]
    self.currentLog = []
    #We want our log to be FIFO [outSignal]
    self.signalDeque = deque()
    #We need to look up signals by ID { signalID : outSignal }
    self.outSignalLookup = {}
    #We need to look up in signals by outsignal #{ outSignalID : [(Channel, inSignal)] }
    self.inSignalLookup = {}

  def logIn(self, channel, signal):
    self.currentLog.append((channel, signal.ID))

  def logOut(self, signal):
    self[signal] = self.currentLog
    self.currentLog = []

    self.signalDeque.append(signal)

    self.signalLookup[signal.ID] = signal

    if len(signalDeque) > MAXSIZE:
      deleteSignal = signalDeque.popleft()
      del self[deleteSignal]
      del self.signalLookup[deleteSignal.ID]

      
