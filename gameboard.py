#!/usr/bin/env python

from numpy import tile, sqrt, ndarray # type: ignore
from numpy.random import choice, randint # type: ignore
from sys import stdout
from typing import Dict, List, Tuple, Union, Optional, Set
from functools import reduce

DIM = 3
UNIT = 5

Dungeon = Dict[int, ndarray]

################
## MAIN UTILS ##
################
def write(x: str):
    ''' writes to stdout '''
    if x=='@':
        x = "\033[1;34m" + x + "\x1b[0m"
    if x=='#':
        x = "\033[1;31m" + x + '\x1b[0m'
    return stdout.write(x)

def update(x: str, pos: Tuple[int, int], mp: ndarray):
    mp[pos[0]-1, pos[1]] = x
    pass

def print_map(row: List[str]):
    ''' '''
    for x in row:
        yield write(x)


###############
## gameboard ##
###############
class GameBoard:
    def __init__(self,
                 dim: int,
                 unit: int):
        self.DIM: int = dim
        self.UNIT: int = unit
        self.HEIGHT: int = self.DIM * self.UNIT
        self.WIDTH: int = 2 * self.HEIGHT
        self.NUM_ROOMS: int = (self.HEIGHT // self.UNIT) * (self.WIDTH // (2 * self.UNIT))
        self.UNNOISED: Set[int] = set()

        self.dungeon: Dungeon = {k: self.mk_room() for k in range(self.NUM_ROOMS)}

    ## ROOMS ##
    def mk_room(self) -> ndarray:
        '''empty room with walls and doors'''
        UNIT = self.UNIT
        # build background
        res = tile(' ', (self.UNIT, 2*self.UNIT))

        # build walls
        res[0] = ['#'] * 2*self.UNIT
        res[-1] = ['#'] * 2*self.UNIT
        res[:, 0] = ['#'] * self.UNIT
        res[:, -1] = ['#'] * self.UNIT

        # build doors
        res[0, 2*self.UNIT // 2] = '^'
        res[-1, 2*self.UNIT // 2] = '^'
        res[self.UNIT // 2, 0] = '^'
        res[self.UNIT // 2, -1] = '^'

        return res


    def shuffle_ids(self):
        ''' assigns/shuffles story ids to rooms. 
        
            ids A thru H signify that i've written/prepped 8 rooms. 

            Should come after '@' reset to origin in a butterfly reset
        '''
        if self.init_room_id==' ': 
            self.init_room_id = choice([x for x in "ABCDEFGH"], 1)[0]
        
        stories = choice([x for x in "ABCDEFGH"], 9)

        for num, room in self.dungeon.items():
            if '#' in self.dungeon[num][1,2*self.UNIT-self.UNIT//4]:
                continue
            elif '@' in self.dungeon[num][self.UNIT//2+1, self.UNIT//2+2]: 
                self.dungeon[num][2, 2*self.UNIT - 3] = self.init_room_id 
            else:
                self.dungeon[num][2, 2*self.UNIT - 3] = stories[num]
        pass

    def mark_num(self):
        ''' marks what number for easier navigating'''
        for num, room in self.dungeon.items():
            self.dungeon[num][1,1] = num
        pass

    def init_party(self) -> int:
        ''' places party in random room
        
            records (and returns) init_room var in state
        '''

        self.init_room_num: int = randint(len(self.dungeon))

        if self.dungeon[self.init_room_num][self.UNIT//2+1, self.UNIT//2+2] =='#':
            #room_num: int = randint(len(rooms))
            return self.init_party()
        else:
            self.dungeon[self.init_room_num][self.UNIT//2+1, self.UNIT//2+2] = '@'

        self.UNNOISED.add(self.init_room_num)
        return self.init_room_num

    def fill_with_rocks(self):
        ''' fills a random room w rocks'''
        room_num: int = randint(len(self.dungeon))

        for k in range(1, self.UNIT-1):
            self.dungeon[room_num][k] = ['#'] * 2*self.UNIT
        return room_num

    def mv_party(self, frm: int, to: Union[str, int]) -> int:
        ''' moves party to selected room '''

        def DIRECTIONS(x: Union[str, int]) -> int:
            ''' cylindrical. N/S loops E/W doesn't.  '''
            if x=='N':
                return (frm-self.DIM)%9
            elif x=='W':
                if frm in [self.DIM*k for k in range(self.DIM*self.DIM)]:
                    return frm
                else:
                    return frm-1
            elif x=='E':
                if frm in [self.DIM*k - 1 for k in range(1, self.DIM*self.DIM)]:
                    return frm
                else:
                    return frm+1
            elif x=='S':
                return (frm+self.DIM)%self.NUM_ROOMS
            else: 
                return int(x) 

        try:
            assert '@' in self.dungeon[frm][self.UNIT//2+1, self.UNIT//2+2], "frm parameter incorrect"
        except AssertionError as e:
            print(e)
        if to in ('N', 'W', 'E', 'S'):
            to = int(DIRECTIONS(to))

        if self.dungeon[int(to)][self.UNIT//2+1, self.UNIT//2+2] == '#':
            self.UNNOISED.add(int(to))
            to = frm
        else:
            self.dungeon[frm][self.UNIT//2+1, self.UNIT//2+2] = ' '
            self.dungeon[int(to)][self.UNIT//2+1, self.UNIT//2+2] = '@'

        self.UNNOISED.add(int(to))
        return int(to)

    def show_dungeon(self, party: Optional[int] = None, denoised: bool = False):
        '''  '''
        rows: int = int(sqrt(self.NUM_ROOMS))

        # noise init
        RESULT: Dungeon = {k: tile('*', (self.UNIT, 2*self.UNIT)) for k in range(self.NUM_ROOMS)}

        if party:
            self.UNNOISED.add(party)
        for k in self.UNNOISED:
            RESULT[k] = self.dungeon[k]

        def show_dungeon_(result: Dungeon):
            for j in range(rows):
                rooms = [result[j*rows + row] for row in range(rows)]
                for k in range(self.UNIT):
                    for x in reduce(lambda x,y: x+y, [list(x[k]) for x in rooms]):
                        write(x)
                    write('\n')

        if denoised:
            show_dungeon_(self.dungeon)
        else:
            show_dungeon_(RESULT)



    def init_game(self):
        ''' ''' 
        self.PARTY = self.init_party()
        
        self.init_room_id = self.dungeon[self.init_room_num][2, 2*self.UNIT - 3]
        
        self.shuffle_ids()
        
        self.mark_num()

        rocks = []
        for i in range(int(sqrt(self.NUM_ROOMS)) - 1):
            rocks.append(self.fill_with_rocks())

    
    def butterfly_reset(self, frm: int): 
        self.mv_party(frm, self.init_room_num)
        self.shuffle_ids()



    def test_make_all_and_show(self, denoised: bool = False):

        self.shuffle_ids()
        self.mark_num()

        rocks = []
        rocks.append(self.fill_with_rocks())
        rocks.append(self.fill_with_rocks())
        #print(rocks)

        party = self.init_party()
        #self.UNNOISED.append(party)

        # interchange this sequence of three directions to test other ones.
        party = self.mv_party(party, 'S')
        #self.UNNOISED.append(party)

        party = self.mv_party(party, 'S')
        #self.UNNOISED.append(party)

        party = self.mv_party(party, 'S')
        #self.UNNOISED.append(party)

        self.party = self.mv_party(party, 'E') 

        self.show_dungeon(denoised = denoised)
