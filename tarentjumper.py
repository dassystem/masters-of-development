import pygame
from player import Player
from block import Block

level1 = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0],
    [0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0],
    [0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
    [0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0],
    [0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,0,0]
]

class TarentJumper:
    # width and height = 0 -> current screen resolution
    def __init__(self, width = 0, height = 0, flags = 0, fps = 30):
        """Initialie pygame, window, background, ...
        """
        pygame.init()
        
        # pygame.HWSURFACE only for fullscreen...
        self.__display = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption("tarent Jumper")
        
        self.__background_color = pygame.Color(50, 60, 200)
        
        self.__clock = pygame.time.Clock()
        self.__fps = fps
        
        self.__fill_blocks()
        self.__init_players()
                
        self.level = Block(50, 50)

    def __fill_blocks(self):
        self.__blocks = []

        for y in range(0, len(level1)):
            prev_line_block = None
            for x in range(0, len(level1[y])):
                if (level1[y][x] == 1):
                    new_x = x * 32
                    new_y = y * 32
                    new_width = 32
                    new_height = 32
                    
                    if prev_line_block:
                        if prev_line_block.get_rect().x / 32 == x - 1:
                            self.__blocks.pop()
                            new_x = prev_line_block.get_rect().x
                            new_y = prev_line_block.get_rect().y
                            new_width = prev_line_block.get_rect().width + 32
                            new_height = 32
                    
                    new_block = Block(new_x, new_y, new_width, new_height)
                    self.__blocks.append(new_block)
                    prev_line_block = new_block

    def __init_players(self):
        # TODO: vorsicht bei width = 0 und/oder height = 0 (fullscreen)
        half_width = self.__display.get_width() // 2
        height = self.__display.get_height()

        self.__player_1 = self.__init_player(1, 0, half_width, height, "dev1.png")
        self.__player_2 = self.__init_player(2, half_width, half_width, height, "dev2.png")

    def __init_player(self, number, screen_x, screen_width, screen_height, image_file_name):
        player_rect = pygame.Rect(screen_x, 0, screen_width, screen_height)
        player_surface = self.__display.subsurface(player_rect)
        
        return Player(number, player_surface, image_file_name, self.__blocks, 1)

    def run(self):
        """The mainloop
        """
        running = True

        while running:
            self.__display.fill(self.__background_color)
            
            for block in self.__blocks:
                block.render(self.__display)
            
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_w:
                        self.__player_1.jump()
                    elif event.key == pygame.K_a:
                        self.__player_1.move_left()
                    elif event.key == pygame.K_d:
                        self.__player_1.move_right()
                    elif event.key == pygame.K_RIGHT:
                        self.__player_2.move_right()
                    elif event.key == pygame.K_LEFT:
                        self.__player_2.move_left()
                    elif event.key == pygame.K_UP:
                        self.__player_2.jump()
                    elif event.key == pygame.K_i:
                        self.__player_1.switch_debug()
                        self.__player_2.switch_debug()

            self.__player_1.update()
            self.__player_2.update()
            
            self.__clock.tick(self.__fps)
            pygame.display.flip()
       
        pygame.quit()

if __name__ == "__main__":
    TarentJumper(800, 600).run()
