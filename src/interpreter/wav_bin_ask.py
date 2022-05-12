# determine the noise floor
# determine the high value
# reduce the amount of points representing a value
# 2 different scales: passcodes, high and low
import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy as np

fs, amplitude = wavfile.read('../data/latest.wav')
if len(np.shape(amplitude[0]) ):
    amplitude, dont_care = zip(*amplitude)

# have info in seconds and amplitude
data = [[i*1/fs, (y**2)**(1/2)] for i, y in enumerate(amplitude)]
x_data, y_data = zip(*data)
y_data = list(y_data)

# calculate the threshold to seperate high and low
amp_total = sum(y_data)
y_data = y_data/amp_total
stats_amp = [[amplitude, amplitude] for amplitude in y_data]

amp_mean = sum(list(map(lambda x: x**2, y_data))) # weighted mean, giving more weight to higher amplitudes
print("Minimum amplitude to be considered HIGH", amp_mean)

# data uses info that includes only highs, the spaces between 1s will be the zeros
bin_data = [[x, 1] for x,y in zip(x_data, y_data) if y>amp_mean]


# 3 time scales to be considered when determining a high and a low
# Code space, bit space (space between a high and low), sample space
# therefore, we have to determine when a new code starts, when a bit ends, and when points are linked to the same high value respectively
time_diff = [int((point_1[0]-point_0[0])*1000000)/1000000 for point_0, point_1 in zip(bin_data, bin_data[1:])]
total_dtime = sum(list(map(lambda x: x**2, time_diff)))
pdf_dtime = [[time, (time**2)/total_dtime] for time in time_diff] # creates a pdf of the time differences between points (more weight to more time).
x_dtime, p_dtime = zip(*pdf_dtime)
code_cluster_thresh = sum(list(map(lambda x,p: p*x, x_dtime, p_dtime)))
print("Value to be considered code seperator", code_cluster_thresh)
distance_codethresh = [abs(dtime-code_cluster_thresh) for dtime in time_diff] # calculate the distance from timediff to code_thresh_cluster
distance_codethresh.sort()
code_dtimes = [dtime for dtime in time_diff if abs(dtime-code_cluster_thresh) in distance_codethresh[:5] ] # seperated codespaces (We know there are 5 codes preamble + 4 repetitions)

# separating bit and sample dtime
dtimes = [dtime for dtime in time_diff if abs(dtime-code_cluster_thresh) not in distance_codethresh[:5] ]  # only contains dtime between bits and between "samples"
avg_dtime = sum(dtimes)/len(dtimes)
y_dtimes_set = set(dtimes)
dtime_hist = [[dtimes.count(dtime), dtime] for dtime in y_dtimes_set]
dtime_hist = [hist for hist in dtime_hist if hist[1] > 0.0001]
dtime_hist.sort(reverse = True )
bit_dtime = dtime_hist[0:2] # the reason why we consider there to be 2 times~
bit_dtime = [x[1] for x in bit_dtime]
sample_dtime = 0
bit_dtime.sort()
print("delta times for code/bit/sample:", code_cluster_thresh,"/", bit_dtime,"/", sample_dtime)

# we now have the information for the delta time which indicates when it is a code, a bit or a sample
# go through the binary data and reduce the bit info
delta_time = bin_data[1][0]-bin_data[0][0]
distance = [abs(delta_time - sample_dtime), abs(delta_time - bit_dtime[0]), abs(delta_time - bit_dtime[1]), abs(delta_time - code_cluster_thresh)]
prev_distance = distance
reduced_data = [bin_data[0]]
for i, (point0, point1) in enumerate(zip(bin_data[1:], bin_data[2:])):
    delta_time = point1[0]-point0[0]
    distance = [abs(delta_time - sample_dtime), abs(delta_time - bit_dtime[0]), abs(delta_time - bit_dtime[1]), abs(delta_time - code_cluster_thresh)] # distance[0]:sample, distance[1]:bit, distance[2]: code
    if((min(distance) == distance[0]) and (min(prev_distance) == prev_distance[0])):
        pass
    else:
        reduced_data.append(point0)
    prev_distance = distance

reduced_data.append(bin_data[-1]) # include the last element as well

seperated_codes = []
prev_i = 0
for i, (point0, point1) in enumerate(zip(reduced_data, reduced_data[1:])):
    delta_time = point1[0]-point0[0]
    distance = [abs(delta_time - bit_dtime[0]), abs(delta_time - bit_dtime[1]), abs(delta_time - code_cluster_thresh)] # distance[0]:sample, distance[1]:bit, distance[2]: code
    if(min(distance) == distance[2]):
        seperated_codes.append(reduced_data[prev_i:i+1])
        prev_i = i+1

# go through the codes and add 0s between every pair
two_levels = []
for j, code in enumerate(seperated_codes):
    for i in range(0,len(code), 2):
        if(i>0):
            two_levels[j].append([code[i][0]-0.000001, 0])
            two_levels[j].append(code[i])
            two_levels[j].append(code[i+1])
            two_levels[j].append([code[i+1][0]+0.000001, 0])
        else:
            two_levels.append([code[i], code[i+1], [code[i+1][0]+0.000001, 0] ])



# determine PWM for a 1, and for a 0,
bit_code_dtime = []
for j, code in enumerate(seperated_codes):
    for i in range(0, len(code)//2):
        point0, point1 = code[i*2], code[i*2+1]
        to_add = point1[0]-point0[0]
        if i==0:
            bit_code_dtime.append([to_add])
        else:
            bit_code_dtime[j].append(to_add)



code_strings =[]
for i, code in enumerate(bit_code_dtime):
    for j, bit in enumerate(code):
        distance = [((bit-bit_dtime[0])**2)**(1/2), ((bit-bit_dtime[1])**2)**(1/2)] # [0]: provides distance ot the first bit_dtime , [1]: distance to the second bit d_time
        to_add = "0" if min(distance) == distance[0] else "1"
        if(j==0):
            code_strings.append(to_add)
        else:
            code_strings[i] += to_add


for code in code_strings:
    print(code, len(code))


# plot square wave
# x_list, y_list = zip(*two_levels[2])
# plt.plot(x_list, y_list, color='darkgreen')
# plt.show()

# x_list, y_list = zip(*seperated_codes[0])
# plt.scatter(x_list, y_list)
# plt.show()
