from nn import node
from nn import util
from nn import channel
import threading
import time
import numpy as np

weights = iter(lambda: 1, "anything but 1")

print node

def feedForward(inputSignals, inputChannels, outputChannels):
	for i in range(len(inputChannels)):
		inputChannels[i].putSignal(inputSignals[i])

	time.sleep(0.1)

	actuals = np.zeros(len(outputChannels))
	for i in range(len(outputChannels)):
		signal = outputChannels[i].getSignal()
		while signal:
			actuals[i] += signal.value
			signal = outputChannels[i].getSignal()


	return actuals

def propogateBackward(outputSignals, outputChannels):
	for i in range(len(outputChannels)):
		outputChannels[i].putFeedback(outputSignals[i])

def makeSigmoidNode():
	return node.Node(signalFilter = util.sigmoid, dsignalFilter = util.dsigmoid)

def localXOR():

	inputNodes = [makeSigmoidNode(), makeSigmoidNode()]
	hiddenNodes = [makeSigmoidNode(), makeSigmoidNode()]
	outputNode = makeSigmoidNode()

	#input channels
	inputChannels = []
	for inputNode in inputNodes:
		chan = channel.Channel()
		inputNode.establishInConnection(chan, next(weights))
		inputChannels.append(chan)

	#channels from input nodes to hidden nodes
	for inputNode in inputNodes:
		for hiddenNode in hiddenNodes:
			chan = channel.Channel()
			inputNode.establishOutConnection(chan)
			hiddenNode.establishInConnection(chan, next(weights))

	#channels from hidden nodes to output node
	for hiddenNode in hiddenNodes:
		chan = channel.Channel()
		hiddenNode.establishOutConnection(chan)
		outputNode.establishInConnection(chan, next(weights))

	#output channel
	outputChannel = channel.Channel()
	outputNode.establishOutConnection(outputChannel)



	#start the nodes a runnin'
	for node in inputNodes:
		threading.Thread(target=node.run)
	for node in hiddenNodes:
		threading.Thread(target=node.run)
	threading.Thread(target=outputNode.run)


	trainingCases = {(0,0):np.array([0]),
									 (0,1):np.array([1]),
									 (1,0):np.array([1]),
									 (1,1):np.array([0])}

	for case in trainingCases:
		actuals = feedForward(case, inputChannels, [outputChannel])
		dErrordOutput = actuals - trainingCases[case]
		propogateBackward(dErrordOutput, [outputChannel])


	for case in trainingCases:
		print feedForward(case, inputChannels, [outputChannel])



localXOR()






