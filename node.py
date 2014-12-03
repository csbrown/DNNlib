import matplotlib.pyplot as plt
import numpy as np
import Queue
import threading
from util import *
from signaling import *
from chanel import *




#I'm wondering how we can learn time-to-fire... if the outgoing signal is zero because we fire too often, the update will be large... if the outgoing signal is one because we fire too sparsely, the update will be large.  If we fire just right, the update will be the smallest possible...

#Let's just fire after checking the signalQ for ALL of the incoming nodes!  We'll just assume that we got input from all of the incoming nodes.




#this is a generic linear node class.  If you want to use a different function, override the signalFilter and dsignalFilter methods
class Node(object):
  DEFAULT_WEIGHT = 1

  #If we get no feedback, we can take that as either a good thing or a bad thing
  FEEDBACKBIAS = 0

  #takes in a function to pass the linear signal through, and the derivative of that function in terms of the function... e.g. dy/dx = y
  #epsilon is a generator for the learning epsilon.  another option is sigmoid, signalFilter = tanh(z), dsignalfilter = 1-y**2
  def __init__(self, **kwargs): 
    def defaulter(key, defaultValue):
      if key in kwargs:
        return kwargs[key]
      return defaultValue

    self.signalLog = SignalLog()

    #OVERRIDABLES
    self.inputs = defaulter("inputs", {BiasChannel():1}) #the input channels: defaults to a single BiasChannel with a weight of 1
    self.outputs = defaulter("outputs", set()) #the output channels: defaults to empty set
    self.signalFilter = defaulter("signalFilter", lambda z : z) #the function we pass a linear combo of inputs through: defaults to identity
    self.dsignalFilter = defaulter("dsignalFilter", lambda y : 1) #the derivative of signalFilter
    self.epsilon = defaulter("epsilon", iter(lambda : 0.01, 0)) #the learning rate generator: defaults to an endless sequence of 0.01

  def run(self):
    while True:
      signal = self.recieveSignals()
      self.sendSignals(signal)

      #dEdys because there may be feedback for multiple different outputs.  { OutputID : FeedbackValue }
      dErrordOutputs = self.recieveFeedbacks() 
      self.sendFeedbacksAndUpdate(dErrordOutputs)

  #retrieve inputs from in channels
  def recieveSignals(self):
    totalSignal = SIGNALBIAS
    for channel in self.inputs:
      signal = channel.getSignal()
      if signal:
        self.signalLog.inLog(channel, signal)
        totalSignal += signal.value * self.inputs[channel]

    return totalSignal

  #send signals to out channels
  def sendSignals(self, inSignal):
    outSignal = self.signalFilter(inSignal)
    for channel in self.outputs:
      channel.putSignal(outSignal)

    self.signalLog.outLog(outSignal)  
    self.inSignal = SIGNALBIAS

  #get feedback from channels.  We have to separate the feedback by ID, because in order to use the feedback we need to know what our output was
  def recieveFeedbacks(self):
    feedbacks = {}
    for channel in self.outputs:
      signal = channel.getFeedback()
      if signal:
        if signal.ID not in feedbacks:
          feedbacks[signal.ID] = 0
        feedbacks[signal.ID] += signal.value

    return feedbacks

  #send feedback to in channels. We send feedback as w_ij * dE/dOutput * dsignalFilter(Output)
  def sendFeedbacksAndUpdate(self, dErrordOutputs):
    #for each of THIS nodes outputs that we got feedback for, look up the channels 
    for outSignalID in dErrordOutputs:
      outSignal = self.signalLog.outSignalLookup[outSignalID]
      inSignals = self.signalLog.inSignalLookup[outSignalID]
      for inChannel, inSignal in inSignals:
        dErrordInput = self.propogateErrorByInputValue(inChannel, outSignal, dErrordOutputs[outSignal.ID])
        inChannel.putFeedback(Signal(inSignal.ID, dErrordInput))

        dErrordWeight = self.propogateErrorByInputWeight(inSignal, outSignal, dErrordOutputs[outSignal.ID])
        self.update(inChannel, dErrordWeight)

  #dE/dy_i = SUM_k ( w_ik * dFilter(y_k) * dE/dy_k ) .... We just update one k at a time, so no sum
  def propogateErrorByInputValue(self, inChannel, outSignal, dErrordOutput):
    #TODO: not entirely sure about some of the math here... Which outputs and inputs and whatever do we put where?
    return self.inputs[inChannel] * self.dsignalFilter(outSignal.value) * dErrordOutput

  def propogateErrorByInputWeight(self, inSignal, outSignal, dErrordOutput):
    return self.dsignalFilter(outSignal.value) * dErrordOutput * inSignal.value

  #updates the weights DELTAw_ri = epsilon * SUM_k ( w_ik * dFilter(y_k) * dE/dy_k *dy_i/dz * dz/dw_ri ) .... We just update one k at a time, so no sum
  #TODO: Maybe we should do this at the same time as sending feedback?
  def update(self, inChannel, inSignal, dErrordInput):
    DELTAw = next(self.epsilon) * dErrordWeight
    self.inputs[inChannel] += DELTAw

  def giveConnection(self, channel):
    self.inputs[channel] = DEFAULT_WEIGHT
    return self

  def getConnection(self, channel):
    self.outputs.add(channel)
    
  def closeOutbound(self, node):
    self.outputs.remove(node)
    node.closeInbound(self)

  def closeInbound(self, node):
    del self.inputs[node]
    node.closeOutbound(self)

    
