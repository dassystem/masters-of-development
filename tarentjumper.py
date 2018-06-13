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
        self.display_surface = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption("tarent Jumper")
        
        self.background_color = pygame.Color(50, 60, 200)
        
        self.clock = pygame.time.Clock()
        self.fps = fps
        
        self.fill_blocks()

        # TODO: vorsicht bei width = 0 und/oder height = 0 (fullscreen)
        half_width = width // 2
        player_1_rect = pygame.Rect(0, 0, half_width, height)
        player_2_rect = pygame.Rect(half_width, 0, half_width, height)
        player_1_surface = self.display_surface.subsurface(player_1_rect)
        player_2_surface = self.display_surface.subsurface(player_2_rect)
        self.player_1 = Player(1, player_1_surface, "dev1.png", self.blocks, 1)
        self.player_2 = Player(2, player_2_surface, "dev2.png", self.blocks, 1)
                
        self.level = Block(50, 50)

    def fill_blocks(self):
        self.blocks = []

        for y in range(0, len(level1)):
            prev_line_block = None
            for x in range(0, len(level1[y])):
                if (level1[y][x] == 1):
                    new_x = x * 32
                    new_y = y * 32
                    new_width = 32
                    new_height = 32
                    
                    if prev_line_block:
                        if prev_line_block.rect.x / 32 == x - 1:
                            self.blocks.pop()
                            new_x = prev_line_block.rect.x
                            new_y = prev_line_block.rect.y
                            new_width = prev_line_block.rect.width + 32
                            new_height = 32
                    
                    new_block = Block(new_x, new_y, new_width, new_height)
                    self.blocks.append(new_block)
                    prev_line_block = new_block

    def run(self):
        """The mainloop
        """
        running = True

        while running:
            self.display_surface.fill(self.background_color)
            
            for block in self.blocks:
                block.render(self.display_surface)
            
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_w:
                        self.player_1.jump()
                    elif event.key == pygame.K_a:
                        self.player_1.move_left()
                    elif event.key == pygame.K_d:
                        self.player_1.move_right()
                    elif event.key == pygame.K_RIGHT:
                        self.player_2.move_right()
                    elif event.key == pygame.K_LEFT:
                        self.player_2.move_left()
                    elif event.key == pygame.K_UP:
                        self.player_2.jump()

            self.player_1.update()
            self.player_2.update()
            
            self.clock.tick(self.fps)
            pygame.display.flip()
       
        pygame.quit()

if __name__ == "__main__":
    TarentJumper(800, 600).run()
