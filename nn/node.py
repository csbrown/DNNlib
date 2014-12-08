import numpy as np
import Queue
from signaling import *
from channel import *




#I'm wondering how we can learn time-to-fire... if the outgoing signal is zero because we fire too often, the update will be large... if the outgoing signal is one because we fire too sparsely, the update will be large.  If we fire just right, the update will be the smallest possible...

#Let's just fire after checking the signalQ for ALL of the incoming nodes!  We'll just assume that we got input from all of the incoming nodes.




#this is a generic linear node class.  If you want to use a different function, override the signalFilter and dsignalFilter methods
class Node(object):

  #takes in a function to pass the linear signal through, and the derivative of that function in terms of the function... e.g. dy/dx = y
  #epsilon is a generator for the learning epsilon.  another option is sigmoid, signalFilter = tanh(z), dsignalfilter = 1-y**2
  def __init__(self, **kwargs): 
    def defaulter(key, defaultValue):
      if key in kwargs:
        return kwargs[key]
      return defaultValue

    self.signalLog = SignalLog()
    self._biasChannel = BiasChannel()

    #OVERRIDABLES
    self.bias = defaulter("bias", 1) #default the bias to 1
    self.inputs = defaulter("inputs", {self._biasChannel:self.bias}) #the input channels: defaults to a single BiasChannel with a weight of 1
    self.outputs = defaulter("outputs", set()) #the output channels: defaults to empty set
    self.signalFilter = defaulter("signalFilter", lambda z : z) #the function we pass a linear combo of inputs through: defaults to identity
    self.dsignalFilter = defaulter("dsignalFilter", lambda y : 1) #the derivative of signalFilter
    self.epsilon = defaulter("epsilon", iter(lambda : 0.01, 0)) #the learning rate generator: defaults to an endless sequence of 0.01

    #If we cannot contact our parents, don't bother doing anything.
    #Alert children that it's down, so that they don't keep waiting
    #Keep listening for downPings
    self.upInputs = set()

    #If we cannot contact our children, don't bother doing anything.
    #Alert parents that it's down, so they don't wait on feedback
    #Keep listening for upPings
    self.upOutputs = set()

  def run(self):
    while True:
      self.receiveInputPings()
      self.receiveOutputPings()
      if self.upInputs and self.upOutputs:
        self.receiveSignals()
        readySignals = self.readySignalsToSend()
        self.sendSignals(readySignals)

        #dEdys because there may be feedback for multiple different outputs.  { OutputID : FeedbackValue }
        dErrordOutputs = self.receiveFeedbacks() 
        self.sendFeedbacksAndUpdate(dErrordOutputs)

        self.sendPingsUp()
        self.sendPingsDown()


  def receiveInputPings(self):
    for channel in self.inputs:
      if channel.getUpPing():
        self.upInputs.add(channel)
      else:
        self.upInputs.discard(channel)
  def receiveOutputPings(self):
    for channel in self.outputs:
      if channel.getDownPing():
        self.upOutputs.add(channel)
      else:
        self.upOutputs.discard(channel)

  def sendPingsDown(self):
    if self.upInputs:
      for outChannel in self.upOutputs:
        outChannel.putUpPing()
  def sendPingsUp(self):
    if self.upOutputs:
      for inChannel in self.upInputs:
        inChannel.putDownPing()


  #retrieve inputs from in channels.  We separate the input signals according to the ultimate input
  def receiveSignals(self):
    for channel in self.inputs:
      signals = channel.getSignals()
      for signal in signals:
        self.signalLog.logIn(channel, signal)

  #This gets all of our ready signals and prepares them to be sent
  def readySignalsToSend(self):
    signalsToSend = []
    for signalID in self.signalLog.inSignalLog:
      if self.signalReady(signalID):
        signalsToSend.append(self.readySignalToSend(signalID))
    return signalsToSend

  #This takes in a signalID and accumulates everything into an out signal, all ready to send out
  def readySignalToSend(self,signalID):
    self.signalLog.inSignalLog[signalID][self._biasChannel] = 1  #add in the bias
    linearSignal = sum([self.inputs[chan]*val for chan, val in self.signalLog.inSignalLog[signalID].iteritems()])
    outSignalValue = self.signalFilter(linearSignal)
    return Signal(signalID, outSignalValue)


  #send prepared signals to out channels
  def sendSignals(self, signalsToSend):
    for channel in self.outputs:
      channel.putSignals(signalsToSend)
    for signal in signalsToSend:
      self.signalLog.logOut(signal)  

  #reports whether a signal is ready to send
  def signalReady(self, signalID):
    #There's gotta be a better way to do this::
    #if we've sent a signal out, don't send another.  If we've got signals in from all our channels, send one out.
    if signalID in self.signalLog.outSignalLog:
      return False
    for channel in self.upInputs:
      if channel not in self.signalLog.inSignalLog[signalID]:
        return False
    return True

  #get feedback from channels.  We have to separate the feedback by ID, because in order to use the feedback we need to know what our output was, and what input corresponded to it
  def receiveFeedbacks(self):
    feedbacks = {}
    for channel in self.outputs:
      signals = channel.getFeedbacks()
      for signal in signals:
        if signal.ID not in feedbacks:
          feedbacks[signal.ID] = 0
        feedbacks[signal.ID] += signal.value
    return feedbacks

  #send feedback to in channels. We send feedback as w_ij * dE/dOutput * dsignalFilter(Output)
  def sendFeedbacksAndUpdate(self, dErrordOutputs):
    #for each of THIS nodes outputs that we got feedback for, look up the channels 
    for signalID in dErrordOutputs:
      outSignalValue = self.signalLog.outSignalLog[signalID]
      inSignals = self.signalLog.inSignalLog[signalID]
      for inChannel, inSignalValue in inSignals.iteritems():
        dErrordInput = self.propogateErrorByInputValue(inChannel, outSignalValue, dErrordOutputs[signalID])
        inChannel.putFeedbacks([Signal(signalID, dErrordInput)])

        dErrordWeight = self.propogateErrorByInputWeight(inSignalValue, outSignalValue, dErrordOutputs[signalID])
        self.updateWeight(inChannel, dErrordWeight)

  #dE/dy_i = SUM_k ( w_ik * dFilter(y_k) * dE/dy_k ) .... We just update one k at a time, so no sum
  def propogateErrorByInputValue(self, inChannel, outSignalValue, dErrordOutput):
    #TODO: not entirely sure about some of the math here... Which outputs and inputs and whatever do we put where?
    return self.inputs[inChannel] * self.dsignalFilter(outSignalValue) * dErrordOutput

  def propogateErrorByInputWeight(self, inSignalValue, outSignalValue, dErrordOutput):
    return self.dsignalFilter(outSignalValue) * dErrordOutput * inSignalValue

  #updates the weights DELTAw_ri = epsilon * SUM_k ( w_ik * dFilter(y_k) * dE/dy_k *dy_i/dz * dz/dw_ri ) .... We just update one k at a time, so no sum
  #TODO: Maybe we should do this at the same time as sending feedback?
  def updateWeight(self, inChannel, dErrordWeight):
    DELTAw = next(self.epsilon) * dErrordWeight
    self.inputs[inChannel] += DELTAw

  def establishInConnection(self, channel, weight):
    self.inputs[channel] = weight

  def establishOutConnection(self, channel):
    self.outputs.add(channel)
    
  def closeOutbound(self, node):
    self.outputs.remove(node)
    node.closeInbound(self)

  def closeInbound(self, node):
    del self.inputs[node]
    node.closeOutbound(self)

    
