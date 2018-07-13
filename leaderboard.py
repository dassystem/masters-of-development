import masters_of_development
import pygame
import utils.db_connector

LETTER_GAP = 30
MAX_ENTRIES = 5

class Leaderboard(object):
    def __init__(self):
        self.__db_connector = utils.db_connector.DbConnector("assets/leaderboard.db")
        self.__db_connector.connect()
        
        self.__init_board()
        
    def __init_board(self):
        c = self.__db_connector.get_cursor()
        
        self.__board = []
                
        for row in c.execute("SELECT id, name, score FROM leaderboard ORDER BY score DESC"):
            self.__board.append(LeaderboardEntry(row[0], row[1], row[2]))
    
    def get_count(self):
        return len(self.__board)
    
    def get_entries(self):
        return tuple(self.__board)
    
    def add_entry(self, player_info):
        self.__db_connector.execute_with_parameter("INSERT INTO leaderboard (name, score) VALUES (?,?)", player_info)
        self.__db_connector.commit()
        pk = self.__db_connector.get_cursor().lastrowid
        self.__board.append(LeaderboardEntry(pk, player_info[0], player_info[1]))
        self.__board.sort(key = lambda entry: entry.get_score(), reverse = True)
    
class LeaderboardEntry(object):
    def __init__(self, identity, name, score):
        self.__id = identity
        self.__name = name
        self.__score = score
        
    def get_id(self):
        return self.__id
    
    def get_name(self):
        return self.__name
        
    def get_score(self):
        return self.__score

class Cursor(pygame.sprite.Sprite):
    def __init__(self, player, leaderboard, initial_x, initial_y, initial_width):
        # IMPORTANT: call the parent class (Sprite) constructor
        super(Cursor, self).__init__()
        
        self.image = pygame.Surface((initial_width, 3))
        self.image.fill(masters_of_development.MastersOfDevelopment.BLACK)
        # https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Group.draw demands an attribute rect
        self.rect = self.image.get_rect(x = 0, y = 0)
        
        self.symbol = ""
        self.__initial_x = initial_x
        self.__initial_y = initial_y
        
        self.rect.x = initial_x
        self.rect.y = initial_y
        
        self.__x_start_limit = 0
        self.__x_end_limit = 0
        self.__y_end_limit = 0
        self.__y_start_limit = 0
        self.__name = []
        self.__namelimit = 6
        self.__active = True
        self.__player = player
        self.__leaderboard = leaderboard

    def reset(self):
        self.rect.x = self.__initial_x
        self.rect.y = self.__initial_y
        self.symbol = ""
        self.__name = []        

    def __save(self):
        if self.__active == False:
            return

        self.__active = False
        player_info = (''.join(self.__name), self.__player.get_score())
        self.__player.set_player_name(''.join(self.__name))
        
        self.__leaderboard.add_entry(player_info)

    def move_cursor_right(self):
        if self.__active == False:
            return
        if self.rect.x < self.__x_end_limit:
            self.rect.x += LETTER_GAP

    def move_cursor_left(self):
        if self.__active == False:
            return
        if self.rect.x > self.__x_start_limit:
            self.rect.x -= LETTER_GAP

    def move_cursor_up(self):
        if self.__active == False:
            return
        if self.rect.y - LETTER_GAP > self.__y_start_limit:
            self.rect.y -= LETTER_GAP

    def move_cursor_down(self):
        if self.__active == False:
            return
        if self.rect.y < self.__y_end_limit:
            self.rect.y += LETTER_GAP

    def set_vertical_limit(self, starty, endy):
        self.__y_start_limit = starty
        self.__y_end_limit = endy

    def set_horizontal_limit(self, startx, endx):
        self.__x_start_limit = startx
        self.__x_end_limit = endx

    def set_selected(self, symbol):
        if self.__active == False:
            return
        self.symbol = symbol

    def enter_letter(self):
        if self.__active == False:
            return

        if self.symbol == "→":
            self.__save()
            return

        if self.symbol == "←":
            self.delete_letter()
            return

        if len(self.__name) < self.__namelimit:
            self.__name.append(self.symbol)

    def delete_letter(self):
        if self.__active == False:
            return
        if len(self.__name) > 0:
            self.__name.remove(self.__name[len(self.__name) - 1])

    def get_name(self):
        return self.__name

    def get_active_status(self):
        return self.__active
    
    def set_active(self, active):
        self.__active = active

        if self.__active:
            self.image.fill(masters_of_development.MastersOfDevelopment.BLACK)
        else:
            self.image.fill(masters_of_development.MastersOfDevelopment.WHITE)
