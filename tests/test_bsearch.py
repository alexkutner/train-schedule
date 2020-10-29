import flaskr.routes as routes

TIMES = ['03:00 AM', '05:00 AM', '09:00 AM', '05:00 PM', '05:02 PM', '09:03 PM']
ENCODED_TIMES = routes.convert_times_to_native_types(TIMES)


def test_search():
    assert ENCODED_TIMES[0] == routes.find_next_concurrent_trains(ENCODED_TIMES, '1:00 AM')
    assert ENCODED_TIMES[1] == routes.find_next_concurrent_trains(ENCODED_TIMES, '3:01 AM')
    assert ENCODED_TIMES[3] == routes.find_next_concurrent_trains(ENCODED_TIMES, '9:01 AM')
    assert ENCODED_TIMES[0] == routes.find_next_concurrent_trains(ENCODED_TIMES, '10:00 PM')
    assert ENCODED_TIMES[5] == routes.find_next_concurrent_trains(ENCODED_TIMES, '9:02 PM')
    assert ENCODED_TIMES[5] == routes.find_next_concurrent_trains(ENCODED_TIMES, '9:03 PM')

    assert None == routes.find_next_concurrent_trains([], '9:03 PM')
