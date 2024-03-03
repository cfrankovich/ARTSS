from src.user_interface import UserInterface
from src.sim import ARTSS
from src.state_utils import State, TRANSITION_TABLE 

ui = UserInterface(900, 600)
sim = ARTSS()
current_state = State.MAIN_MENU
ui.transition_state(current_state)

while current_state != State.QUIT:
    sim_event = sim.tick()
    ui.render()

    ui_event = ui.event_handler()
    if TRANSITION_TABLE[ui_event] != None: 
        current_state = TRANSITION_TABLE[ui_event] 
        ui.transition_state(current_state)
