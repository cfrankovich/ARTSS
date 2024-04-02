"""
PUSHBACK CLEARANCE
    Pilot: "[Airport] Ground, [Flight Number], at gate [Number], ready for pushback, with information [Alpha]."
    ATC: "[Flight Number], [Airport] Ground, cleared for pushback and engine start, advise ready to taxi."
TAXI CLEARANCE
    Pilot: "[Airport] Ground, [Flight Number], ready to taxi."
    ATC: "[Flight Number], taxi to runway [Number], via taxiways [Name], [Name], hold short of runway [Number]."
READ BACK
    Pilot: "Taxi to runway [Number], via taxiways [Name], [Name], hold short of runway [Number], [Flight Number]."
HOLDING SHORT
    Pilot: "Holding short of runway [Number], [Flight Number]."
LINE UP
    ATC: "[Flight Number], runway [Number], line up and wait."
    Pilot: "Runway [Number], lining up and waiting, [Flight Number]."
TAKEOFF CLEARANCE
    ATC: "[Flight Number], runway [Number], cleared for takeoff, wind [Direction] at [Speed]."
    Pilot: "Runway [Number], cleared for takeoff, [Flight Number]."
DEPARTURE
    Pilot: "[Departure Frequency], [Flight Number], passing [Altitude], climbing to [Assigned Altitude]."
    ATC: "[Flight Number], radar contact, climb to [Altitude], proceed on course."

INITIAL CONTACT WITH APPROACH CONTROL
    Pilot: "[Approach Control], [Flight Number], with you, [Altitude] descending to [Assigned Altitude], with information [Alpha]."
    ATC: "[Flight Number], [Approach Control], radar contact, descend to [Altitude], expect ILS approach runway [Number]."
HOLD:
    ATC: "[Flight Number], [Approach Control], due to [reason for hold, e.g., traffic congestion, runway unavailability], hold at [Hold Fix Name or Navaid] on the [specified radial, course, or bearing], maintain [Altitude], expect further clearance at [Time or Condition]."
APPROACH CLEARANCE
    ATC: "[Flight Number], proceed direct to [Fix], descend and maintain [Altitude], expect vector for ILS approach runway [Number]."
    Pilot: "Direct to [Fix], descending to [Altitude], expecting vector for ILS approach runway [Number], [Flight Number]."
    ATC: "[Flight Number], you are [Distance] miles from [Fix], turn [Direction], maintain [Altitude] until established on the localizer, cleared ILS approach runway [Number]."
    Pilot: "Cleared ILS approach runway [Number], maintain [Altitude] until established, [Flight Number]."
TRANSFER TO TOWER
    ATC (Approach Control): "[Flight Number], contact [Airport] Tower on [Frequency]."
    Pilot: "[Frequency], [Flight Number], switching, thank you."
INITIAL CONTACT WITH TOWER
    Pilot: "[Airport] Tower, [Flight Number], on the ILS, runway [Number]."
    ATC (Tower): "[Flight Number], [Airport] Tower, continue approach, number [Position in line], expect landing clearance at [Distance/Marker]."
LANDING CLEARANCE
    ATC (Tower): "[Flight Number], runway [Number], wind [Direction] at [Speed], cleared to land."
    Pilot: "Runway [Number], cleared to land, [Flight Number]."
AFTER LANDING
    Pilot: "[Airport] Tower, [Flight Number], runway vacated at taxiway [Name]."
    ATC (Ground): "[Flight Number], [Airport] Ground, taxi to gate [Number], via taxiways [Name], [Name]."
    Pilot: "Taxi to gate [Number], via taxiways [Name], [Name], [Flight Number]."
AT THE GATE
    Pilot: "[Airport] Ground, [Flight Number], at gate [Number], shutting down."
    ATC (Ground): "[Flight Number], roger, good day."
"""
from enum import Enum

class CommunicationType(Enum):
    NONE = 0 
    PUSHBACK_CLEARANCE = 1
    TAXI_CLEARANCE = 2
    READ_BACK = 3
    HOLDING_SHORT = 4
    LINE_UP = 5
    TAKEOFF_CLEARANCE = 6
    DEPARTURE = 7
    INITIAL_CONTACT = 8 
    APPROACH_CLEARANCE = 9
    TRANSFER_TO_TOWER = 10
    INITIAL_CONTACT_WITH_TOWER = 11
    LANDING_CLEARANCE = 12
    AFTER_LANDING = 13
    AT_THE_GATE = 14
    CONFIRM_TAKEOFF_CLEARANCE = 15
    pass
