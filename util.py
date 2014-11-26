import numpy as np
import Queue
import deque

#create a random ID... if we collide 1 in a billion times, that won't hurt anybody... Since nodes don't keep track of anyone past their inputs and outputs, we should be able to avoid system time seed race condition here somehow...
def createID():
  return np.random.randint(0,2**32)

def logistic(a,b,x):
  return 1.0/(1+a*np.exp(-b*x))

#this is just so that I can see the shape of a random variable function:
def plotRV(points):
  plt.hist(points, bins = int(len(points)**(0.5)))
  plt.show()




