import pygame

from handlers.base_event_handler import BaseEventHandler


class JoystickEventHandler(BaseEventHandler):
    VERTICAL_AXIS = 1
    HORIZONTAL_AXIS = 0
    UP = -1
    DOWN = 1
    LEFT = -1
    RIGHT = 1
    STOP = 0

    def __init__(self, tarent_jumper):
        BaseEventHandler.__init__(self, tarent_jumper)
        self.__joysticks = []

        for player in self._tarent_jumper.get_players():
            self.__joysticks.append(player.get_joystick())

    def can_handle(self, event):
        return event.type == pygame.JOYAXISMOTION

    def handle_event(self, event):
        if event.type == pygame.JOYAXISMOTION:
            self.__handle_axis_motion(event)

    def __handle_axis_motion(self, event):
        if event.axis > JoystickEventHandler.VERTICAL_AXIS:
            return

        player = self.__player_for_event(event)

        if player is None:
            return

        if event.axis == JoystickEventHandler.VERTICAL_AXIS:
            self.__handle_vertical_axis_motion(event, player)
        elif event.axis == JoystickEventHandler.HORIZONTAL_AXIS:
            self.__handle_horizontal_axis_motion(event, player)

    def __player_for_event(self, event):
        player = None

        for i in range(len(self.__joysticks)):
            if self.__joysticks[i] is not None and self.__joysticks[i].get_id() == event.joy:
                player = self._tarent_jumper.get_players()[i]
                break

        return player

    def __handle_vertical_axis_motion(self, event, player):
        if self.__round_event_value(event) == JoystickEventHandler.UP:
            player.set_ready()
            player.jump()

    def __handle_horizontal_axis_motion(self, event, player):
        event_value = self.__round_event_value(event)

        if event_value == JoystickEventHandler.LEFT:
            player.move_left()
        elif event_value == JoystickEventHandler.RIGHT:
            player.move_right()
        elif event_value == JoystickEventHandler.STOP:
            player.stop()

    def __round_event_value(self, event):
        return round(event.value, 0)