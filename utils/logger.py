import time
import os


class ARTSSClock():
    TICKS_PER_MINUTE = 1
    start_time = "0000" 
    ticks = 0 
    Running = False
    
    def tick():
        if ARTSSClock.Running:
            ARTSSClock.ticks += 1

    def get_fancy_time():
        tick_minutes = ARTSSClock.ticks / ARTSSClock.TICKS_PER_MINUTE 
        minutes = int(ARTSSClock.start_time[2:]) + tick_minutes
        hours = (int(ARTSSClock.start_time[:2]) + (minutes // 60)) % 24 
        minutes = int(minutes % 60)
        str_mins = f"0{minutes}" if minutes < 10 else f"{minutes}"
        return f"{int(hours)}:{str_mins}" 

    def setRunning(status):
        ARTSSClock.Running = status

class Logger():
    last_atc_message = ""
    last_flight_message = ""
    def __init__(self):
        unix_time = int(time.time()) 
        dir = f"artss-logs/sim-{unix_time}"
        self.flight_dir = f"{dir}/flights"
        os.makedirs(dir, exist_ok=True)
        os.makedirs(self.flight_dir, exist_ok=True)
        self.atc_log_file = open(dir + "/atc.log", "a") 
        self.flight_log_files = {}

    def log_atc_com(self, com):
        self.atc_log_file.write(f"[{ARTSSClock.get_fancy_time()}] {com}\n")
        Logger.last_atc_message = f"[{ARTSSClock.get_fancy_time()}] {com}"
    
    def log_flight_com(self, flight_num, com):
        dir = f"{self.flight_dir}/{flight_num}.log" 
        if not os.path.exists(dir):
            new_flight_log_file = open(dir, "a") 
            self.flight_log_files[flight_num] = new_flight_log_file 
        self.flight_log_files[flight_num].write(f"[{ARTSSClock.get_fancy_time()}] {com}\n")
        Logger.last_flight_message = f"[{ARTSSClock.get_fancy_time()}] {com}"

    def close_flight_log(self, flight_num):
        self.flight_log_files[flight_num].close()
        del self.flight_log_files[flight_num]

    def close(self):
        for flight_num, flight_log_file in self.flight_log_files.items():
            flight_log_file.close()
            del self.flight_log_files[flight_num]
        self.atc_log_file.close()


logger = Logger()
