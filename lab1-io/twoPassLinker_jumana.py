import logging
import sys

#SETTING UP LOGGING FOR DEBUGGING
#create logger and set its level to DEBUG
logger = logging.getLogger('linker')
logger.setLevel(logging.DEBUG)

#format of outputted log and further formatting of its date
FORMAT = "%(asctime)s : %(name)s : %(message)s"  #%(funcName)s
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(FORMAT,DATE_FORMAT)

#create a console handler and set its formatting and level
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)

#add the created handler to logger
logger.addHandler(ch)
#
# logger.debug("Printing".format())

inputFile = sys.stdin.readlines()
editedInput = []

#ADDING INPUT ITEMS IN AN ARRAY
for item in inputFile:
	item = item.split()
	for newItem in item:
		if newItem.isdigit():
			newItem = int(newItem)
		editedInput.append(newItem)

#DECLARING ALL GLOVAL VARIABLES
MODULE_NUM = editedInput[0]
MAX_SIZE = 200
variableDict = {} #Symbol table
symbolModule = {} #keeps track of which module each symbol was defined in
symbolAddress = {}
instructions = [] #list of all the instructions to resolve
numInsPerModule = []
useIndex = [] #where all the uses are declared
baseValueIncrement = [] #offset list
errorList = []

#first pass
def FirstPass(input):
	pointer = 1
	module = 0
	baseValueOffset = 0
	while module<MODULE_NUM:
		numVariables = input[pointer]
		# logger.debug("Pointer:{}, input: {}, numVariables: {}".format(pointer, input[pointer], numVariables))
		pointer +=1
		# logger.debug("Pointer: {}, Value: {}".format(pointer, input[pointer]))
		for index in range(0, numVariables*2, 2): #CREATING AND ADDING TO SYMBOL TABLE
			if input[pointer+index] in variableDict.keys():
				# logger.debug("Error for {}".format(input[pointer+index]))
				error = 1
				errorList.append(ErrorCheck(error, input[pointer+index]))
			else:
				variableDict[input[pointer+index]] = input[pointer+index+1]+baseValueOffset
				symbolModule[input[pointer+index]] = module
				symbolAddress[input[pointer+index]] = input[pointer+index+1]
				# logger.debug("Key: {}, Value: {}".format(input[pointer+index], input[pointer+index+1]))
		pointer = pointer+(numVariables*2)
		jumpUses= input[pointer] #jumping the values where the uses are defined
		useIndex.append(pointer)
		pointer = pointer+(jumpUses*2) + 1
		numInstructions = input[pointer] #KEEPING TRACK OF THE NUMBER OF INSTRUCTIONS PER MODULE
		numInsPerModule.append(numInstructions)
		baseValueOffset += numInstructions
		baseValueIncrement.append(baseValueOffset) #KEEPING TRACK OF BASE VALUE IN EACH MODILE
		# logger.debug("Pointer: {}, Number of Instructions: {} Base Value Offset {}".format(pointer, numInstructions, baseValueOffset))
		pointer+=1
		for index in range(numInstructions):
			instructions.append(input[pointer+index]) #CREATING A LIST OF ONLY INSTRUCTIONS
			# logger.debug("Adding {} to instruction list".format(input[pointer+index]))
		pointer += numInstructions
		# logger.debug("Next modules starting at index: {}".format(pointer))
		module=module+1


def SecondPass(input):
	pointer = 0
	module = 0
	baseValueOffset = 0
	useList = []
	while module<MODULE_NUM:
		for index in useIndex:
			pointer=index
			numUses = input[pointer]
			tempUseDict = {} #temporary dictionary to check whether multiple values have same use
			for x in range(1,numUses*2+1, 2):
				# logger.debug("{} is used at {}".format(input[x + pointer], input[x + pointer + 1]))
				if input[x+pointer+1] in tempUseDict.keys():
					error = 8
					tempUseDict[input[x + pointer + 1]] = input[x + pointer]
					errorList.append(ErrorCheck(error, tempUseDict[input[x+pointer+1]]))
				else:
					tempUseDict[input[x+pointer+1]] = input[x+pointer]
			# logger.debug("tempUseDict is {}".format(tempUseDict))
			for value,key in tempUseDict.items():
				# logger.debug("{} is used at {}".format(key, value))
				useList.append(key)
				numResolve(key, value, baseValueOffset) #CALLING NUMRESOLVE - A RECURSIVE FUNCTION THAT DEALS WITH EXTERNAL ADDRESSES

			#
			# for x in range(1, numUses*2+1, 2):
			# 	logger.debug("{} is used at {}".format(input[x+pointer], input[x+pointer+1]))
			# 	useList.append(input[x+pointer])
			# 	logger.debug("Instruction list is {}".format(instructions))
			# 	numResolve(input[x+pointer], input[x+pointer+1], baseValueOffset)
			# logger.debug("Finished resolving externals for module {}".format(module))
			instructionsResolve(baseValueOffset, module) #RESOLVES ALL THE OTHER INSTRUCTIONS WITHIN THE MODULE
			baseValueOffset =  baseValueIncrement[module] #CHANGES THE OFFSET
			module = module + 1 #MOVES ON TO NEXT MODULE
		# print(value)
	for key in symbolModule.keys():
		if key not in useList:
			error = 4
			errorList.append(ErrorCheck(error, key)) #ITERATES OVER USES AND DISPLAYS ERROR IF KEY NOT USED
	for key, value in variableDict.items(): #CHECKS IF THE KEY WAS DEFINED IN AN INSTRUCTION OUTSIDE THE ONE GIVEN
		if (symbolAddress[key] + 1) > numInsPerModule[symbolModule[key]]:
			error = 5
			errorList.append(ErrorCheck(error, key))
			variableDict[key] =  (variableDict[key] - symbolAddress[key])

	# logger.debug("Final Instruction list is {}".format(instructions))
	# logger.debug("Use List: {}".format(useList))

def instructionsResolve(offset, currentMod):
	for i in range(numInsPerModule[currentMod]):
		ptr = offset+i
		current = str(instructions[ptr])
		# print(len(current))
		if len(current) == 5:
			if int(current[4]) == 1:
				instructions[ptr] = int(current[0:4])
			elif int(current[4]) ==2:
				if int(current[1:4])>=MAX_SIZE:
					error = 7
					instructions[ptr] = (int(current[0])*1000)+(MAX_SIZE-1)
					errorList.append(ErrorCheck(error,current))
				else:
					instructions[ptr] = int(current[0:4])
			elif int(current[4]) == 3:
				addField = int(current[1:4])
				newAddField = addField+offset
				newNum = (int(current[0])*1000)+newAddField
				# logger.debug("New add field {}. Current: {} Final: {}".format(newAddField, int(current), newNum))
				instructions[ptr] = newNum
			elif int(current[4]) ==4:
				error = 6
				instructions[ptr] = int(current[0:4])
				errorList.append(ErrorCheck(error, current))
		else:
			pass
		# logger.debug("Current Mod {}. Instruction: {}".format(currentMod, current))
	# print(offset, instructions[offset], numInsPerModule[currentMod] )

def numResolve(keyValue, index, offset):
	# logger.debug("Call to numResolve for {} at {}".format(keyValue, index+offset))
	ptr = index+offset
	insString = str(instructions[ptr])
	# logger.debug("Instruction String is {}".format(insString))
	if int(insString[4] ) == 4 or int(insString[4])==3:
		newJump = int(insString[1:4])
		if keyValue in variableDict.keys():
			# logger.debug("replacing with {}".format(variableDict[keyValue]))
			if (symbolAddress[keyValue]+1) > numInsPerModule[symbolModule[keyValue]]:
				# error = 5
				# errorList.append(ErrorCheck(error, keyValue))
				instructions[ptr] = int(insString[0:4]) - newJump + variableDict[keyValue] - symbolAddress[keyValue]
			# variableDict[keyValue] = (variableDict[keyValue] - symbolAddress[keyValue])
			# 	logger.debug("New Value {}".format((variableDict[keyValue]-symbolAddress[keyValue])))

			else:
				instructions[ptr] = int(insString[0:4]) - newJump + variableDict[keyValue]
		else:
			error = 2
			instructions[ptr] = int(insString[0:4]) - newJump
			errorList.append(ErrorCheck(error,keyValue))
		if newJump == 777:
			pass
		else:
			numResolve(keyValue,newJump,offset)
	elif int(insString[4]) == 1:
		error = 3
		errorList.append(ErrorCheck(error, insString))
		insString = insString[0:4]+'4'
		instructions[ptr] = int(insString)
		numResolve(keyValue, index, offset)


def ErrorCheck(error, key):
	errString = ''
	if error ==1:
		errString = errString + 'Error:  '+key+' was multiply defined. First value used.'
	elif error == 2:
		errString = errString + 'Error: '+key+' was used but not defined. Used zero instead.'
	elif error ==3:
		errString = errString + 'Error: immediate address '+key+' appeared on a use list. Was treated as a relative address.'
	elif error ==4:
		errString = errString +'Warning: '+ key + ' was defined in module ' + str(symbolModule[key]) + ' but never used.'
	elif error ==5:
		errString = errString + 'Error: The definition of '+key+' was outside module '+str(symbolModule[key])+'. Zero (relative) used.'
	elif error ==6:
		errString = errString + 'Error: '+key+' is an E type address that was not on use-chain; treated as I type.'
	elif error ==7:
		errString = errString + 'Error: '+key+' is an absolute address that exceeds the size of the machine ('+str(MAX_SIZE)+'). Largest legal value used.'
	elif error ==8:
		errString = errString + 'Error: multiple symbols are listed as used in the same instruction in module '+str(symbolModule[key])+'. '+key+ ' will be considered the last usage and others will be ignored.'
	return errString

def PrintingOutput():
	print('Symbol Table')
	for key in variableDict.keys():
		print(str(key)+' : '+ str(variableDict[key]))
	print('\n')
	print('Memory Map')
	for index, value in enumerate(instructions):
		print(str(index)+' :\t '+str(value))
	print('\n')
	for error in errorList:
		print(error)


FirstPass(editedInput)
SecondPass(editedInput)
PrintingOutput()
