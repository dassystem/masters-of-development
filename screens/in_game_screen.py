from screens.base import BaseScreen, BaseScreenEventHandler
from utils import Utils
import pygame
import random
import masters_of_development
from block import Block
import utils.timer
import numpy as np

class InGameScreen(BaseScreen):
    def __init__(self, surface, fonts, sounds, images, players, joysticks, seconds = 100):
        super(InGameScreen, self).__init__(
            surface,
            [InGameScreenJoystickEventHandler(self, players, joysticks)])
        
        self.__fonts = fonts
        self.__images = images
        
        self.__players = players
        
        self.__play_areas = []
        self.__init_play_areas(fonts, sounds, images)
        
        super().add_event_handler(InGameScreenKeyboardEventHandler(self, self.__play_areas))
        
        timer = utils.timer.FontSpriteTimer(
            "ingame",
            seconds,
            {"center": (960, 77)},
            fonts["big"],
            masters_of_development.MastersOfDevelopment.GREEN,
            masters_of_development.MastersOfDevelopment.RED,
            sounds,
            10)
             
        self.__timer = pygame.sprite.GroupSingle(timer)
        
        super().add_event_handler(InGameScreenTimerElapsedEventHandler(self, self.get_timer()))

        self.__init_redraw_areas()

    def __init_play_areas(self, fonts, sounds, images):
        split_screen = []
        player_1_rect = images["in_game_screen_play_area_bg"].get_rect(topleft = (55, 85))
        split_screen.append(self._surface.subsurface(player_1_rect))
        
        player_2_rect = images["in_game_screen_play_area_bg"].get_rect(topleft = (1015, 85))
        split_screen.append(self._surface.subsurface(player_2_rect))
        
        for i, subsurface in enumerate(split_screen):
            # pass a copy of the surface rect to the player so that the player can't mess up with the surface
            self.__players[i].set_surface_rect(subsurface.get_rect().copy())
            self.__play_areas.append(InGameScreenPlayArea(self, subsurface, fonts, sounds, images, self.__players[i]))
    
    def __init_redraw_areas(self):
        self.__redraw_areas = {}

        self.__redraw_areas["timer_1"] = (self.__images["in_game_screen_bg"].subsurface((870, 85, 35, 40)), (870, 85))        
        self.__redraw_areas["timer_2"] = (self.__images["in_game_screen_bg"].subsurface((1015, 85, 35, 40)), (1015, 85)) 
        self.__redraw_areas["head_1"] = (self.__images["in_game_screen_bg"].subsurface((400, 795, 155, 25)), (400, 795))
        self.__redraw_areas["head_2"] = (self.__images["in_game_screen_bg"].subsurface((1360, 800, 120, 20)), (1360, 800))

    def render(self):
        if not self.is_active():
            return
        
        self._surface.blit(self.__images["in_game_screen_bg"], (0, 0))

        for play_area in self.__play_areas:
            play_area.update()
        
        self.__redraw()
            
        all_dead = True

        for player in self.__players:
            all_dead = all_dead and player.is_dead()
            
        if self.all_dead() and self.get_timer().is_started():
            self.get_timer().stop()
            
        self.__render_timer()

    def __redraw(self):
        for redraw_area in self.__redraw_areas.values():
            self._surface.blit(redraw_area[0], redraw_area[1])

    def all_dead(self):
        all_dead = True

        for player in self.__players:
            all_dead = all_dead and player.is_dead()
        
        return all_dead

    def __render_timer(self):
        self.__timer.update()
        self.__timer.draw(self._surface)

    def set_active(self, active):
        super().set_active(active)
        
        if self.is_active():
            self.add_event_handler(self.get_timer().get_event_handler())
            self.get_timer().start()
            
            for play_area in self.__play_areas:
                play_area.reset()
        else:
            self.get_timer().stop()
            self.remove_event_handler(self.get_timer().get_event_handler())

    def get_player_surfaces(self):
        return self.__player_surfaces

    def get_players(self):
        return self.__players

    def get_timer(self):
        """Get the timer out of the sprite group."""
        return self.__timer.sprite
    
class InGameScreenPlayArea(object):
    """A area where a player is playing."""
    
    def __init__(self, screen, surface, fonts, sounds, images, player):
        self.__screen = screen
        self.__surface = surface
        self.__fonts = fonts
        self.__sounds = sounds
        self.__images = images
        self.__player = pygame.sprite.GroupSingle(player)
        self.__blocks = pygame.sprite.Group()
        self.__block_items = pygame.sprite.Group()
        
        self.__text = self.__fonts["big"].render(
            "PLAYER {0:d}: ".format(self.get_player().get_number()), True, masters_of_development.MastersOfDevelopment.GREEN)
        self.__score = pygame.sprite.GroupSingle(Score(fonts["big"], sounds["score"]))
        
        self.__debug_info = pygame.sprite.GroupSingle(DebugInfo(self, fonts))
        self.__scroll_velocity = 8
        self.__level = 0
        
    def reset(self):
        """Resets the state of the play area so that it can be (re-) used for a new game.
        
           Resets the player and generates new blocks.
        """
        self.__level = 0

        self.__player.sprite.reset()
        self.__blocks.empty()
        self.__block_items.empty()
        self.__generate_blocks()
        self.__score.sprite.reset()
        
        self.__player.sprite.set_on_block(self.__blocks.sprites()[0])
        self.__player.sprite.rect.centerx = (self.__surface.get_rect().centerx)
        
        self.__ending_sound_played = False
    
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
            
            r = random.randint(0, 10)
            
            if r == 1:
                coin = Coin(self.__images, new_block)
                self.__block_items.add(coin)
            elif r == 2:
                power_up = PowerUpJump(self.__images, new_block, self)
                self.__block_items.add(power_up)
            elif r == 3:
                bug = Bug(self.__images, new_block)
                self.__block_items.add(bug)
            elif r == 4:
                power_up = PowerUpBugResistant(self.__images, new_block, self)
                self.__block_items.add(power_up)
            
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
        
        background = self.__images["in_game_screen_play_area_bg"]
        self.__surface.blit(background, (0, 0))
        
        self.__scroll_screen()
        # generate new blocks after scrolling if necessary
        self.__generate_blocks()
        
        self.__player.update()
        
        self.__surface.blit(self.__text, self.__text.get_rect(topright = (self.__surface.get_width() // 2, 5)))
        
        self.__score.update(self.__surface)
        self.__debug_info.update()

        self.__detect_block_collision()
        self.__detect_block_item_collision()

        self.__blocks.draw(self.__surface)
        self.__block_items.draw(self.__surface)
        self.__player.draw(self.__surface)
        self.__score.draw(self.__surface)
        
        if self.__debug_info.sprite.is_visible():
            self.__debug_info.draw(self.__surface)

    def __detect_block_collision(self):
        collided_blocks = pygame.sprite.spritecollide(self.get_player(), self.__blocks, False, detect_player_block_collide)
       
        for block in collided_blocks:
            block.on_collide(self.get_player(), self.get_score())
       
    def __detect_block_item_collision(self):
        collided_items = pygame.sprite.spritecollide(self.get_player(), self.__block_items, True)
        
        for collided_item in collided_items:
            collided_item.on_collide(self.get_player(), self.get_score())

    def __render_game_over(self):
        bg = None
        text = None
        
        if self.get_screen().all_dead():
            other_player = None
            score_color = None
            
            if self.get_player().get_number() == 1:
                other_player = self.get_screen().get_players()[1]
            else:
                other_player = self.get_screen().get_players()[0]
            
            if self.get_player().get_score() > other_player.get_score():
                bg = self.__images["in_game_screen_win_bg"]
                score_color = masters_of_development.MastersOfDevelopment.GREEN
                
                if not self.__ending_sound_played:
                    self.__sounds["player{0:d}wins".format(self.get_player().get_number())].play()
                    self.__ending_sound_played = True
            elif self.get_player().get_score() < other_player.get_score():
                bg = self.__images["in_game_screen_loose_bg"]
                score_color = masters_of_development.MastersOfDevelopment.RED
            else:
                # draw
                bg = self.__images["in_game_screen_win_bg"]
                score_color = masters_of_development.MastersOfDevelopment.GREEN
                self.__ending_sound_played = True
                
            text = self.__fonts["big"].render(str(self.get_player().get_score()), True, score_color)
        else:
            bg = self.__images["in_game_screen_game_over_bg"]
            
        self.__surface.blit(bg, (0, 0))
    
        if text is not None:
            self.__surface.blit(text, text.get_rect(center = (426, 604)))
    
    def __scroll_screen(self):
        player_rect = self.__player.sprite.rect
        
        if player_rect.top <= self.__surface.get_height() // 2:
            player_rect.y += self.__scroll_velocity
            
            self.__blocks.update(self.__scroll_velocity, self.__surface.get_height())
            self.__block_items.update()
            
    def get_player(self):
        return self.__player.sprite
    
    def get_score(self):
        return self.__score.sprite
    
    def get_screen(self):
        return self.__screen
    
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
        self.__play_area = play_area
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
                      
        debug_info = "falling: {0:s} jumping: {1:s} jump_height: {2:2d}".format(
            str(player.is_falling()), str(player.is_jumping()), player.get_jump_height())
        
        debug_surfaces.append(self.__render_debug_info(debug_info))

        debug_info = "speed: {0:d} velocity: {1:d}".format(
            player.get_speed(), player.get_velocity())
        
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
        self.image.fill(masters_of_development.MastersOfDevelopment.BACKGROUND_COLOR)
        self.rect = self.image.get_rect(top = self.__play_area.get_score().rect.bottom)
        
        if self.__play_area.get_player().get_number() == 1:
            self.rect.left = 0
        else:
            self.rect.right = self.__play_area.get_surface().get_width() - 1
        
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
    
    def __init__(self, font, sound):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Score, self).__init__()
        self.__font = font
        self.__sound = sound
        self.__score = 0
        self.__dirty = True

    def reset(self):
        self.__score = 0
        self.__dirty = True
        
    def update(self, target_surface):
        """Updates the score display. Does nothing if score hasn't changed..
           See also https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.update
        """
        if not self.__dirty:
            return
        
        self.image = self.__font.render("{0:d}".format(self.__score), True, masters_of_development.MastersOfDevelopment.WHITE)

        self.rect = self.image.get_rect(topleft = (target_surface.get_width() // 2, 5))
        
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

class Item(pygame.sprite.Sprite):
    def __init__(self, block):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Item, self).__init__()
        self.__block = block
        
        self.rect = self.image.get_rect()
        self.rect.bottom = self.__block.rect.top
        
        r = random.randint(0, 3)
        
        if r == 1:
            self.rect.left = self.__block.rect.left
        elif r == 2:
            self.rect.midbottom = self.__block.rect.midtop
        else:
            self.rect.right = self.__block.rect.right
        
        self.__block.add_item(self)
        
    def update(self):
        # items scroll with their block, get killed by their block
        self.rect = self.image.get_rect(bottom = self.__block.rect.top, x = self.rect.x)

    def on_collide(self, player, score):
        pass

class Coin(Item):
    """A sprite representing a collectable extra score item."""
    
    def __init__(self, images, block, base_score = 100):
        r = random.randint(0, 70)
        
        if r <= 10:
            self.image = images["gem1"]
        elif r <= 20:
            self.image = images["gem2"]
        elif r <= 30:
            self.image = images["gem3"]
        elif r <= 40:
            self.image = images["gem4"]
        elif r <= 50:
            self.image = images["gem5"]
        elif r <= 60:
            self.image = images["gem6"]
        elif r <= 70:
            self.image = images["gem7"]

        self.__score = (r // 10 + 1) * base_score

        # IMPORTANT: call the parent class (Sprite) constructor
        super(Coin, self).__init__(block)
    
    def get_score(self):
        return self.__score
    
    def on_collide(self, player, score):
        score.add_score(self.get_score())
        player.set_score(score.get_score())

class PowerUp(Item):
    def __init__(self, name, block, play_area, active_seconds = 5):
        self.__name = name
        self.__play_area = play_area
        self.__active_seconds = active_seconds

        # IMPORTANT: call the parent class (Sprite) constructor
        super(PowerUp, self).__init__(block)

    def get_name(self):
        return self.__name

    def get_timer(self):
        return self.__timer

    def on_collide(self, player, score):
        player.add_power_up(self)
        
        self.__timer = utils.timer.Timer("powerup", self.__active_seconds)
        
        self.__event_handlers = []
        self.__event_handlers.append(self.__timer.get_event_handler())
        self.__event_handlers.append(PowerupTimerElapsedEventHandler(self.__play_area.get_screen(), self))
        
        for event_handler in self.__event_handlers:
            self.__play_area.get_screen().add_event_handler(event_handler)
        
        self.__timer.start()
        
    def deactivate(self):
        self.__play_area.get_player().remove_power_up(self)
        self.__timer.stop()
        self.__timer = None
        
        for event_handler in self.__event_handlers:
            self.__play_area.get_screen().remove_event_handler(event_handler)
        
        self.__event_handlers = []

class PowerUpJump(PowerUp):
    def __init__(self, images, block, play_area):
        self.image = images["power_up_jump_height"]
        super(PowerUpJump, self).__init__("power_up_jump", block, play_area)

class PowerUpBugResistant(PowerUp):
    def __init__(self, images, block, play_area):
        self.image = images["power_up_bug_resistant"]
        super(PowerUpBugResistant, self).__init__("power_up_bug_resistant", block, play_area)

class Bug(Item):
    def __init__(self, images, block, base_score = -100):
        self.image = images["bug"]
        self.__score = (random.randint(0, 70) // 10 + 1) * base_score
        
        super(Bug, self).__init__(block)

    def get_score(self):
        return self.__score

    def on_collide(self, player, score):
        power_ups = player.get_power_ups()
        
        if "power_up_bug_resistant" in power_ups:
            bug_resistant = power_ups["power_up_bug_resistant"]
            
            if len(bug_resistant) > 0:
                return
        
        score.add_score(self.get_score())
        player.set_score(score.get_score())
        
class PowerupTimerElapsedEventHandler(BaseScreenEventHandler):
    def __init__(self, in_game_screen, power_up):
        super(PowerupTimerElapsedEventHandler, self).__init__(in_game_screen)
        self.__power_up = power_up
        
    def can_handle(self, event):
        if not super().can_handle(event):
            return False
        
        return event.type == utils.timer.ELAPSED_EVENT and event.timer == self.__power_up.get_timer()
    
    def handle_event(self, event):
        self.__power_up.deactivate()

class InGameScreenKeyboardEventHandler(BaseScreenEventHandler):
    def __init__(self, in_game_screen, play_areas):
        super(InGameScreenKeyboardEventHandler, self).__init__(in_game_screen)
        self.__play_areas = play_areas

    def can_handle(self, event):
        if not super().can_handle(event):
            return False
        
        return event.type == pygame.KEYDOWN or event.type == pygame.KEYUP

    def handle_event(self, event):
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
        elif event.key == pygame.K_RETURN:
            if self.get_screen().all_dead() or not self.get_screen().get_timer().is_started():
                self.get_screen().set_active(False)

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
        if self.get_screen().all_dead() or not self.get_screen().get_timer().is_started():
            self.get_screen().set_active(False)
        else:
            player = Utils.get_player_from_joystick_event(event, self.__joysticks, self.__players)
    
            if player is None:
                return
    
            player.jump()

class InGameScreenTimerElapsedEventHandler(BaseScreenEventHandler):
    def __init__(self, in_game_screen, timer):
        super(InGameScreenTimerElapsedEventHandler, self).__init__(in_game_screen)
        self.__timer = timer

    def can_handle(self, event):
        if not super().can_handle(event):
            return False

        return event.type == utils.timer.ELAPSED_EVENT and event.timer == self.__timer

    def handle_event(self, event):
        for player in self.get_screen().get_players():
            player.set_dead()
