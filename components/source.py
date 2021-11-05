import random

class Request:

    def __init__(self, generation_time, number, source_number):
        self.generation_time = generation_time
        self.number = number
        self.source_number = source_number
        self._is_in_buffer = False
        self._is_in_device = False
        self._is_in_refusal = False

        self.buffering_start_time = 0.0
        self.buffering_end_time = 0.0
        self.processing_time = 0.0


    def refuse(self):
        self.is_in_refusal = True
        self.buffering_time = self.buffering_end_time - self.buffering_start_time

    def set_buffer(self):
        self.is_in_buffer = True

    def set_device(self):
        self.is_in_buffer = False
        self.is_in_device = True

    def processed(self):
        self._is_in_buffer = False
        self._is_in_device = False
        self._is_in_refusal = False


class Source:

    def __init__(self, number, alpha, beta):
        self.number = number
        self.alpha = alpha
        self.beta = beta
        self.prev_time = 0.0
        self.time_next_generation = -1.0
        self.__is_generated = False


        self.count_request = 0
        self.processed_requests = 0
        self.processing_time = []
        self.waiting_time = []


    def next_generation(self):
        if not self.__is_generated:
            self.time_next_generation = self.prev_time + (self.beta - self.alpha)\
                                        * random.random() + self.alpha
            self.__is_generated = True
        return self.time_next_generation

    def generate(self):

        self.count_request += 1

        request = Request(self.time_next_generation, self.count_request, self.number)

        self.__is_generated = False

        self.prev_time = self.time_next_generation

        return request
