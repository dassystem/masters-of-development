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
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
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
        
        # TODO: vorsicht bei width = 0 und/oder height = 0 (fullscreen)
        half_width = width // 2
        player_1_rect = pygame.Rect(0, 0, half_width, height)
        player_2_rect = pygame.Rect(half_width, 0, half_width, height)
        player_1_surface = self.display_surface.subsurface(player_1_rect)
        player_2_surface = self.display_surface.subsurface(player_2_rect)
        self.player_1 = Player(player_1_surface, 0, 400, "dev1.png")
        self.player_2 = Player(player_2_surface, 0, 400, "dev2.png")
        
        self.fill_blocks()
        
        self.level = Block(50, 50)
        self.gravity = -1

    def fill_blocks(self):
        self.blocks = []

        for y in range(0, len(level1)):
            for x in range(0, len(level1[y])):
                if (level1[y][x] == 1):
                    self.blocks.append(Block(x * 32, y * 32))

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

            self.player_1.update(self.gravity, self.blocks)
            self.player_1.render()
            
            self.player_2.update(self.gravity, self.blocks)
            self.player_2.render()
            
            self.clock.tick(self.fps)
            pygame.display.flip()
       
        pygame.quit()

if __name__ == "__main__":
    TarentJumper(800, 600).run()
