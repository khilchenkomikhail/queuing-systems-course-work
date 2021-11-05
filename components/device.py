import math
import random

class Device:

    def __init__(self, number, lambda_param):
        self.number = number
        self.request = None
        self.time_request_out = 0
        self.lambda_param = lambda_param
        self.end_time = -1
        self.is_busy = False
        self.busy_time = 0.0

    def get_end_of_processing_time(self):
        return self.end_time

    def set_request(self, request, system_time):
        self.request = request
        request.set_device()
        self.time_request_in = system_time
        self.is_busy = True
        self.end_time = self.time_request_in + math.log(1 - random.random()) / (- self.lambda_param)
        self.request.processing_time = self.end_time - self.time_request_in
        self.busy_time += self.end_time - self.time_request_in

    def delete_request(self):
        if self.request is not None:
            self.time_request_out = self.end_time
            self.request.processed()
            self.request = None
        self.is_busy = False
