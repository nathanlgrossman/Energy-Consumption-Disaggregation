
from __future__ import division
from math import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def findPulses(aggregateSignal, expectedHeight, expectedWidth, heightMargin, widthMargin):
    pulseTrain = np.zeros(len(aggregateSignal))
    pulseFound = 0
    estimatedHeight = 0
    # For every sample in the time series under consideration ...
    for i in range(expectedWidth,(len(aggregateSignal) - int(2*expectedWidth))):
        # If not in the pulseFound state, check whether the conditions are met for entering the pulseFound state.
        if pulseFound == 0:
            previousMin = min(aggregateSignal[(i - int((widthMargin/8)*expectedWidth)):(i - 1)])
            currentMin = min(aggregateSignal[i:(i + int((1 - 2*widthMargin)*expectedWidth))])
            futureMin = min(aggregateSignal[(i + expectedWidth + 1):(i + expectedWidth + \
                                                                     int(4*widthMargin*expectedWidth))])
            # If the minimum of the time series over the "current and short-term future range" of samples is:
            # (1) greater than the minimum of the time series over the "past range" of samples (by an amount
            # approximately equal to the expected height of the pulse); and
            # (2) greater than the minimum of the time series over the "longer-term future range" of samples (by an
            # amount approximately equal to the expected height of the pulse); then
            # enter the pulseFound state.
            # Note that the "short-term future range" extends from the current instant to a future interval equal to
            # the approximate expected width of the pulse; and the "longer-term future range" extends into the future
            # beyond the approximate expected width of the pulse.
            if ((currentMin - previousMin) > (1 - 2*heightMargin)*expectedHeight) \
                & ((currentMin - previousMin) < (1 + 4*heightMargin)*expectedHeight) \
                & ((futureMin - previousMin) < (1 - 2*heightMargin)*expectedHeight):
                pulseFound = 1
                estimatedHeight = currentMin - previousMin
        # If in the pulseFound state, check whether the conditions are met for exiting the pulseFound state.
        if pulseFound == 1:
            # If the current sammple is less than the minimum of the time series over the approximate expected width
            # of the pulse, then exit the pulseFound state.
            if aggregateSignal[i] < currentMin:
                pulseFound = 0
                estimatedHeight = 0
        # Set the current sample of the estimated pulse train equal to the estimated height of the pulse,
        # which equal to:
        # the delta between "the current and short-term future minimum" and
        # "the past minimum" if in the pulseFound state; and
        # zero if not in the pulseFound state.
        pulseTrain[i] = estimatedHeight
    return pulseTrain


print "Begin Energy Consumption Disaggregation"

###########################
# Read data from CSV file #
###########################
print "Reading data from CSV file"

data = pd.read_csv('data.csv', names=['time', 'power'])
time = np.asarray(data['time'])
power = np.asarray(data['power'])

#############################################################
# Specify number of samples for intervals of various widths #
#############################################################
print "Specifying number of samples for intervals of various widths"
samplesPerSecond = 1
samplesPerMinute = 60 * samplesPerSecond
samplesPerHour = 60 * samplesPerMinute
samplesPerDay = 24 * samplesPerHour
samplesPerMonth = 31 * samplesPerDay

#############################
# Define appliance profiles #
#############################
print "Defining appliance profiles"

ac1Profile = {'expectedHeight':2750, 'expectedWidth':int((12*samplesPerMinute)), \
              'heightMargin':0.10, 'widthMargin':0.15}

ac2Profile = {'expectedHeight':4000, 'expectedWidth':int((60*samplesPerMinute)), \
              'heightMargin':0.10, 'widthMargin':0.25}

pumpProfile = {'expectedHeight':1520, 'expectedWidth':int((2.8*samplesPerHour)), \
               'heightMargin':0.10, 'widthMargin':0.10}

fridgeProfile = {'expectedHeight':180, 'expectedWidth':int((45*samplesPerMinute)), \
                 'heightMargin':0.10, 'widthMargin':0.25}

testSignal = power
# startPoint = 1600000
# endPoint = startPoint + 3 * samplesPerDay
# testSignal = power[startPoint:(endPoint)]
# power = power[startPoint:(endPoint)]
# time = time[startPoint:(endPoint)]

##########################
# Search for AC 1 pulses #
##########################
print "Searching for AC 1 pulses"

ac1Signal = findPulses(testSignal, ac1Profile['expectedHeight'], ac1Profile['expectedWidth'], \
                       ac1Profile['heightMargin'], ac1Profile['widthMargin'])

print "Writing AC 1 data to CSV file"

ac1Columns = ['time', 'power', 'ac1Signal']
ac1Data = pd.DataFrame([], columns=list(ac1Columns))
ac1Data['time'] = time
ac1Data['power'] = power
ac1Data['ac1Signal'] = ac1Signal
ac1Data.to_csv('ac1_signal_data.csv')

##########################
# Search for AC 2 pulses #
##########################
print "Searching for AC 2 pulses"

ac2Signal = findPulses(testSignal, ac2Profile['expectedHeight'], ac2Profile['expectedWidth'], \
                       ac2Profile['heightMargin'], ac2Profile['widthMargin'])

print "Writing AC 2 data to CSV file"

ac2Columns = ['time', 'power', 'ac2Signal']
ac2Data = pd.DataFrame([], columns=list(ac2Columns))
ac2Data['time'] = time
ac2Data['power'] = power
ac2Data['ac2Signal'] = ac2Signal
ac2Data.to_csv('ac2_signal_data.csv')

###############################
# Search for pool pump pulses #
###############################
print "Searching for pool pump pulses"

pumpSignal = findPulses(testSignal, pumpProfile['expectedHeight'], pumpProfile['expectedWidth'], \
                        pumpProfile['heightMargin'], pumpProfile['widthMargin'])

print "Writing pool pump data to CSV file"

pumplColumns = ['time', 'power', 'pumpSignal']
pumplData = pd.DataFrame([], columns=list(pumplColumns))
pumplData['time'] = time
pumplData['power'] = power
pumplData['pumpSignal'] = pumpSignal
pumplData.to_csv('pump_signal_data.csv')

##################################
# Search for refrigerator pulses #
##################################
print "Searching for refrigerator pulses"

fridgeSignal = findPulses(testSignal, fridgeProfile['expectedHeight'], fridgeProfile['expectedWidth'], \
                          fridgeProfile['heightMargin'], fridgeProfile['widthMargin'])

print "Writing refrigerator data to CSV file"

fridgelColumns = ['time', 'power', 'fridgeSignal']
fridgelData = pd.DataFrame([], columns=list(fridgelColumns))
fridgelData['time'] = time
fridgelData['power'] = power
fridgelData['fridgeSignal'] = fridgeSignal
fridgelData.to_csv('fridge_signal_data.csv')

###############################################
# Read and plot processed data from CSV files #
###############################################
print "Reading processed data from CSV file"

# Read AC 1 data
ac1Data = pd.read_csv('ac1_signal_data.csv')
time = np.asarray(ac1Data['time'])
power = np.asarray(ac1Data['power'])
ac1Signal = np.asarray(ac1Data['ac1Signal'])

# Plot AC 1 data
plt.plot(time, power, label='Total Power', color='blue')
plt.plot(time, ac1Signal, label='AC 1 Power', color='red')
plt.legend(loc='upper left')
plt.xlim(min(time), max(time))
plt.xlabel("Time: Seconds / Unix Timestamp")
plt.ylabel("Power: Watts")
plt.title("AC 1 Time Series")
plt.show()

# Read AC 2 data
ac2Data = pd.read_csv('ac2_signal_data.csv')
time = np.asarray(ac2Data['time'])
power = np.asarray(ac2Data['power'])
ac2Signal = np.asarray(ac2Data['ac2Signal'])

# Plot AC 2 data
plt.plot(time, power, label='Total Power', color='blue')
plt.plot(time, ac2Signal, label='AC 2 Power', color='red')
plt.legend(loc='upper left')
plt.xlim(min(time), max(time))
plt.xlabel("Time: Seconds / Unix Timestamp")
plt.ylabel("Power: Watts")
plt.title("AC 2 Time Series")
plt.show()

# Read pool pump data
pumpData = pd.read_csv('pump_signal_data.csv')
time = np.asarray(pumpData['time'])
power = np.asarray(pumpData['power'])
pumpSignal = np.asarray(pumpData['pumpSignal'])

# Plot pool pump data
plt.plot(time, power, label='Total Power', color='blue')
plt.plot(time, pumpSignal, label='Pool Pump Power', color='red')
plt.legend(loc='upper left')
plt.xlim(min(time), max(time))
plt.xlabel("Time: Seconds / Unix Timestamp")
plt.ylabel("Power: Watts")
plt.title("Pool Pump Time Series")
plt.show()

# Read refrigerator data
fridgeData = pd.read_csv('fridge_signal_data.csv')
time = np.asarray(fridgeData['time'])
power = np.asarray(fridgeData['power'])
fridgeSignal = np.asarray(fridgeData['fridgeSignal'])

# Plot refrigerator data
plt.plot(time, power, label='Total Power', color='blue')
plt.plot(time, fridgeSignal, label='Refrigerator Power', color='red')
plt.legend(loc='upper left')
plt.xlim(min(time), max(time))
plt.xlabel("Time: Seconds / Unix Timestamp")
plt.ylabel("Power: Watts")
plt.title("Refrigerator Time Series")
plt.show()

print "End Energy Consumption Disaggregation"


