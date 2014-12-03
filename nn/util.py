import numpy as np

#create a random ID... if we collide 1 in a billion times, that won't hurt anybody... Since nodes don't keep track of anyone past their inputs and outputs, we should be able to avoid system time seed race condition here somehow...
def createID():
  return np.random.randint(0,2**32)

def logistic(a,b,x):
  return 1.0/(1+a*np.exp(-b*x))

def sigmoid(x):
	return np.tanh(x)
#in terms of the output of the sigmoid function above
def dsigmoid(y):
	return 1-y**2







