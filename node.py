import matplotlib.pyplot as plt
import numpy as np
import Queue
import threading
from util import *




#I'm wondering how we can learn time-to-fire... if the outgoing signal is zero because we fire too often, the update will be large... if the outgoing signal is one because we fire too sparsely, the update will be large.  If we fire just right, the update will be the smallest possible...

#Let's just fire after checking the signalQ for ALL of the incoming nodes!  We'll just assume that we got input from all of the incoming nodes.




#this is a generic linear node class.  If you want to use a different function, override the signalFilter and dsignalFilter methods
class Node(object):
  DEFAULT_WEIGHT = 1
  #We can have a node that's always firing to our node
  SIGNALBIAS = 0
  #If we get no feedback, we can take that as either a good thing or a bad thing
  FEEDBACKBIAS = 0

  #takes in a function to pass the linear signal through, and the derivative of that function in terms of the function... e.g. dy/dx = y
  #epsilon is a generator for the learning epsilon
  def __init__(self, signalFilter = lambda z : z, dsignalFilter = lambda y : 1, epsilon = iter(lambda : 0.01, 0)):
    #dictionary where a channel points to a weight
    self.inputs = {}
    self.outputs = set()

    self.signalLog = SignalLog()

    self.signalFilter = signalFilter
    self.dsignalFilter = dsignalFilter

  def run(self):
    while True:
      signal = self.recieveSignals()
      self.sendSignals(signal)

      #dEdys because there may be feedback for multiple different outputs.  { OutputID : FeedbackValue }
      dEdys = self.recieveFeedbacks() 
      self.sendFeedbacks(dEdys)

      self.update(dEdys)


  #retrieve inputs from in channels
  def recieveSignals(self):
    totalSignal = SIGNALBIAS
    for channel in self.inputs:
      try:
        if not channel.signalQ.isempty():
          signal = channel.signalQ.get(False)
          self.signalLog.inLog(channel, signal)
          totalSignal += signal.value * self.inputs[channel]
      except Queue.Empty:
        raise Exception("Too many people using channel!")

    return totalSignal

  #send signals to out channels
  def sendSignals(self, inSignal):
    outSignal = self.signalFilter(inSignal)
    for channel in self.outputs:
      try:
        if not channel.signalQ.isfull():
          channel.signalQ.put(outSignal, False)
      except Queue.Full:
        raise Exception("Too many people using channel!")

    self.signalLog.outLog(outSignal)
    
    self.inSignal = SIGNALBIAS

  #get feedback from channels.  We have to separate the feedback by ID, because in order to use the feedback we need to know what our output was
  def recieveFeedbacks(self):
    feedbacks = {}
    for channel in self.outputs:
      try:
        if not channel.feedbackQ.isempty():    
          signal = channel.feedbackQ.get(False)
          if signal.ID not in feedbacks:
            feedbacks[signal.ID] = 0
          feedbacks[signal.ID] += signal.value
      except Queue.Empty:
        raise Exception("Too many people using channel!")
    return feedbacks

  #send feedback to in channels. We send feedback as w_ij * dE/dOutput * dsignalFilter(Output)
  def sendFeedbacks(self, dEdys):
    #for each of THIS nodes outputs that we got feedback for, look up the channels 
    for signalID in dEdys:
      



  #takes the node offline, and updates the weights using the current list of target output and the corresponding actual output (where to store that??) NOTE: UPDATE BETWEEN FIRES!  NOTE: I think the best way to do this is to, once the ratio of feedback to number of fires reaches a certain threshhold, take the thing offline and update, throw away any future feedback that we get based on the previous weights somehow, rinse and repeat.
  def update(self, dEdys):
    raise NotImplementedError("your weight function needs to have an update method"

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

  def __hash__(self):
    
