from src.user_interface import UserInterface
from src.sim import ARTSS
from utils.states import State, Event, TRANSITION_TABLE 
from utils.login import check_key

ui = UserInterface()
sim = ARTSS()
current_state = State.MAIN_MENU
ui.transition_state(current_state)

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
