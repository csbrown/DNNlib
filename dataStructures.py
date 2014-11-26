import matplotlib.pyplot as plt
import numpy as np
import Queue
import threading


    


#this is a logistic function node
class LogisticNode(Node):
  DEFAULT_WEIGHT = 1

  def __init__(self):
    Node.__init__(self)
    self.a,self.b = (1,1) 

  def computeSignal(self, *inputs):
    return logistic(a,b,sum(inputs)/len(inputs))

  def receive(self, signal, source):
    
    

  #       dE 
  # -ep  ----  ==   ep SUM(x_i_n actual_n (1 - actual_n) (target_n - actual_n)) 
  #      dw_i          n in training
  def update(self, target, actual, inputs):
    for 
    

  def giveConnection(self):
    newConnection = Channel(LogisticNode.DEFAULT_WEIGHT)
    newConnection.whereTo = self
    self.inputs.add(newConnection)
    return newConnection
    
    
    


    



 





