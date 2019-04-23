
import sys
import copy

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.last_scheduled_time=arrive_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def end_simulation_time(process_list):
    n = len(process_list)
    last_process = process_list[n-1]
    end_tm = last_process.arrive_time + last_process.burst_time
    return end_tm+20

def append_schedules(scheduled_process,current_time, process_id):
    n = len(scheduled_process)
    if n > 0:
        last_schedule = scheduled_process[n-1]
        previous_prcs = last_schedule[1]
        if process_id != previous_prcs:
            scheduled_process.append((current_time, process_id))
    else:
        scheduled_process.append((current_time, process_id))

def RR_scheduling(process_list, time_quantum ):
    current_time = 0
    waiting_time = 0
    scheduled_process = []
    current_processing_queue = []
    end_tm = end_simulation_time(process_list)
    to_be_processed = copy.deepcopy(process_list)
    while current_time < end_tm:
        while to_be_processed.__len__() > 0:
            tba_process = to_be_processed[0]
            process_arrv_tm = tba_process.arrive_time
            if process_arrv_tm <= current_time+time_quantum:
                current_processing_queue.append(tba_process)
                to_be_processed.pop(0)
            else:
                break

        if current_processing_queue.__len__() > 0:
            current_process = current_processing_queue[0]
            process_arrv_tm = current_process.arrive_time
            if process_arrv_tm <= current_time:
                current_process = current_processing_queue.pop(0)
                if current_time < current_process.last_scheduled_time:
                    current_time = current_process.last_scheduled_time
                waiting_time = waiting_time + (current_time - current_process.last_scheduled_time)
                append_schedules(scheduled_process, current_time, current_process.id)  # processing
                if current_process.burst_time > time_quantum:
                    current_process.burst_time -= time_quantum
                    current_time += time_quantum
                    current_process.last_scheduled_time = current_time
                    current_processing_queue.append(current_process)
                else:
                    current_time += current_process.burst_time
                    current_process.burst_time = 0
                    current_process.last_scheduled_time = current_time
            else:
                current_time += 1
        else:
            current_time += 1

    average_waiting_time = waiting_time / float(len(process_list))
    return scheduled_process, average_waiting_time

def SRTF_scheduling(process_list):
    current_time = 0
    waiting_time = 0
    scheduled_process = []
    current_processing_queue = []
    to_be_processed = copy.deepcopy(process_list)
    end_tm = end_simulation_time(process_list)

    while current_time < end_tm:
        if to_be_processed.__len__() > 0:
            tba_process = to_be_processed[0]
            if tba_process.arrive_time == current_time:
                current_processing_queue.append(tba_process)
                to_be_processed.pop(0)

        if current_processing_queue.__len__() > 0:
            current_processing_queue = sorted(current_processing_queue, key=lambda process: process.burst_time)
            curr_process = current_processing_queue.pop(0)
            append_schedules(scheduled_process, current_time, curr_process.id)# processing
            if curr_process.burst_time > 1:
                curr_process.burst_time -= 1
                waiting_time = waiting_time + (current_time - curr_process.last_scheduled_time)
                current_time += 1
                curr_process.last_scheduled_time = current_time
                current_processing_queue.append(curr_process)
            else:
                curr_process.burst_time = 0
                waiting_time = waiting_time + (current_time - curr_process.last_scheduled_time)
                current_time += 1
                curr_process.last_scheduled_time = current_time
        else:
            current_time += 1

    average_waiting_time = waiting_time / float(len(process_list))
    return scheduled_process, average_waiting_time

def init_expected_burst_time(to_be_processed, initial_guess):
    expected_burst_time = {}
    for process in to_be_processed:
        expected_burst_time[process.id] = initial_guess
    return expected_burst_time



def find_expected_burst_time(alpha,actual_burst_time,predicted_burst_time):
    expected_burst_time = (alpha*actual_burst_time) + ((1-alpha) * predicted_burst_time)
    return expected_burst_time

def SJF_scheduling(process_list, alpha):
    current_time = 0
    waiting_time = 0
    current_processing_queue = []
    scheduled_process = []
    to_be_processed = copy.deepcopy(process_list)
    end_tm = end_simulation_time(process_list)

    expected_burst_time = init_expected_burst_time(to_be_processed, initial_guess=5)

    while current_time < end_tm:
        while to_be_processed.__len__() > 0:
            tba_process = to_be_processed[0]
            process_arrv_tm = tba_process.arrive_time
            if process_arrv_tm <= current_time:
                process_id = tba_process.id
                tba_process.expected_burst_time = expected_burst_time[process_id]
                current_processing_queue.append(tba_process)
                to_be_processed.pop(0)
            else:
                break

        if current_processing_queue.__len__() > 0:
            current_processing_queue = sorted(current_processing_queue, key=lambda process: process.expected_burst_time)
            current_process = current_processing_queue.pop(0)
            waiting_time = waiting_time + (current_time - current_process.last_scheduled_time)
            scheduled_process.append((current_time, current_process.id))  # processing
            current_time += current_process.burst_time
            process_id = current_process.id
            expected_burst_time[process_id] = find_expected_burst_time(alpha, current_process.burst_time, current_process.expected_burst_time)
        else:
            current_time += 1

    average_waiting_time = waiting_time / float(len(process_list))
    return scheduled_process, average_waiting_time


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("incorrect input received")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("<---printing input data ---->")
    for process in process_list:
        print (process)
    print ("<---Building FCFS---->")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("<---Building RR ---->")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("<---Building SRTF ---->")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("<---Building SJF ---->")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])
