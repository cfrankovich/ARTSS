import time
import os


class ARTSSClock():
    time = 0 

    def tick():
        ARTSSClock.time += 1


class Logger():
    def __init__(self):
        unix_time = int(time.time()) 
        dir = f"artss-logs/sim-{unix_time}"
        self.flight_dir = f"{dir}/flights"
        os.makedirs(dir, exist_ok=True)
        os.makedirs(self.flight_dir, exist_ok=True)
        self.atc_log_file = open(dir + "/atc.log", "a") 
        self.flight_log_files = {}

    def log_atc_com(self, com):
        self.atc_log_file.write(f"[{ARTSSClock.time}] {com}\n")

    def log_flight_com(self, flight_num, com):
        dir = f"{self.flight_dir}/{flight_num}.log" 
        if not os.path.exists(dir):
            new_flight_log_file = open(dir, "a") 
            self.flight_log_files[flight_num] = new_flight_log_file 
        self.flight_log_files[flight_num].write(f"[{ARTSSClock.time}] {com}\n")

    def close_flight_log(self, flight_num):
        self.flight_log_files[flight_num].close()
        del self.flight_log_files[flight_num]

    def close(self):
        for flight_num, flight_log_file in self.flight_log_files.items():
            flight_log_file.close()
            del self.flight_log_files[flight_num]
        self.atc_log_file.close()


logger = Logger()
