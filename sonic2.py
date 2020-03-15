#Action space: MultiBinary(12)
#Observation space: Box(224, 320, 3)
#Observation high: 255, low: 0

import retro
env = retro.make(game='SonicTheHedgehog2-Genesis')

import math
import array
import sys
import time
import hashlib

from ctypes import *
so_file = "/usr/local/lib/libT-Rex.so"
tRex = CDLL(so_file)

#OBSERVATION DATA
SCREEN_ROWS = 224
SCREEN_COLUMNS = 320
COLOR_CHANNELS = 3
BITS_PER_OBSERVATION = 128 #Md5 has a digest size of 128 bits

#ACTION DATA
BITS_PER_ACTION = 12

#NEURAL NETWORK DATA
NEURAL_NETWORK_NUMBER_OF_INPUTS = BITS_PER_OBSERVATION
NEURAL_NETWORK_NUMBER_OF_HIDDEN_LAYERS = 50
NEURAL_NETWORK_NUMBER_OF_OUTPUTS = BITS_PER_ACTION

#Number of consecutive victories to consider the training completed
MAX_CONSECUTIVE_VICTORIES = ((NEURAL_NETWORK_NUMBER_OF_INPUTS ** 2) * NEURAL_NETWORK_NUMBER_OF_HIDDEN_LAYERS + (NEURAL_NETWORK_NUMBER_OF_OUTPUTS * NEURAL_NETWORK_NUMBER_OF_INPUTS))

NEURAL_NETWORK_FILE_LOAD_ERROR = -10
NEURAL_NETWORK_ERROR_CODE = -12

NEURAL_NETWORK_FILE_PATH = create_string_buffer(str.encode("neural_network.json"))

action = env.action_space.sample() 

def computeNeuralNetworkInput(myObservation, myNeuralNetwork):
	
	myBitArray = array.array('i',(0 for i in range(0, NEURAL_NETWORK_NUMBER_OF_INPUTS)))

	myMd5 = hashlib.md5()

	returnValue = 0
	myBitArrayIndex = 0;
	neuralNetworkInputIndex = 0
	
	for row in range(SCREEN_ROWS):
		for column in range(SCREEN_COLUMNS):
			for channel in range(COLOR_CHANNELS):

				myMd5.update(myObservation[row][column][channel])

	print("Pixel digest:", myMd5.hexdigest())

	digest = myMd5.digest()

	for byte in range(myMd5.digest_size):
		for i in reversed(range(7)):

			bit = digest[byte] >> i

			if (bit & 1):
				myBitArray[myBitArrayIndex] = 1
			else:
				myBitArray[myBitArrayIndex] = 0

			myBitArrayIndex += 1

	while neuralNetworkInputIndex < NEURAL_NETWORK_NUMBER_OF_INPUTS and returnValue==0:
	
		returnValue = tRex.setNeuralNetworkInput(myNeuralNetwork, neuralNetworkInputIndex, myBitArray[neuralNetworkInputIndex])

		neuralNetworkInputIndex += 1

	return returnValue
	
def parseNeuralNetworkOutput(neuralNetworkOutput, numberOfOutputs):
	
	neuralNetworkOutputIndex = 0
	
	while neuralNetworkOutputIndex < numberOfOutputs:

		if (neuralNetworkOutput[neuralNetworkOutputIndex]==1):
			action[neuralNetworkOutputIndex] = 1
		else:
			action[neuralNetworkOutputIndex] = 0

		neuralNetworkOutputIndex += 1
	
	return action			

#Main logic
neuralNetworkFileFound = False

bestNeuralNetwork = c_void_p()
neuralNetworkClone = c_void_p()
auxNeuralNetwork = c_void_p()

#Check if a trained neural network already exists
returnValue = tRex.loadNeuralNetwork(NEURAL_NETWORK_FILE_PATH, byref(bestNeuralNetwork))

if returnValue==0:
	neuralNetworkFileFound = True
	print("Neural network file found")
elif returnValue==NEURAL_NETWORK_FILE_LOAD_ERROR:
	returnValue = tRex.createNeuralNetwork(byref(bestNeuralNetwork), NEURAL_NETWORK_NUMBER_OF_INPUTS, NEURAL_NETWORK_NUMBER_OF_HIDDEN_LAYERS, NEURAL_NETWORK_NUMBER_OF_OUTPUTS)

if returnValue==0:
	returnValue = tRex.createNeuralNetwork(byref(neuralNetworkClone), NEURAL_NETWORK_NUMBER_OF_INPUTS, NEURAL_NETWORK_NUMBER_OF_HIDDEN_LAYERS, NEURAL_NETWORK_NUMBER_OF_OUTPUTS)

consecutiveVictories = 0
bestReward = 0
episode = 0

while consecutiveVictories < MAX_CONSECUTIVE_VICTORIES and returnValue==0 and not neuralNetworkFileFound:
	
	observation = env.reset()

	reward = 0;
	episode += 1

	while returnValue==0:
		c_int_p = POINTER(c_int)
		myOutputArray = c_int_p()
		myOutputArraySize = c_int()
			
		#print(observation)

		returnValue = computeNeuralNetworkInput(observation, neuralNetworkClone)

		if returnValue==0:
			returnValue = tRex.computeNeuralNetworkOutput(neuralNetworkClone, byref(myOutputArray), byref(myOutputArraySize))

		if returnValue==0 and myOutputArraySize.value!=NEURAL_NETWORK_NUMBER_OF_OUTPUTS:
			returnValue = NEURAL_NETWORK_ERROR_CODE

		if returnValue==0:
			action = parseNeuralNetworkOutput(myOutputArray, myOutputArraySize.value)
			observation, newReward, done, info = env.step(action)
#			env.render()

			reward += newReward

			print("Reward:", reward)
			print("Best reward:", bestReward)
			print("Action:", action)
			print("Episode:", episode)

			if done:

				if reward > bestReward:
				
					auxNeuralNetwork = bestNeuralNetwork
					bestNeuralNetwork = neuralNetworkClone
					neuralNetworkClone = auxNeuralNetwork

					consecutiveVictories = 0
					bestReward = reward
				else:
					consecutiveVictories += 1

				returnValue = tRex.cloneNeuralNetwork(bestNeuralNetwork, neuralNetworkClone)

				if returnValue==0:
					returnValue = tRex.mutateNeuralNetwork(neuralNetworkClone)
			
				print("Episode finished")
				break

			print("Consecutive victories:", consecutiveVictories, "/", MAX_CONSECUTIVE_VICTORIES)	

#Destroy the neural network clone
if returnValue==0:
	returnValue = tRex.destroyNeuralNetwork(byref(neuralNetworkClone))

#Save the best neural network
if returnValue==0 and not neuralNetworkFileFound:
	returnValue = tRex.saveNeuralNetwork(NEURAL_NETWORK_FILE_PATH, bestNeuralNetwork)

observation = env.reset()
reward = 0;

print("----- FINAL GAME -----")

while returnValue==0:
	c_int_p = POINTER(c_int)
	myOutputArray = c_int_p()
	myOutputArraySize = c_int()
		
	#print(observation)

	returnValue = computeNeuralNetworkInput(observation, bestNeuralNetwork)

	if returnValue==0:
		returnValue = tRex.computeNeuralNetworkOutput(bestNeuralNetwork, byref(myOutputArray), byref(myOutputArraySize))

	if returnValue==0 and myOutputArraySize.value!=NEURAL_NETWORK_NUMBER_OF_OUTPUTS:
		returnValue = NEURAL_NETWORK_ERROR_CODE

	if returnValue==0:
		action = parseNeuralNetworkOutput(myOutputArray, myOutputArraySize.value)
		observation, newReward, done, info = env.step(action)
		env.render()

		reward += newReward

		print("Reward:", reward)
		print("Action:", action)

		if done:
			break

env.close()

#Destroy the best neural network
if returnValue==0:
	returnValue = tRex.destroyNeuralNetwork(byref(bestNeuralNetwork))

if returnValue!=0:
	print("ERROR", returnValue)


# This code can be used to get the observation space and action space of other games
"""
print(env.action_space)
#> Discrete(9)
print(env.observation_space)
#> Box(128,)
#print(env.action_space.high)
#> [1.]
#print(env.action_space.low)
#> [-1.]
print(env.observation_space.high)
#> 255
print(env.observation_space.low)
#> 0
sys.exit()
"""
