from screens.base import BaseScreen, BaseScreenEventHandler
import tarentjumper
from utils import Utils
from utils.timer import Timer

class CountdownScreen(BaseScreen):
    def __init__(self, surface, font, seconds = 5):
        BaseScreen.__init__(self, surface, [CountdownScreenEventHandler(self)])
        self.__font = font
        self.__seconds = seconds
        self.__timer = Timer(seconds)
        
        self._add_event_handler(self.__timer.get_event_handler())
        
    def set_active(self, active):
        BaseScreen.set_active(self, active)
        
        if self.is_active():
            self.__start_timer()
        else:
            self.__stop_timer()
    
    def __start_timer(self):
        self.__timer.start()

    def __stop_timer(self):
        self.__timer.stop()
        self._remove_event_handler(self.__timer.get_event_handler())
    
    def countdown(self):
        self.__timer.countdown()
    
    def render(self):
        if not self.is_active():
            return
        
        self._surface.fill(tarentjumper.TarentJumper.BACKGROUND_COLOR)

        countdown_txt = self.__font.render("Games starts in", True, tarentjumper.TarentJumper.BLACK)
        countdown_txt_rect = Utils.center(countdown_txt, self._surface)
        self._surface.blit(countdown_txt, countdown_txt_rect)

        time_txt = self.__font.render(str(self.__timer.get_seconds_left()), True, tarentjumper.TarentJumper.BLACK)
        time_txt_rect = Utils.center(time_txt, self._surface)
        time_txt_rect.move_ip(0, 200)
        
        self._surface.blit(time_txt, time_txt_rect)

class CountdownScreenEventHandler(BaseScreenEventHandler):
    def __init__(self, count_down_screen):
        BaseScreenEventHandler.__init__(self, count_down_screen)
    
    def can_handle(self, event):
        if not BaseScreenEventHandler.can_handle(self, event):
            return False
        
        return event.type == Timer.ELASPED_EVENT
    
    def handle_event(self, event):
        if not self.can_handle(event):
            return
        
        if event.type == Timer.ELASPED_EVENT:
            self.get_screen().set_active(False)
