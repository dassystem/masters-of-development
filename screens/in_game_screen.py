from screens.base import BaseScreen, BaseScreenEventHandler
from utils import Utils
import pygame
import random
import masters_of_development
from block import Block
from utils.timer import Timer

class InGameScreen(BaseScreen):
    def __init__(self, surface, fonts, sounds, players, joysticks, seconds = 100):
        super(InGameScreen, self).__init__(
            surface,
            [InGameScreenJoystickEventHandler(self, players, joysticks),
             InGameScreenTimerElapsedEventHandler(self)])
        
        self.__font = fonts["small"]
        
        self.__players = players
        
        self.__play_areas = []
        self.__init_play_areas(fonts, sounds)
        
        super()._add_event_handler(InGameScreenKeyboardEventHandler(self, self.__play_areas))
             
        self.__timer = Timer(seconds)

    def __init_play_areas(self, fonts, sounds):
        split_screen = Utils.split_screen(self._surface)
        
        for i, surface in enumerate(split_screen):
            # pass a copy of the surface rect to the player so that the player can't mess up with the surface
            self.__players[i].set_surface_rect(surface.get_rect().copy())
            self.__play_areas.append(InGameScreenPlayArea(surface, fonts, sounds, self.__players[i]))

    def render(self):
        if not self.is_active():
            return
        
        self._surface.fill(masters_of_development.MastersOfDevelopment.BACKGROUND_COLOR)

        for play_area in self.__play_areas:
            play_area.update()
            
        all_dead = True

        for player in self.__players:
            all_dead = all_dead and player.is_dead()
            
        if all_dead:
            self.set_active(False)
            
        self.__render_timer()

    def __render_timer(self):
        text_surface_1 = self.__font.render("Time", True, masters_of_development.MastersOfDevelopment.TARENT_RED)
        text_rect_1 = Utils.center(text_surface_1, self._surface)
        self._surface.blit(text_surface_1, text_rect_1)

        text_surface_2 = self.__font.render(
            "{0:d}s".format(self.__timer.get_seconds_left()), True , masters_of_development.MastersOfDevelopment.TARENT_RED)
        text_rect_2 = Utils.center(text_surface_2, self._surface)
        text_rect_2.move_ip(0, text_rect_1.height)
        self._surface.blit(text_surface_2, text_rect_2)

    def set_active(self, active):
        super().set_active(active)
        
        if self.is_active():
            self._add_event_handler(self.__timer.get_event_handler())
            self.__timer.start()
            
            for play_area in self.__play_areas:
                play_area.reset()
        else:
            self.__timer.stop()
            self._remove_event_handler(self.__timer.get_event_handler())

    def get_player_surfaces(self):
        return self.__player_surfaces

class InGameScreenPlayArea(object):
    """A area where a player is playing."""
    
    def __init__(self, surface, fonts, sounds, player):
        self.__surface = surface
        self.__fonts = fonts
        self.__player = pygame.sprite.GroupSingle(player)
        self.__blocks = pygame.sprite.Group()
        self.__score = pygame.sprite.GroupSingle(Score((0, 0), fonts["small"], sounds["score"]))
        self.__debug_info = pygame.sprite.GroupSingle(DebugInfo(player, fonts))
        self.__scroll_velocity = 8
        self.__level = 0
        
    def reset(self):
        """Resets the state of the play area so that it can be (re-) used for a new game.
        
           Resets the player and generates new blocks.
        """
        self.__player.sprite.reset()
        self.__blocks.empty()
        self.__generate_blocks()
        self.__score.sprite.reset()
        
        self.__player.sprite.set_on_block(self.__blocks.sprites()[0])
        self.__player.sprite.rect.centerx = (self.__surface.get_rect().centerx)
        
        self.__level = 0
    
    def __generate_blocks(self):
        if len(self.__blocks) == 0:
            self.__generate_base_block()
        
        # only generate as much new blocks as needed
        while len(self.__blocks) < 13:
            self.__level += 1
            ygaps = random.randrange(50, 100)
            xgaps = random.randrange(100, 150)
            block_width = random.randrange(80, 160)
            last_block = self.__blocks.sprites()[-1]

            last_block_top = last_block.rect.top
            random_y_position = last_block_top - ygaps
            random_x_position = last_block.rect.centerx

            # random if the platform spawns left or right to last one
            if random.randint(0,1) == 1:
                random_x_position += xgaps
            else:
                random_x_position -=  xgaps

            new_block = Block(self.__level,
                      random_x_position,
                      random_y_position,
                      block_width,
                      Block.BLOCK_HEIGHT)
            # make sure that the block is not out of screen bounds
            while new_block.rect.right > self.__surface.get_rect().right:
                new_block.rect.right -= xgaps

            while new_block.rect.left < self.__surface.get_rect().left:
                new_block.rect.right += xgaps

            self.__blocks.add(new_block)

    def __generate_base_block(self):
        baseBlock = Block(
            0,
            self.__surface.get_rect().x,
            self.__surface.get_height() - Block.BLOCK_HEIGHT,
            self.__surface.get_width(), Block.BLOCK_HEIGHT
        )
        
        self.__blocks.add(baseBlock) 
    
    def switch_debug(self):
        """Switches the debug information on/off."""
        self.__debug_info.sprite.switch_visibility()
      
    def update(self):
        """Updates all sprites and draws them on the play area. Scrolls if necessary.
           see also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        
        if self.get_player().is_dead():
            self.__render_game_over()
            return
        
        self.__scroll_screen()
        # generate new blocks after scrolling if necessary
        self.__generate_blocks()
        
        self.__player.update()
        self.__score.update()
        self.__debug_info.update()

        collideted_blocks = pygame.sprite.spritecollide(self.get_player(), self.__blocks, False, detect_player_block_collide)
       
        if len(collideted_blocks) > 0:
            uplevel = self.get_player().set_on_block(collideted_blocks[0])
            
            if uplevel > 0:
                self.__score.sprite.add_platform_score(uplevel)
                self.get_player().set_score(self.__score.sprite.get_score())
        
        self.__blocks.draw(self.__surface)
        self.__player.draw(self.__surface)
        self.__score.draw(self.__surface)
        
        if self.__debug_info.sprite.is_visible():
            self.__debug_info.draw(self.__surface)
        
    def __render_game_over(self):
        font_surface = self.__fonts["big"].render("GAME OVER", True, (255, 0, 0))
        font_rect = font_surface.get_rect()
        font_rect.x = self.__surface.get_rect().centerx - font_surface.get_width() // 2
        font_rect.y = self.__surface.get_rect().centery - font_surface.get_height() // 2
        
        self.__surface.blit(font_surface, font_rect)
    
    def __scroll_screen(self):
        player_rect = self.__player.sprite.rect
        
        if player_rect.top <= self.__surface.get_height() // 2:
            player_rect.y += self.__scroll_velocity
            
            self.__blocks.update(self.__scroll_velocity, self.__surface.get_height())

    def get_player(self):
        return self.__player.sprite
    
    def get_surface(self):
        return self.__surface

def detect_player_block_collide(player, block):
    if player.rect.colliderect(block.rect):
        falled_on = player.is_falling() and player.rect.bottom >= block.rect.top and player.rect.bottom <= block.rect.centery
        jumped_on = player.is_jumping() and player.rect.bottom == block.rect.top
        
        if falled_on or jumped_on:
            return True
    
    return False

class DebugInfo(pygame.sprite.Sprite):
    """A sprite representing an area with some debug infos. Toggled by pressing i."""
    def __init__(self, play_area, fonts):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(DebugInfo, self).__init__()
        self._play_area = play_area
        self.__visible = False

        self.__font = fonts["micro"]
        self.__color = pygame.Color(0, 255, 0)    
        
    def update(self):
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
                      
        debug_info = "falling: {0:s} jumping: {1:s}".format(
            str(player.is_falling()), str(player.is_jumping()))
        
        debug_surfaces.append(self.__render_debug_info(debug_info))

        debug_info = "speed: {0:d} velocity: {1:d}".format(
            self.player.get_speed(), self.player.get_velocity())
        
        debug_surfaces.append(self.__render_debug_info(debug_info))
        
        debug_info = "screen width {0:d} height {0:d}".format(
            self.__play_area.get_surface().get_width(), self.__play_area.get_surface().get_height())
        
        debug_surfaces.append(self.__render_debug_info(debug_info))
        
        joystick = self.player.get_joystick()
        
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
        
        self.image = pygame.Surface(max_width, height * len(debug_surfaces))
        
        for i, debug_surface in enumerate(debug_surfaces):
            self.image.blit(debug_surface, (0, i * height))

    def __render_debug_info(self, debug_info):
        return self.__font.render(debug_info, False, self.__color)
    
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

class Score(pygame.sprite.Sprite):
    """A sprite representing the score display."""
    PLATFORM_LEVEL_SCORE = 100
    
    def __init__(self, pos, font, sound):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Score, self).__init__()
        self.__font = font
        self.__sound = sound
        self.rect = pygame.Rect(pos, (1, 1))
        self.__score = 0
        self.__dirty = True

    def reset(self):
        self.__score = 0
        self.__dirty = True
        
    def update(self):
        """Updates the score display. Does nothing if score hasn't changed..
           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        if not self.__dirty:
            return
        
        height = self.__font.get_height()
        text_surfaces = []
        
        for txt in ("SCORE", "{0:d}".format(self.__score)):
            text_surfaces.append(self.__font.render(txt, True, masters_of_development.MastersOfDevelopment.BLACK))
        
        width = max(txt_surface.get_width() for txt_surface in text_surfaces)
        
        self.image = pygame.Surface((width, height * len(text_surfaces)), pygame.SRCALPHA)
        
        for y, txt_surface in enumerate(text_surfaces):
            self.image.blit(txt_surface, (0, y * height))
        
        self.rect = self.image.get_rect(topleft = self.rect.topleft)
        
        self.__dirty = False
    
    def add_platform_score(self, uplevel):
        """Adds a score for achiving a higher block."""
        self.add_score(uplevel * Score.PLATFORM_LEVEL_SCORE)
        
    def add_score(self, score):
        """Adds a score."""
        self.__score += score
        self.__dirty = True
        self.__sound.play()
    
    def get_score(self):
        """Gets the current score (number)."""
        return self.__score

class InGameScreenKeyboardEventHandler(BaseScreenEventHandler):
    def __init__(self, in_game_screen, play_areas):
        super(InGameScreenKeyboardEventHandler, self).__init__(in_game_screen)
        self.__play_areas = play_areas

    def can_handle(self, event):
        if not super().can_handle(event):
            return False
        
        return event.type == pygame.KEYDOWN or event.type == pygame.KEYUP

    def handle_event(self, event):
        if not self.can_handle(event):
            return
        
        if event.type == pygame.KEYDOWN:
            self.__handle_keydown_event(event)
        elif event.type == pygame.KEYUP:
            self.__handle_keyup_event(event)

    def __handle_keydown_event(self, event):
        if event.key == pygame.K_w:
            self.__play_areas[0].get_player().jump()
        elif event.key == pygame.K_a:
            self.__play_areas[0].get_player().move_left()
        elif event.key == pygame.K_d:
            self.__play_areas[0].get_player().move_right()
        elif event.key == pygame.K_RIGHT:
            self.__play_areas[1].get_player().move_right()
        elif event.key == pygame.K_LEFT:
            self.__play_areas[1].get_player().move_left()
        elif event.key == pygame.K_UP:
            self.__play_areas[1].get_player().jump()
        elif event.key == pygame.K_i:
            for play_area in self.__play_areas:
                play_area.switch_debug()

    def __handle_keyup_event(self, event):
        if event.key == pygame.K_a or event.key == pygame.K_d:
            self.__play_areas[0].get_player().stop()
        elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            self.__play_areas[1].get_player().stop()

class InGameScreenJoystickEventHandler(BaseScreenEventHandler):
    VERTICAL_AXIS = 1
    HORIZONTAL_AXIS = 0
    UP = -1
    DOWN = 1
    LEFT = -1
    RIGHT = 1
    STOP = 0

    def __init__(self, in_game_screen, players, joysticks):
        super(InGameScreenJoystickEventHandler, self).__init__(in_game_screen)
        self.__players = players
        self.__joysticks = joysticks

    def can_handle(self, event):
        if not super().can_handle(event):
            return False
        
        return event.type == pygame.JOYAXISMOTION or event.type == pygame.JOYBUTTONDOWN

    def handle_event(self, event):
        if not self.can_handle(event):
            return
        
        if event.type == pygame.JOYAXISMOTION:
            self.__handle_axis_motion(event)
        elif event.type == pygame.JOYBUTTONDOWN:
            self.__handle_button_down(event)

    def __handle_axis_motion(self, event):
        if event.axis > InGameScreenJoystickEventHandler.VERTICAL_AXIS:
            return

        player = Utils.get_player_from_joystick_event(event, self.__joysticks, self.__players)

        if player is None:
            return

        if event.axis == InGameScreenJoystickEventHandler.VERTICAL_AXIS:
            self.__handle_vertical_axis_motion(event, player)
        elif event.axis == InGameScreenJoystickEventHandler.HORIZONTAL_AXIS:
            self.__handle_horizontal_axis_motion(event, player)

    def __handle_vertical_axis_motion(self, event, player):
        if self.__round_event_value(event) == InGameScreenJoystickEventHandler.UP:
            player.jump()

    def __handle_horizontal_axis_motion(self, event, player):
        event_value = self.__round_event_value(event)

        if event_value == InGameScreenJoystickEventHandler.LEFT:
            player.move_left()
        elif event_value == InGameScreenJoystickEventHandler.RIGHT:
            player.move_right()
        elif event_value == InGameScreenJoystickEventHandler.STOP:
            player.stop()

    def __round_event_value(self, event):
        return round(event.value, 0)

    def __handle_button_down(self, event):
        player = Utils.get_player_from_joystick_event(event, self.__joysticks, self.__players)

        if player is None:
            return

        player.jump()

class InGameScreenTimerElapsedEventHandler(BaseScreenEventHandler):
    def __init__(self, in_game_screen):
        super(InGameScreenTimerElapsedEventHandler, self).__init__(in_game_screen)

    def can_handle(self, event):
        if not super().can_handle(event):
            return False

        return event.type == Timer.ELASPED_EVENT

    def handle_event(self, event):
        if not self.can_handle(event):
            return

        if event.type == Timer.ELASPED_EVENT:
            self.get_screen().set_active(False)
