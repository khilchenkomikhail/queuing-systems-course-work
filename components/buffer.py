class Buffer:

    def __init__(self, number):
        self.number = number
        self.busy_time = 0
        self.is_busy = False
        self.request = None

    def add_request(self, request, system_time):
        self.request = request
        self.time_requset_in = system_time
        request.set_buffer()
        self.is_busy = True

    def get_request_generation_time(self):
        if self.request is None:
            return -1
        return self.request.generation_time

    def get_request(self, system_time):
        self.time_requset_out = system_time
        self.busy_time += self.time_requset_out - self.time_requset_in
        res = self.request
        self.request = None
        self.is_busy = False
        return res
