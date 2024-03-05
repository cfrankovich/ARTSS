from utils.coms import CommunicationType 


def get_plane_from_com(com):
    return None


class Agent():
    def __init__(self):
        pass

    def send_com(self, plane, com):
        plane.receive_com(com)

    def receive_com(self, com):
        plane = get_plane_from_com(com)
        com_to_send = self.check_request(plane, com) 
        self.send_com(plane, com_to_send)

    # Return command to send back to plane based on the checks
    def check_request(self, plane, com):
        return ("", CommunicationType.NONE) 
