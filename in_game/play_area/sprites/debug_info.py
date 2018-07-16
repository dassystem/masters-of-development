import pygame

from colors import BACKGROUND_COLOR

class DebugInfo(pygame.sprite.Sprite):
    """A sprite representing an area with some debug infos. Toggled by pressing i."""
    def __init__(self, play_area, fonts):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(DebugInfo, self).__init__()
        self.__play_area = play_area
        self.__visible = False

        self.__font = fonts["micro"]
        self.__color = pygame.Color(0, 255, 0)    
        
    def update(self, seconds):
        """Updates the debug info. Does nothing if not visible.
           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        if not self.__visible:
            return
        
        player = self.__play_area.get_player()
        
        debug_surfaces = []
        
        player_rect = player.rect
        
        debug_info = "player left {0:3d} right {1:3d} top {2:3d} bottom {3:3d}".format(
            player_rect.left, player_rect.right, player_rect.top, player_rect.bottom)
        
        debug_surfaces.append(self.__render_debug_info(debug_info))
                      
        debug_info = "falling: {0:s} jumping: {1:s} jump_height: {2:2d}".format(
            str(player.is_falling()), str(player.is_jumping()), player.get_jump_height())
        
        debug_surfaces.append(self.__render_debug_info(debug_info))

        debug_info = "speed: {0:d} velocity: {1:d} seconds/frame: {2:f}".format(
            player.get_speed(), player.get_velocity(), seconds)
        
        debug_surfaces.append(self.__render_debug_info(debug_info))
        
        debug_info = "screen width {0:d} height {0:d}".format(
            self.__play_area.get_surface().get_width(), self.__play_area.get_surface().get_height())
        
        debug_surfaces.append(self.__render_debug_info(debug_info))
        
        joystick = player.get_joystick()
        
        if joystick != None:
            debug_info = "joystick: {0:s} {1:s}".format(
                str(joystick.get_id()), self.__remove_whitespace(joystick.get_name()))
        
            debug_surfaces.append(self.__render_debug_info(debug_info, 0, 64))
            
        max_width = 0
        height = 0    
            
        for debug_surface in debug_surfaces:
            if max_width < debug_surface.get_width():
                max_width = debug_surface.get_width()
                 
            if height == 0:
                height = debug_surface.get_height()
        
        self.image = pygame.Surface((max_width, height * len(debug_surfaces)))
        self.image.fill(BACKGROUND_COLOR)
        self.rect = self.image.get_rect(top = self.__play_area.get_score().rect.bottom)
        
        if self.__play_area.get_player().get_number() == 1:
            self.rect.left = 0
        else:
            self.rect.right = self.__play_area.get_surface().get_width() - 1
        
        for i, debug_surface in enumerate(debug_surfaces):
            self.image.blit(debug_surface, (0, i * height))

    def __remove_whitespace(self, name):
        """Remove unneccessary whitespaces (for the joystick name)."""
        whitespaces = 0
        new_name = ""
        
        for char in name:
            if char.isspace():
                whitespaces += 1
            else:
                whitespaces = 0
            
            if whitespaces <= 1:
                new_name += char

        return new_name
    
    def switch_visibility(self):
        """Switches debug info visibility on/off."""
        self.__visible = not self.__visible
        
    def is_visible(self):
        """Checks if the debug info is visible."""
        return self.__visible
