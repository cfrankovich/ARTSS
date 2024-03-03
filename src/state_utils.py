from enum import Enum

class State(Enum):
    QUIT = 1
    MAIN_MENU = 2
    SETTINGS = 3
    LOGIN = 4
    FULLSCREEN = 5

class Event(Enum):
    GOTO_MAIN_MENU = 1
    GOTO_SETTINGS = 2
    QUIT = 3
    NONE = 4
    GOTO_LOGIN = 5
    TOGGLE_FULLSCREEN = 6

TRANSITION_TABLE = {
    # <event type>: <state to transition to>
    Event.GOTO_MAIN_MENU: State.MAIN_MENU,
    Event.GOTO_SETTINGS: State.SETTINGS,
    Event.QUIT: State.QUIT,
    Event.NONE: None,
    Event.GOTO_LOGIN: State.LOGIN,
    Event.TOGGLE_FULLSCREEN: State.FULLSCREEN,
}
