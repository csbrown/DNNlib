import sys
sys.path.append("../nn")
import node
import util
import channel
import threading
import signaling
import time
import numpy as np
import Queue
import random


weights = iter(lambda: random.random(), "something lambda will never return")

expected = {}

def feedPingsToInputChannel(chan):
	while True:
		chan.putUpPing()
		time.sleep(0.1)

def feedPingsToOutputChannel(chan):
	while True:
		chan.putDownPing()
		time.sleep(0.1)

def startSimpleNode():
	nodeA = node.Node(bias = next(weights))
	inChannel = channel.Channel()
	outChannel = channel.Channel()

	nodeA.establishInConnection(inChannel, -next(weights))
	nodeA.establishOutConnection(outChannel)

	n = threading.Thread(target=nodeA.run)
	i = threading.Thread(target=feedPingsToInputChannel, args = (inChannel,))
	o = threading.Thread(target=feedPingsToOutputChannel, args = (outChannel,))

	n.daemon=True
	i.daemon=True
	o.daemon=True

	n.start()
	i.start()
	o.start()

	return nodeA,inChannel,outChannel,n,i,o

def localNOT():
	global expected
	nodeA,inChannel,outChannel,n,i,o = startSimpleNode()



	fb = threading.Thread(target=simpleNodeOutputFeedbacker, args=(outChannel,))
	fb.daemon=True
	fb.start()



	while True:
		zero = signaling.Signal(util.createID(),0)
		expected[zero.ID] = 1

		one = signaling.Signal(util.createID(),1)
		expected[one.ID] = 0

		inChannel.putSignals([zero,one])

		print "inChannelStats:  ", inChannel.upPing, inChannel.downPing, inChannel.signalQ.qsize(), inChannel.feedbackQ.qsize()
		print "outchannelStats: ", outChannel.upPing, outChannel.downPing, outChannel.signalQ.qsize(), outChannel.feedbackQ.qsize()
		print "nodeStats:       ", nodeA.upInputs, nodeA.upOutputs, nodeA.inputs[inChannel]


def simpleNodeOutputFeedbacker(outChannel):
	while True:
		outSignals = outChannel.getSignals()
		for signal in outSignals:
			if signal.ID in expected:
				outChannel.putFeedbacks([signaling.Signal(signal.ID,-(expected[signal.ID] - signal.value))])


localNOT()

