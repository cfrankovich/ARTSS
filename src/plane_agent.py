import pygame
import math
from utils.flight_data_handler import generate_flight_data, FlightStatus 
from utils.coms import CommunicationType 

AIRPORT = "DAB"
DEPARTURE_FREQUENCY = "125.800 MHz"

class Plane(pygame.sprite.Sprite):
    def __init__(self, color, height, width):
       super().__init__() 
       self.color = color
       self.image = pygame.Surface([width, height])
       self.image.fill(color)
       self.image = pygame.image.load("graphics/plane.png")
       self.rect = self.image.get_rect() 
       self.rect.x = 800
       self.rect.y = 400
       self.flight_data = generate_flight_data() 

    def get_status(self):
        return self.flight_data["status"]

    def receieve_com(self, atc, com):
        fn = self.flight_data["flight_number"]
        ct = com[1]
        if ct == CommunicationType.TAXI_CLEARANCE:
            runway_number = ""
            taxiways = ""
            self.send_com(atc, (f"Taxi to runway {runway_number}, via taxiways {taxiways}, hold short of runway {runway_number}, {fn}.", CommunicationType.READ_BACK))
        elif ct == CommunicationType.LINE_UP:
            runway_number = ""
            self.send_com(atc, (f"Runway {runway_number}, lining up and waiting, {fn}.", CommunicationType.LINE_UP))
        elif ct == CommunicationType.TAKEOFF_CLEARANCE:
            runway_number = ""
            self.send_com(atc, (f"Runway {runway_number}, cleared for takeoff, {fn}.", CommunicationType.CONFIRM_TAKEOFF_CLEARANCE))

    def send_com(self, atc, com=None):
        if com is not None:
            atc.receieve_com(com, self)
            return
        fn = self.flight_data["flight_number"]
        status = self.flight_data["status"]
        com = ("", CommunicationType.NONE)
        if status == FlightStatus.READY_FOR_PUSHBACK:
            com = (f"{AIRPORT} Ground, {fn}, at gate {self.flight_data["gate"]}, ready for pushback.", CommunicationType.PUSHBACK_CLEARANCE)
        elif status == FlightStatus.WAITING_FOR_TAXI_CLEARANCE:
            com = (f"{AIRPORT} Ground, {fn}, ready to taxi.", CommunicationType.TAXI_CLEARANCE)
        elif status == FlightStatus.HOLDING_SHORT:
            com = (f"Holding short of runway {self.flight_data["runway"]}, {fn}.", CommunicationType.HOLDING_SHORT) 
        elif status == FlightStatus.AIRBORNE:
            com = (f"{fn}, passing {self.flight_data["altitude"]}, climbing to {self.flight_data["desired_altitude"]}.", CommunicationType.DEPARTURE)
        atc.receieve_com(com, self)

    def update_pos(self):
        pass

    def move(self, dx, dy):

        self.rect.x += dx
        self.rect.y += dy
      
        rot_plane = self.rot_center(self.image, self.rot_direction(dx, dy))
        return rot_plane
    
    def rot_direction(self, dx, dy):
        new_angle = 0
        if (dy < 0 and dx > 0):      
            new_angle = 0 + (math.atan(dy/dx) * 180 / math.pi)
        elif (dy < 0 and dx < 0):
            new_angle = 0 + (math.atan(dy/dx) * 180 / math.pi)
        elif(dy > 0 and dx > 0):       
            new_angle = -90 - (math.atan(dy/dx) * 180 / math.pi)
        elif(dy > 0 and dx < 0):
            new_angle = 180 + (math.atan(dy/dx) * 180 / math.pi)
        return new_angle
    
    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image
       
        