class BaseEventHandler:
    def __init__(self, tarent_jumper):
        self._tarent_jumper = tarent_jumper

    def can_handle(self, event):
        return False

    def handle_event(self, event):
        pass