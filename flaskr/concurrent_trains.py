from time import strptime

from . import db
TIME_FORMAT = '%I:%M %p'


# convert a list of times in string format to one in python time objects
def convert_times_to_native_types(times_in_string):
    times_in_time = []
    for stime in times_in_string:
        times_in_time.append(convert_string_to_time(stime))
    return times_in_time


def convert_string_to_time(stime):
    return strptime(stime, TIME_FORMAT)


# b-search across a sorted list to find the next time.  If we end up off the end then return the 1st element
def find_next_concurrent_trains(concurrent_train_times, time_searched):
    start = 0
    end = len(concurrent_train_times)
    if end == 0:
        return None

    while start < end:
        mid = int((start + end) / 2)
        if concurrent_train_times[mid] == time_searched:
            return time_searched
        elif concurrent_train_times[mid] < time_searched:
            start = mid + 1
        else:
            end = mid

    # if we went past the end looking return the 1st element as we want to wrap
    if start >= len(concurrent_train_times):
        start = 0
    return concurrent_train_times[start]


# return a sorted list of times when multiple trains will be in the station at the same time
# The list is build by doing a sort of merge sort across all routes submitted
def build_concurrent_train_list():
    it = db.keys()
    schedules = list()
    for key in it:
        times_in_string = db.fetch(key)['times']
        schedules.append(convert_times_to_native_types(times_in_string))

    concurrent_list = []
    while len(schedules) > 1:
        popset = []
        min_val = None
        # move through sets looking for small non matches or groups of matches
        for i in range(0, len(schedules)):
            if not min_val or min_val > schedules[i][0]:
                popset = [i]
                min_val = schedules[i][0]
            elif min_val == schedules[i][0]:
                min_val == schedules[i][0]
                popset.append(i)

        # if we found a match copy it from the first schedule we saw it on
        if len(popset) > 1:
            concurrent_list.append(schedules[popset[0]][0])

        # remove smallest items in list
        deletion_adjuster = 0
        for i in popset:
            schedules[i-deletion_adjuster].pop(0)
            if len(schedules[i-deletion_adjuster]) == 0:
                schedules.pop(i-deletion_adjuster)
                deletion_adjuster += 1

        # store the data in time types so we can search against it
    return concurrent_list
