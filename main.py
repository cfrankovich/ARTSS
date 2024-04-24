from src.user_interface import UserInterface
from src.sim import ARTSS
from utils.states import State, Event, TRANSITION_TABLE 
from utils.login import check_key
from utils.map_handler import load_map
from utils.logger import ARTSSClock

load_map()
ui = UserInterface()
sim = ARTSS()
ARTSSClock.start_time = "1530" # 3:30pm
current_state = State.SIMULATION
ui.transition_state(current_state)

# # # BEGIN DEBUGGING # # #

from src.plane_agent import Plane, plane_queue
from utils.flight_data_handler import FlightStatus
from utils.coms import CommunicationType


a = Plane(FlightStatus.DEBUG, 39, 16)
plane_queue.append(a)
com = (f"Airport Ground, debug, ready to taxi.", CommunicationType.TAXI_CLEARANCE)
sim.atc_agent.receive_com(com, a)

plane_queue.append(Plane(FlightStatus.CRUISING, 0, 0))

# # #  END DEBUGGING  # # #

while current_state != State.QUIT:
    sim_event = sim.tick()
    ui.render()

    ui_event = ui.event_handler()
    try: 
        current_state = TRANSITION_TABLE[ui_event] 
        ui.transition_state(current_state)
    except:
        pass

    if ui_event == Event.CHECK_KEY:
        if check_key(ui.current_ui.key_input_text):
            ui.transition_state(State.SIMULATION)
        else:
            ui.current_ui.key_input_text = ''
