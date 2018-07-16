import pygame

VERTICAL_AXIS = 1
HORIZONTAL_AXIS = 0
UP = -1
DOWN = 1
LEFT = -1
RIGHT = 1
STOP = 0

def init_joysticks():
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    
    for joystick in joysticks:
        joystick.init()
        
    return joysticks

def round_event_value(event):
    return round(event.value)

def is_motion(event):
    return event.type == pygame.JOYAXISMOTION

def is_vertical_motion(event):
    return is_motion(event) and event.axis == VERTICAL_AXIS

def is_horizontal_motion(event):
    return is_motion(event) and event.axis == HORIZONTAL_AXIS

def is_up(event):
    return is_vertical_motion(event) and round_event_value(event) == UP

def is_down(event):
    return is_vertical_motion(event) and round_event_value(event) == DOWN

def is_left(event):
    return is_horizontal_motion(event) and round_event_value(event) == LEFT

def is_right(event):
    return is_horizontal_motion(event) and round_event_value(event) == RIGHT

def is_horizontal_stop(event):
    return is_horizontal_motion(event) and round_event_value(event) == STOP

def is_button_down(event):
    return event.type == pygame.JOYBUTTONDOWN

def get_id(event):
    return event.id
