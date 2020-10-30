from flaskr.concurrent_trains import find_next_concurrent_trains, convert_times_to_native_time_objects, convert_string_to_time

TIMES = ['03:00 AM', '05:00 AM', '09:00 AM', '05:00 PM', '05:02 PM', '09:03 PM']
ENCODED_TIMES = convert_times_to_native_time_objects(TIMES)


def test_search():
    assert ENCODED_TIMES[0] == find_next_concurrent_trains(ENCODED_TIMES, convert_string_to_time('1:00 AM'))
    assert ENCODED_TIMES[1] == find_next_concurrent_trains(ENCODED_TIMES, convert_string_to_time('3:01 AM'))
    assert ENCODED_TIMES[3] == find_next_concurrent_trains(ENCODED_TIMES, convert_string_to_time('9:01 AM'))
    assert ENCODED_TIMES[0] == find_next_concurrent_trains(ENCODED_TIMES, convert_string_to_time('10:00 PM'))
    assert ENCODED_TIMES[5] == find_next_concurrent_trains(ENCODED_TIMES, convert_string_to_time('9:02 PM'))
    assert ENCODED_TIMES[5] == find_next_concurrent_trains(ENCODED_TIMES, convert_string_to_time('9:03 PM'))
    assert None == find_next_concurrent_trains([], convert_string_to_time('9:03 PM'))
