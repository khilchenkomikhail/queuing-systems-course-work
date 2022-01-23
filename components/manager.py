import sys
import components.source as source
import components.buffer as buffer
import components.device as device

devices = []
sources = []
buffers = []
device_pointer = None
buffer_pointer = None

dict = {}


class CirclePointer:
    def __init__(self, overall_number):
        self.i = 0
        self.overall_number = overall_number

    def set_next(self):
        if self.i == self.overall_number - 1:
            self.i = 0
        else:
            self.i += 1

    def set_i(self, i):
        self.i = i

    def get_index(self):
        return self.i


def get_oldest_in_buffers():
    i = -1
    min_time = sys.float_info.max
    for j in range(len(buffers)):
        tmp = buffers[j].get_request_generation_time()
        if -1.0 < tmp < min_time:
            min_time = tmp
            i = j
    return i


def get_youngest_in_buffers():
    i = -1
    min_time = sys.float_info.min
    for j in range(len(buffers)):
        tmp = buffers[j].get_request_generation_time()
        if tmp > min_time and tmp > -1.0:
            min_time = tmp
            i = j
    return i


def handle_request(request, system_time):
    global dict
    start_dev_index = device_pointer.get_index()

    if devices[start_dev_index].request is None:
        devices[start_dev_index].set_request(request, system_time)
        device_pointer.set_next()
        sources[request.source_number - 1].processed_requests += 1
        sources[request.source_number - 1].processing_time.append(request.processing_time)
        return

    device_pointer.set_next()
    dev_index = device_pointer.get_index()
    while devices[dev_index].request is not None and dev_index != start_dev_index:
        device_pointer.set_next()
        dev_index = device_pointer.get_index()

    if dev_index != start_dev_index:
        devices[dev_index].set_request(request, system_time)
        device_pointer.set_next()
        sources[request.source_number - 1].processed_requests += 1
        sources[request.source_number - 1].processing_time.append(request.processing_time)
        return

    start_buff_index = buffer_pointer.get_index()
    if buffers[start_buff_index].request is None:
        buffers[start_buff_index].add_request(request, system_time)
        buffer_pointer.set_next()
        request.buffering_start_time = system_time
        return

    buffer_pointer.set_next()
    buff_index = buffer_pointer.get_index()
    while buffers[buff_index].request is not None and buff_index != start_buff_index:
        buffer_pointer.set_next()
        buff_index = buffer_pointer.get_index()

    if buff_index != start_buff_index:
        buffers[buff_index].add_request(request, system_time)
        request.buffering_start_time = system_time
        buffer_pointer.set_next()
        return

    old_i = get_oldest_in_buffers()
    request_refused = buffers[old_i].get_request(system_time)
    request_refused.buffering_end_time = system_time
    request_refused.refuse()

    sources[request_refused.source_number - 1].processing_time.append(request_refused.processing_time)
    sources[request_refused.source_number - 1].waiting_time.append(request_refused.buffering_time)

    buffer_pointer.set_i(old_i)
    buffers[old_i].add_request(request, system_time)
    request.buffering_start_time = system_time
    buffer_pointer.set_next()


def handle_request_step(request, system_time):
    global dict
    start_dev_index = device_pointer.get_index()

    if devices[start_dev_index].request is None:
        devices[start_dev_index].set_request(request, system_time)
        device_pointer.set_next()
        sources[request.source_number - 1].processed_requests += 1
        sources[request.source_number - 1].processing_time.append(request.processing_time)
        dict[str(system_time)] = [str(request.source_number) + '.' + str(request.number), 'dev', str(start_dev_index)]
        return

    device_pointer.set_next()
    dev_index = device_pointer.get_index()
    while devices[dev_index].request is not None and dev_index != start_dev_index:
        device_pointer.set_next()
        dev_index = device_pointer.get_index()

    if dev_index != start_dev_index:
        devices[dev_index].set_request(request, system_time)
        device_pointer.set_next()
        sources[request.source_number - 1].processed_requests += 1
        sources[request.source_number - 1].processing_time.append(request.processing_time)
        dict[str(system_time)] = [str(request.source_number) + '.' + str(request.number), 'dev', str(dev_index)]
        return

    start_buff_index = buffer_pointer.get_index()
    if buffers[start_buff_index].request is None:
        buffers[start_buff_index].add_request(request, system_time)
        buffer_pointer.set_next()
        request.buffering_start_time = system_time
        dict[str(system_time)] = [str(request.source_number) + '.' + str(request.number), 'buf', str(start_buff_index)]
        return

    buffer_pointer.set_next()
    buff_index = buffer_pointer.get_index()
    while buffers[buff_index].request is not None and buff_index != start_buff_index:
        buffer_pointer.set_next()
        buff_index = buffer_pointer.get_index()

    if buff_index != start_buff_index:
        buffers[buff_index].add_request(request, system_time)
        request.buffering_start_time = system_time
        buffer_pointer.set_next()
        dict[str(system_time)] = [str(request.source_number) + '.' + str(request.number), 'buf', str(buff_index)]
        return

    old_i = get_oldest_in_buffers()
    request_refused = buffers[old_i].get_request(system_time)
    request_refused.buffering_end_time = system_time
    request_refused.refuse()
    temp_key = ''
    for key, value in dict.items():
        if value[1] == 'buf' and int(value[0][:1]) == request_refused.source_number and int(value[0][-1]) == request_refused.number:
            temp_key = key
            break

    if temp_key != '':
        del dict[temp_key]

    dict[str(-1.0)] = [str(request_refused.source_number) + '.' + str(request_refused.number), 'refuse']
    sources[request_refused.source_number - 1].processing_time.append(request_refused.processing_time)
    sources[request_refused.source_number - 1].waiting_time.append(request_refused.buffering_time)

    buffer_pointer.set_i(old_i)
    buffers[old_i].add_request(request, system_time)
    request.buffering_start_time = system_time
    buffer_pointer.set_next()
    dict[str(system_time)] = [str(request.source_number) + '.' + str(request.number), 'buf', str(buff_index)]


def handle_buffered_requests(system_time):
    start_dev_index = device_pointer.get_index()
    dev_index = device_pointer.get_index()
    tmp = get_youngest_in_buffers()
    if not devices[dev_index].is_busy and tmp > -1.0:
        request = buffers[tmp].get_request(system_time)
        devices[dev_index].set_request(request, system_time)
        sources[request.source_number - 1].processed_requests += 1
        sources[request.source_number - 1].processing_time.append(request.processing_time)

    if tmp > -1.0:
        device_pointer.set_next()
        dev_index = device_pointer.get_index()

    tmp = get_youngest_in_buffers()
    while tmp > -1.0 and dev_index != start_dev_index:
        if not devices[dev_index].is_busy:
            request = buffers[tmp].get_request(system_time)
            devices[dev_index].set_request(request, system_time)
            sources[request.source_number - 1].processed_requests += 1
            sources[request.source_number - 1].processing_time.append(request.processing_time)
        device_pointer.set_next()
        dev_index = device_pointer.get_index()


def handle_buffered_requests_step(system_time):
    global dict
    start_dev_index = device_pointer.get_index()
    dev_index = device_pointer.get_index()
    tmp = get_youngest_in_buffers()
    if not devices[dev_index].is_busy and tmp > -1.0:
        request = buffers[tmp].get_request(system_time)
        devices[dev_index].set_request(request, system_time)
        sources[request.source_number - 1].processed_requests += 1
        sources[request.source_number - 1].processing_time.append(request.processing_time)

        for key, value in dict.items():
            if value[0] == str(request.source_number) + '.' + str(request.number):
                dict[key][1] = 'devs'
                dict[key][2] = str(dev_index)
                break

    if tmp > -1.0:
        device_pointer.set_next()
        dev_index = device_pointer.get_index()

    tmp = get_youngest_in_buffers()
    while tmp > -1.0 and dev_index != start_dev_index:
        if not devices[dev_index].is_busy:
            request = buffers[tmp].get_request(system_time)
            devices[dev_index].set_request(request, system_time)
            sources[request.source_number - 1].processed_requests += 1
            sources[request.source_number - 1].processing_time.append(request.processing_time)
            for key, value in dict.items():
                if value[0] == str(request.source_number) + '.' + str(request.number):
                    dict[key][1] = 'devs'
                    dict[key][2] = str(dev_index)
                    tmp = get_youngest_in_buffers()
                    break
        device_pointer.set_next()
        dev_index = device_pointer.get_index()


def get_first_in_devices():
    i = 0
    min_time = sys.float_info.max
    for j in range(len(devices)):
        tmp = devices[j].get_end_of_processing_time()
        if tmp < min_time and devices[j].request is not None:
            min_time = tmp
            i = j
    return i, min_time


def free_device(system_time):
    counter = 0
    for dev in devices:
        if dev.get_end_of_processing_time() == system_time and dev.request is not None:
            counter += 1
            dev.delete_request()
    return counter


def free_device_step(system_time):
    global dict
    counter = 0
    for dev in devices:
        if dev.get_end_of_processing_time() == system_time and dev.request is not None:
            counter += 1
            for key, value in dict.items():
                if dict[key][0] == str(dev.request.source_number) + '.' + str(dev.request.number):
                    del dict[key]
                    break
            dev.delete_request()
    return counter


def init(n_s, n_b, n_d, alpha, beta, lambda_param):
    devices.clear()
    sources.clear()
    buffers.clear()

    global device_pointer, buffer_pointer
    device_pointer = CirclePointer(n_d)
    buffer_pointer = CirclePointer(n_b)

    for i in range(n_s):
        temp_source = source.Source(i + 1, alpha, beta)
        sources.append(temp_source)
    for i in range(n_b):
        temp_buffer = buffer.Buffer(i + 1)
        buffers.append(temp_buffer)
    for i in range(n_d):
        temp_device = device.Device(i + 1, lambda_param)
        devices.append(temp_device)


def application(n_s, n_b, n_d, number_of_requests, alpha, beta, lambda_param):
    init(n_s, n_b, n_d, alpha, beta, lambda_param)

    processed_requests = 0
    generated_requests = 0

    first_request_time = sys.float_info.max

    for src in sources:
        tmp = src.next_generation()
        if  tmp < first_request_time:
            first_request_time = tmp
    system_time = first_request_time

    end = False

    while not end:
        requests = []
        for src in sources:
            if src.next_generation() == system_time and generated_requests < number_of_requests:
                requests.append(src.generate())
                generated_requests += 1

        processed_requests += free_device(system_time)
        handle_buffered_requests(system_time)
        for req in requests:
            handle_request(req, system_time)

        next_time = sys.float_info.max
        if generated_requests < number_of_requests:
            for src in sources:
                if next_time > src.next_generation() > -1.0:
                    next_time = src.next_generation()

        i, min_tmp = get_first_in_devices()
        if -1.0 < min_tmp < next_time:
            next_time = min_tmp

        if next_time < sys.float_info.max:
            system_time = next_time

        if generated_requests == number_of_requests:
            are_working_dev = False
            for dev in devices:
                if dev.is_busy:
                    are_working_dev = True
                    break
            are_full_buffer = False
            for buf in buffers:
                if buf.is_busy:
                    are_full_buffer = True
                    break
            end = not are_full_buffer and not are_working_dev

    sources_numbers = []
    devices_numbers = []
    amount_generated_requests = []
    probability_declining = []
    average_system_time = []
    average_waiting_time = []
    average_processing_time = []
    waiting_dispersion = []
    processing_dispersion = []

    for src in sources:
        sources_numbers.append(int(src.number))
        amount_generated_requests.append(src.count_request)
        if src.count_request != 0:
            probability_declining.append(1.0 - src.processed_requests / src.count_request)
            average_system_time.append((sum(src.processing_time) + sum(src.waiting_time)) / src.count_request)
        else:
            probability_declining.append(0.0)
            average_system_time.append(0.0)

        if len(src.waiting_time) != 0:
            average_waiting_time.append(sum(src.waiting_time) / len(src.waiting_time))
            waiting_dispersion.append(
                sum([(xi - average_waiting_time[src.number - 1]) ** 2 for xi in src.waiting_time]) / len(
                    src.waiting_time))
        else:
            average_waiting_time.append(0.0)
            waiting_dispersion.append(0.0)

        if len(src.processing_time) != 0:
            average_processing_time.append(sum(src.processing_time) / len(src.processing_time))
            processing_dispersion.append(sum([(xi - average_processing_time[src.number - 1]) ** 2 for xi in src.processing_time]) \
                                    / len(src.processing_time))
        else:
            average_processing_time.append(0)
            processing_dispersion.append(0)

    devices_coefficients = []
    for dev in devices:
        devices_numbers.append(dev.number)
        devices_coefficients.append(dev.busy_time / system_time)

    return amount_generated_requests,\
        probability_declining,\
        average_system_time,\
        average_waiting_time,\
        average_processing_time,\
        waiting_dispersion,\
        processing_dispersion,\
        devices_coefficients,\
        sources_numbers,\
        devices_numbers


def step_init(n_s, n_b, n_d, alpha, beta, lambda_param):
    devices.clear()
    sources.clear()
    buffers.clear()
    global dict
    dict = {}

    device_pointer = CirclePointer(n_d)
    buffer_pointer = CirclePointer(n_b)

    for i in range(n_s):
        temp_source = source.Source(i + 1, alpha, beta)
        sources.append(temp_source)
    for i in range(n_b):
        temp_buffer = buffer.Buffer(i + 1)
        buffers.append(temp_buffer)
    for i in range(n_d):
        temp_device = device.Device(i + 1, lambda_param)
        devices.append(temp_device)

    first_request_time = sys.float_info.max
    for src in sources:
        tmp = src.next_generation()
        if  tmp < first_request_time:
            first_request_time = tmp
    system_time = first_request_time
    return system_time, device_pointer, buffer_pointer


def step_application(number_of_requests, system_time, generated_requests, dev_pointer, buf_pointer):
    global device_pointer, buffer_pointer
    device_pointer, buffer_pointer = dev_pointer, buf_pointer

    global dict

    processed_requests = 0
    end = False

    if len(dict) > 0:
        tmp_dict = {}
        for key, value in dict.items():
            if key != str(system_time) and dict[key][1] != 'src' or float(key) < system_time:
                tmp_dict[key] = dict[key]

        dict = tmp_dict

    requests = []
    for src in sources:
        if src.next_generation() == system_time and generated_requests < number_of_requests:
            requests.append(src.generate())
            generated_requests += 1
            dict[str(system_time)] = [str(requests[-1].source_number) + '.' + str(requests[-1].number), 'src']

    processed_requests += free_device_step(system_time)
    handle_buffered_requests_step(system_time)
    for req in requests:
        handle_request_step(req, system_time)

    next_time = sys.float_info.max
    if generated_requests < number_of_requests:
        for src in sources:
            if next_time > src.next_generation() > -1.0:
                next_time = src.next_generation()

    i, min_tmp = get_first_in_devices()
    if -1.0 < min_tmp < next_time:
        next_time = min_tmp

    if next_time < sys.float_info.max:
        system_time = next_time

    if generated_requests == number_of_requests:
        are_working_dev = False
        for dev in devices:
            if dev.is_busy:
                are_working_dev = True
                break
        are_full_buffer = False
        for buf in buffers:
            if buf.is_busy:
                are_full_buffer = True
                break
        end = not are_full_buffer and not are_working_dev

    return end, system_time, generated_requests, device_pointer, buffer_pointer