import sys
import copy

#constants used throughout program
PROCESS_LENGTH = 4
#constants for the different states
INITIAL= 'unstarted'
READY = 'ready'
RUNNING = 'running'
BLOCKED = 'blocked'
TERMINATED = 'terminated'
QUANTUM = 2
VERBOSE = False
#variable which opens the random numbers file to read from
randNumFile = open("random-numbers.txt", 'r')
#global because multiple functions use it and hard to overcome scope
finishTime = 0 #the cycles taken for all processes to terminate

#processes the input file. Returns a list of Process objects.
def processInput():
	with open(sys.argv[-1], 'r') as f:
		contents = f.read()
	contents = contents.split()
	contents = list(map(int,contents))
	numProcesses = contents.pop(0)
	allProcesses = []
	index = 1
	for i in range(0,len(contents),PROCESS_LENGTH):
		allProcesses.append(Process(contents[i:i+PROCESS_LENGTH],index))
		index+=1
	return allProcesses,numProcesses

#used to calculate CPU burst times
def randomOS(U):
	x = int(randNumFile.readline())
	return 1+x%U

class Process:
	def __init__(self, attrList, inputNum):
		self.A = attrList[0] #arrival time
		self.B = attrList[1] #used to give next CPU burst time (randomOS(B))
		self.C = attrList[2] #total CPU time needed
		self.M = attrList[3] #used to give I/O burst time
		self.inputNum = inputNum #position in inputfile
		self.state = INITIAL
		self.cpuRemainder = self.C #initial CPU remainder time is the total time
		self.FT = 0 #finishing time (cycle when it terminated --> cpu remainder went to 0)
		self.TAT = 0 #turnaround time --> total time spent in the CPU queue (from when it arrived, to started being processed to completion) (increment for running, blocked, ready)
		self.WT = 0 #waiting time --> time it had to wait for before it actually started to be processed. (TAT - burst time) (time spent in ready time)
		self.IOT = 0 #i/o time --> time spent in 'blocked' state
		self.runT = 0 #time the process spent running (increment when state == running)
		self.readyT = 0 #used for sorting, (reset readyT every time the process' state changes from anything else to ready)
		self.cpuBurst = 0 #this is both the cpuBurst and the IOBurst when in the blocked stage
		self.ioBurst = 0
		self.prevCPUBurst = 0
		self.quantum = QUANTUM
	
	def printProcess(self, index):
		print("Process {}".format(index))
		print("\t(A, B, C, M) = ({} {} {} {})".format(self.A, self.B, self.C, self.M))
		print("\tFinishing Time: {}".format(self.FT))
		print("\tTurnaround Time: {}".format(self.TAT))
		print("\tI/O Time: {}".format(self.IOT))
		print("\tWaiting Time: {}".format(self.WT))
	
	def runProcess(self):
		self.quantum = QUANTUM
		self.state = RUNNING
		nextBurst = randomOS(self.B)
		if (nextBurst > self.cpuRemainder):
			self.prevCPUBurst = self.cpuRemainder
			self.cpuBurst = self.prevCPUBurst
		else:
			self.prevCPUBurst = nextBurst
			self.cpuBurst = self.prevCPUBurst
	
	def runRRProcess(self):
		self.quantum = QUANTUM
		self.state = RUNNING
		if (self.cpuBurst ==0):
			self.runProcess()
		
def printAllProcesses(processList):
	for index, process in enumerate(processList):
		process.printProcess(index)

def print_verbose(processList, cycle, isRR):
	print('Before cycle {}: '.format(cycle), end=' ')
	for process in processList:
		if (process.state == BLOCKED):
			print(process.state+' '+str(process.ioBurst), end = ' ')
		elif(isRR): #ONLY HAVING THIS TO MATCH THE OUTPUT FILES GIVEN IN THE ORIGINAL HOMEWORK FOLDER.
			if process.state == RUNNING:
				print(process.state+' '+str(process.quantum), end=' ')
			elif process.state == READY:
				print(process.state+' 0 ', end=' ')
			else:
				print(process.state + ' ' + str(process.cpuBurst), end=' ')
		else:
			print(process.state+' '+str(process.cpuBurst), end=' ')
	print()

def printOutput(originalList,orderedList, numProcesses):
    print('The original input was: {} '.format(numProcesses), end = '')
    for process in originalList:
        print('({} {} {} {})'.format(process.A, process.B, process.C, process.M), end=' ')
    print()
    print('The sorted input is: {} '.format(numProcesses),end='')
    for process in orderedList:
        print('({} {} {} {})'.format(process.A, process.B, process.C, process.M), end=' ')
    print()
    print()

def printSummary(str, ioutil, processList):
    totalTAT = 0
    totalRT = 0
    totalWT = 0
    listFT = []
    print()
    print("The scheduling algorithm used was {}".format(str))
    print()
    for index, process in enumerate(processList):
        totalTAT = totalTAT+process.TAT
        totalRT = totalRT+ process.runT
        totalWT = totalWT+process.WT
        listFT.append(process.FT)
        process.printProcess(index)
    print()
    finishTime = max(listFT)
    cpuUtil = totalRT/finishTime
    io = ioutil/finishTime
    throughput = 100* (len(processList)/finishTime)
    avgTAT = totalTAT/len(processList)
    avgWT = totalWT/len(processList)
    print("Summary Data: ")
    print("\tFinishing time: ", finishTime)
    print("\tCPU Utilization: ", cpuUtil)
    print("\tI/O Utilization: ", io)
    print("\tThroughput: {} processes per 100 cycles".format(throughput))
    print("\tAverage turnaround time: ", avgTAT)
    print("\tAverage waiting time: ", avgWT)
    print("______________________________________________________________________________________________________")

def allTerminated(processList):
	terminated = []
	for process in processList:
		if process.state == TERMINATED:
			terminated.append(process)
	if len(terminated) == len(processList):
		return True
	else:
		return False

def filterByState(processList, state): #initially tried to manually append to seperate lists while running the loop --> but lists kept resetting so did not work.
	#returns a list with the correct states.
    filterList = []
    for process in processList:
        if process.state == state:
            filterList.append(process)
    return filterList

def FCFS():
	randNumFile.seek(0)
	originalList, numProcesses = processInput()
	processList = copy.deepcopy(originalList) #make a copy because you need the original input for printing.
	processList.sort(key=lambda process: process.A) #sort by arrival time for FCFS
	printOutput(originalList, processList,numProcesses)
	cycle = 0
	ioUtil = 0
	while(allTerminated(processList)==False):
		if ("--verbose" in sys.argv):
			print_verbose(processList, cycle, False)
		# runList = filterByState(processList, RUNNING)
		# readyList = filterByState(processList, READY)
		# blockedList = filterByState(processList, BLOCKED)
		# print('runlist: ', len(runList))
		# printAllProcesses(runList)
		# print('ready list: ', len(readyList))
		# printAllProcesses(readyList)
		# print('blocked list', len(blockedList))
		# printAllProcesses(blockedList)
		for index, process in enumerate(processList):
			if (process.state == INITIAL and cycle == process.A):
				# print("made ready", index)
				# readyList.append(process)
				process.state = READY
				process.readyT = cycle
			elif(process.state == READY):
				# readyList.append(process)
				# print("made ready", index)
				# process.printProcess(index)
				process.TAT+=1
				process.WT+=1
			elif(process.state == BLOCKED):
				process.TAT+=1
				process.IOT+=1
				if process.ioBurst == 1:
					# readyList.append(process)
					# print("made ready", index)
					# process.printProcess(index)
					process.ioBurst = 0
					process.state = READY
					process.readyT = cycle
				else:
					# blockedList.append(process)
					# process.printProcess(index)
					process.ioBurst-=1
			elif(process.state == RUNNING):
				# runList.append(process)
				# process.printProcess(index)
				process.TAT+=1
				process.runT+=1
				process.cpuRemainder-=1
				process.cpuBurst-=1
				if (process.cpuBurst == 0):
					process.state = BLOCKED
					# blockedList.append(process)
					process.ioBurst = process.prevCPUBurst*process.M
				if (process.cpuRemainder == 0):
					process.state = TERMINATED
					process.FT = cycle
					process.cpuBurst = 0
		runList = filterByState(processList, RUNNING)
		readyList = filterByState(processList, READY)
		blockedList = filterByState(processList, BLOCKED)
		if(len(blockedList)!=0):
			ioUtil+=1
		if(len(runList)==0):
			readyList = sorted(readyList, key=lambda process: (process.readyT, process.A, process.inputNum))
			if(len(readyList)!=0):
				process_to_run = readyList.pop(0)
				process_to_run.runProcess()
		cycle +=1
	printSummary("First Come First Served", ioUtil, processList)
	
def RR(): #code is almost the same as FCFS but takes quantum into account
	randNumFile.seek(0)
	originalList, numProcesses = processInput()
	processList = copy.deepcopy(originalList)
	processList.sort(key=lambda process: process.A)
	printOutput(originalList, processList,numProcesses)
	cycle = 0
	ioUtil = 0
	while(allTerminated(processList)==False):
		if ("--verbose" in sys.argv):
			print_verbose(processList, cycle, True)
		for index, process in enumerate(processList):
			if (process.state == INITIAL and cycle == process.A):
				process.state = READY
				process.readyT = cycle
			elif(process.state == READY):
				process.TAT+=1
				process.WT+=1
			elif(process.state == BLOCKED):
				process.TAT+=1
				process.IOT+=1
				if (process.ioBurst == 1):
					process.ioBurst = 0
					process.state = READY
					process.readyT = cycle
				else:
					process.ioBurst-=1
			elif(process.state == RUNNING):
				process.TAT+=1
				process.runT+=1
				process.cpuRemainder-=1
				process.cpuBurst-=1
				process.quantum -=1
				if (process.cpuBurst == 0):
					process.state = BLOCKED
					process.ioBurst = process.prevCPUBurst*process.M
				elif (process.quantum == 0):
					process.state = READY
					process.readyT = cycle
				if (process.cpuRemainder == 0):
					process.state = TERMINATED
					process.FT = cycle
					process.cpuBurst = 0
		runList = filterByState(processList, RUNNING)
		readyList = filterByState(processList, READY)
		blockedList = filterByState(processList, BLOCKED)
		if(len(blockedList)!=0):
			ioUtil+=1
		if(len(runList)==0):
			readyList = sorted(readyList, key=lambda process: (process.readyT, process.A, process.inputNum))
			if(len(readyList)!=0):
				process_to_run = readyList.pop(0)
				process_to_run.runRRProcess()
		cycle +=1
	printSummary("Round Robbin", ioUtil, processList)

def SJF():
	randNumFile.seek(0)
	originalList, numProcesses = processInput()
	processList = copy.deepcopy(originalList) #make a copy because you need the original input for printing.
	processList.sort(key=lambda process: process.A) #sort by arrival time for FCFS
	printOutput(originalList, processList,numProcesses)
	cycle = 0
	ioUtil = 0
	while(allTerminated(processList)==False):
		if ("--verbose" in sys.argv):
			print_verbose(processList, cycle, False)
		for index, process in enumerate(processList):
			if (process.state == INITIAL and cycle == process.A):
				process.state = READY
				process.readyT = cycle
			elif(process.state == READY):
				process.TAT+=1
				process.WT+=1
			elif(process.state == BLOCKED):
				process.TAT+=1
				process.IOT+=1
				if process.ioBurst == 1:
					process.ioBurst = 0
					process.state = READY
					process.readyT = cycle
				else:
					process.ioBurst-=1
			elif(process.state == RUNNING):
				process.TAT+=1
				process.runT+=1
				process.cpuRemainder-=1
				process.cpuBurst-=1
				if (process.cpuBurst == 0):
					process.state = BLOCKED
					process.ioBurst = process.prevCPUBurst*process.M
				if (process.cpuRemainder == 0):
					process.state = TERMINATED
					process.FT = cycle
					process.cpuBurst = 0
		runList = filterByState(processList, RUNNING)
		readyList = filterByState(processList, READY)
		blockedList = filterByState(processList, BLOCKED)
		if(len(blockedList)!=0):
			ioUtil+=1
		if(len(runList)==0):
			readyList = sorted(readyList, key=lambda process: (process.cpuRemainder, process.A, process.inputNum))
			if(len(readyList)!=0):
				process_to_run = readyList.pop(0)
				process_to_run.runProcess()
		cycle +=1
	printSummary("Shortest Job First", ioUtil, processList)

def HPRN():
	randNumFile.seek(0)
	originalList, numProcesses = processInput()
	processList = copy.deepcopy(originalList) #make a copy because you need the original input for printing.
	processList.sort(key=lambda process: process.A) #sort by arrival time for FCFS
	printOutput(originalList, processList,numProcesses)
	cycle = 0
	ioUtil = 0
	while(allTerminated(processList)==False):
		if ("--verbose" in sys.argv):
			print_verbose(processList, cycle, False)
		for index, process in enumerate(processList):
			if (process.state == INITIAL and cycle == process.A):
				process.state = READY
				process.readyT = cycle
			elif(process.state == READY):
				process.TAT+=1
				process.WT+=1
			elif(process.state == BLOCKED):
				process.TAT+=1
				process.IOT+=1
				if process.ioBurst == 1:
					process.ioBurst = 0
					process.state = READY
					process.readyT = cycle
				else:
					process.ioBurst-=1
			elif(process.state == RUNNING):
				process.TAT+=1
				process.runT+=1
				process.cpuRemainder-=1
				process.cpuBurst-=1
				if (process.cpuBurst == 0):
					process.state = BLOCKED
					process.ioBurst = process.prevCPUBurst*process.M
				if (process.cpuRemainder == 0):
					process.state = TERMINATED
					process.FT = cycle
					process.cpuBurst = 0
		runList = filterByState(processList, RUNNING)
		readyList = filterByState(processList, READY)
		blockedList = filterByState(processList, BLOCKED)
		if(len(blockedList)!=0):
			ioUtil+=1
		if(len(runList)==0):
			readyList = sorted(readyList, key=lambda process: (-(process.TAT/max(1,process.runT)), process.A, process.inputNum))
			if(len(readyList)!=0):
				process_to_run = readyList.pop(0)
				process_to_run.runProcess()
		cycle +=1
	printSummary("Highest Penalty Ratio Next", ioUtil, processList)

FCFS()
RR()
SJF()
HPRN()