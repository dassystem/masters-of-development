from handlers.base_event_handler import BaseEventHandler
from handlers.joystick_event_handler import JoystickEventHandler
from handlers.keyboard_event_handler import KeyboardEventHandler
from handlers.quit_event_handler import QuitEventHandler


class EventHandler(BaseEventHandler):
    def __init__(self, tarent_jumper):
        BaseEventHandler.__init__(self, tarent_jumper)
        self.__handlers = []
        self.__handlers.append(QuitEventHandler(self._tarent_jumper))
        self.__handlers.append(KeyboardEventHandler(self._tarent_jumper))
        self.__handlers.append(JoystickEventHandler(self._tarent_jumper))

    def handle_event(self, event):
        handler = None

        for h in self.__handlers:
            if h.can_handle(event):
                handler = h
                break

        if handler is not None:
            handler.handle_event(event)