from time import strptime, struct_time

from . import db
TIME_FORMAT = '%I:%M %p'


# convert a list of times in string format to one in python time objects
def convert_times_to_native_time_objects(times_in_string):
    times_in_time = []
    for stime in times_in_string:
        times_in_time.append(convert_string_to_time(stime))
    return times_in_time


def convert_string_to_time(stime):
    return strptime(stime, TIME_FORMAT)


# b-search across a sorted list to find the next time.  If we end up off the end then return the 1st element
def find_next_concurrent_trains(concurrent_train_times, time_searched):
    key = time_searched.tm_hour * 60 + time_searched.tm_min

    minute_of_day = concurrent_train_times[key]
    if minute_of_day:
        time = struct_time((0,0,0, #year.mon.day
                            int(minute_of_day/60),
                            minute_of_day%60,
                            0, 0, 0, 0 #sec and smaller
                            ))
        return time
    return None


# return a list of times that can be indexed into to return the next avalable train
def build_concurrent_train_list():
    it = db.keys()
    concurrent_list = [0]*24*60 #build array of 0's to hold values
    for key in it:
        times_in_string = db.fetch(key)['times']
        times = convert_times_to_native_time_objects(times_in_string)
        for t in times:
            concurrent_list[t.tm_hour * 60 + t.tm_min] += 1

    current_concurrent_value = None
    # grab the min value to set the concurrent list with as we walk backwards
    for idx, val in enumerate(concurrent_list):
        if val > 1:
            current_concurrent_value = idx
            break

    concurrent_lookup = [None]*24*60

    for idx in range(len(concurrent_list)-1, -1, -1):
        if concurrent_list[idx] > 1:
            current_concurrent_value = idx
        concurrent_lookup[idx] = current_concurrent_value

    return concurrent_lookup
