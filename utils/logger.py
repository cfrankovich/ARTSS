import time
import os


class Logger():
    def __init__(self, sim_clock):
        unix_time = int(time.time()) 
        dir = f"artss-logs/sim-{unix_time}"
        self.flight_dir = f"{dir}/flights"
        os.makedirs(dir, exist_ok=True)
        os.makedirs(self.flight_dir, exist_ok=True)
        self.atc_log_file = open(dir + "atc.log", "a") 
        self.sim_clock = sim_clock
        self.flight_log_files = {}

    def log_atc_com(self, com):
        self.atc_log_file.write(f"[{self.sim_clock.get_time()}] {com}")

    def log_flight_com(self, flight_num, com):
        dir = f"{self.flight_dir}/{flight_num}.log" 
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=True)
            new_flight_log_file = open(dir, "a") 
            self.flight_log_files[flight_num] = new_flight_log_file 
        self.flight_log_files[flight_num].write(f"[{self.sim_clock.get_time()}] {com}")

    def close_flight_log(self, flight_num):
        self.flight_log_files[flight_num].close()
        del self.flight_log_files[flight_num]

    def close(self):
        for flight_num, flight_log_file in self.flight_log_files.items():
            flight_log_file.close()
            del self.flight_log_files[flight_num]
        self.atc_log_file.close()
