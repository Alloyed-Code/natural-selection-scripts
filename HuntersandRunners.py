import pygame
import random
import math
import copy

# --------- variables ---------
#grid square height and width
WIDTH = 4
HEIGHT = 4
MARGIN = 0
#grid size
grid_size_x = 128
grid_size_y = 128
#Colors
black = (0, 0, 0) #bad/undefined
white = (255, 255, 255) #air
blue = (0, 0, 255) #Runner
red = (255, 0 ,0) #Hunter
green = (0, 255, 0) #Block

class Tile ():
    color = black
    def __init__(self, y, x):
        self.y = y
        self.x = x

    def behavior (self):
        return

    def newCoords(self, y, x):
        self.y = y
        self.x = x

class Air (Tile):
    color = white
    def __inti__(self, y, x):
        Tile.__init__(self,y,x)
        

    def deepcopy(self, memodict=[]):
        return Air(self.y,self.x)

class Block (Tile):
    color = green
    def __init__(self, y, x):
        Tile.__init__(self,y,x)
        

    def deepcopy(self, memodict=[]):
        return Air(self.y,self.x)

class Entity (Tile):
    moved = False
    def __init__(self, y, x):
        Tile.__init__(self,y,x)

class Hunter (Entity):
    score = 0
    color = red
    def __init__(self, y, x, genome):
        Entity.__init__(self,y,x)
        self.genome = genome

    def behavior (self):
        self.moved = False
        i = 0
        while( i < len(self.genome)):
            self.moved = self.genome[i].action(self.y,self.x, self.moved)
            i += 1
        
class Runner (Entity):
    score = 0
    color = blue
    def __init__(self, y, x):
        Entity.__init__(self,y,x)

#========Action Functions=======#
actions = []
class Action ():
    def __init__(self, func):
        self.f = func

    def action(self, y,x, moved):
        return self.f(y,x,moved)

def moveUp(y,x,moved):
    if moved is False:
        if type(checkSpace(y-1,x)) is Air:
            next_grid[yWrapHandler(y-1)][xWrapHandler(x)] = grid[y][x]
            next_grid[yWrapHandler(y-1)][xWrapHandler(x)].newCoords(yWrapHandler(y-1),xWrapHandler(x))
            next_grid[y][x] = Air(y,x)
            return True
        else:
            next_grid[y][x] = grid[y][x]
            return False
    else:
        next_grid[y][x] = grid[y][x]
        return False
actions.append(Action(moveUp))

def moveRight(y,x,moved):
    if moved is False:
        if type(checkSpace(y,x+1)) is Air:
            next_grid[yWrapHandler(y)][xWrapHandler(x+1)] = grid[y][x]
            next_grid[yWrapHandler(y)][xWrapHandler(x+1)].newCoords(yWrapHandler(y),xWrapHandler(x+1))
            next_grid[y][x] = Air(y,x)
            return True
        else:
            next_grid[y][x] = grid[y][x]
            return False
    else:
        next_grid[y][x] = grid[y][x]
        return False
actions.append(Action(moveRight))

def moveDown(y,x,moved):
    if moved is False:
        if type(checkSpace(y+1,x)) is Air:
            next_grid[yWrapHandler(y+1)][xWrapHandler(x)] = grid[y][x]
            next_grid[yWrapHandler(y+1)][xWrapHandler(x)].newCoords(yWrapHandler(y+1),xWrapHandler(x))
            next_grid[y][x] = Air(y,x)
            return True
        else:
            next_grid[y][x] = grid[y][x]
            return False
    else:
        next_grid[y][x] = grid[y][x]
        return False
actions.append(Action(moveDown))

def moveLeft(y,x,moved):
    if moved is False:
        if type(checkSpace(y,x-1)) is Air:
            next_grid[yWrapHandler(y)][xWrapHandler(x-1)] = grid[y][x]
            next_grid[yWrapHandler(y)][xWrapHandler(x-1)].newCoords(yWrapHandler(y),xWrapHandler(x-1))
            next_grid[y][x] = Air(y,x)
            return True
        else:
            next_grid[y][x] = grid[y][x]
            return False
    else:
        next_grid[y][x] = grid[y][x]
        return False
actions.append(Action(moveLeft))


#======Sense Functions====#
senses = []
class Sense ():
    def __init__ (self, func):
        self.f = func

    def action(self, y, x):
        return self.f(y,x)

def senseUp(y,x):
    return checkSpace(y-1,x)
senses.append(Sense(senseUp))

def senseRight(y,x):
    return checkSpace(y,x+1)
senses.append(Sense(senseRight))

def senseDown(y,x):
    return checkSpace(y+1,x)
senses.append(Sense(senseDown))

def senseLeft(y,x):
    return checkSpace(y,x-1)
senses.append(Sense(senseLeft))
types = [Air, Block, Entity, Hunter, Runner]

#========Conditional Functions=======#
conditionals = []
class Conditional ():
    def __init__ (self,a,b,c,func):
        self.a = a
        self.b = b
        self.c = c
        self.f = func
    def action(self,y,x,moved):
        return self.f(self.a,self.b,self.c,y,x,moved)
        
def ifTileIsType(a,b,c,y,x,moved):
    if isinstance(a.action(y,x), b):
        return c.action(y,x,moved)
    else:
        next_grid[y][x] = grid[y][x]
        return False
conditionals.append(ifTileIsType)

def ifNOTTileIsType(a,b,c,y,x,moved):
    if not isinstance(a.action(y,x), b):
        return c.action(y,x,moved)
    else:
        next_grid[y][x] = grid[y][x]
        return False
conditionals.append(ifNOTTileIsType)

def ifTileIsTypeofOther(a,b,c,y,x,moved):
    if type(a.action(y,x)) is type(b.action(y,x)):
        return c.action(y,x,moved)
    else:
        next_grid[y][x] = grid[y][x]
        return False
conditionals.append(ifTileIsTypeofOther)

def ifNOTTileIsTypeofOther(a,b,c,y,x,moved):
    if not type(a.action(y,x)) is type(b.action(y,x)):
        return c.action(y,x,moved)
    else:
        next_grid[y][x] = grid[y][x]
        return False
conditionals.append(ifNOTTileIsTypeofOther)

#============Genome Maker============#
#initial Genome is random
initLenMax = 10
def initialGenome():
    Genome = []
    length = random.randint(1,initLenMax)
    for i in range(length):
        actionType = random.randint(1,2)
        if actionType == 1: #action
            choice = random.randint(0,3)
            Genome.append(actions[choice])
        elif actionType == 2: #conditional
            conditionalType = random.randint(0,len(conditionals)-1)
            if conditionalType < 2:
                senseType = random.randint(0,len(senses)-1)
                tileType = random.randint(0,len(types)-1)
                actionType = random.randint(0,len(actions)-1)
                Genome.append(Conditional(senses[senseType],types[tileType],actions[actionType],conditionals[conditionalType]))
            else:
                senseType = random.randint(0,len(senses)-1)
                senseType2 = random.randint(0,len(senses)-1)
                actionType = random.randint(0,len(actions)-1)
                Genome.append(Conditional(senses[senseType],senses[senseType2],actions[actionType],conditionals[conditionalType]))
    return Genome





#========array for the grid==========#
grid = []
next_grid = []
for row in range(grid_size_y): #range is grid height
    #adds column list for every row
    grid.append([])
    next_grid.append([])
    for column in range(grid_size_x): #range is grid width
        grid[row].append(Air(row,column)) #all cells start as air
        next_grid[row].append(Air(row,column))



#blanks grid to empty
def blankGrid(grid):
    for row in range(grid_size_y):
            for column in range(grid_size_x):
                if not isinstance(grid[row][column], entity):
                    grid[row][column] = Air[row][column]

def randomValue(coord):
    rand_coord = random.randint(0,coord - 1)
    return rand_coord

def checkSpace(y,x):
    return next_grid[yWrapHandler(y)][xWrapHandler(x)]

def xWrapHandler(x):
    if x >= grid_size_x: #wrap right
        return 0
    elif x < 0: #wrap left
        return grid_size_x -1
    return x

def yWrapHandler(y):
    if y >= grid_size_y: #wrap up
        return 0
    elif y < 0: #wrap down
        return grid_size_y -1
    return y        



    
#initialize game
pygame.init()
#set size of screen
window_size = [grid_size_x * WIDTH, grid_size_y * HEIGHT]
screen = pygame.display.set_mode(window_size)
#Title
pygame.display.set_caption("The Arena")
#stop program button
done = False
#screen update speed
clock = pygame.time.Clock()

# Initialization functions

blockTotal = 100
for i in range(blockTotal):
    placex = random.randint(0,grid_size_x-1)
    placey = random.randint(0,grid_size_y-1)
    grid[placey][placex] = Block(placey,placex)
grid[50][50] = Hunter(50,50,initialGenome())
grid[100][100] = Hunter(100,100,initialGenome())
grid[50][100] = Hunter(50,100,initialGenome())
grid[100][50] = Hunter(100,50,initialGenome())
grid[6][6] = Runner(6,6)
grid[7][7] = Block(7,7)

# -------- Main Loop -----------
while not done:
    round_num = 0
    pause = False
    reset_terrain = False
    wait_round = False
    auto_restart = False
    # -------- Round Loop -----------
    while not done:
        aliveHunters = 0
        aliveRunners = 0
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # User clicks the mouse. Get the position
                pos = pygame.mouse.get_pos()
                # Change the x/y screen coordinates to grid coordinates
                column = pos[0] // (WIDTH)
                row = pos[1] // (HEIGHT)
                print("Click ", pos, "Grid coordinates: ", row, column)
                if type(grid[row][column]) is block:
                    if grid[row][column].block_type == cellMax:
                        grid[row][column] = block(row,column,0)
                    else:
                        grid[row][column] = block(row,column, 1 + grid[row][column].block_type)
                if isinstance(grid[row][column], entity):
                    if type(grid[row][column]) is source:
                        print("Energy: " + str(grid[row][column].energy))
                        print("Age: " + str(grid[row][column].age) + "/" + str(grid[row][column].age_limit))
                        print("Score: " + str(grid[row][column].score))
                    if type(grid[row][column]) is feeler:
                        print("State: " + str(grid[row][column].state))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if pause == True:
                        print("Unpaused")
                        pause = False
                    elif pause == False:
                        print("Paused")
                        pause = True
                if event.key == pygame.K_r:
                    print("Reseting terrain...")
                    reset_terrain = True
                if event.key == pygame.K_s:
                    print("Spawned 1 new")
                    random_x = random.randint(0, grid_size_x -1)
                    grid[32][random_x] = source(random_x,32,initialGenes(),starting_energy)
                if event.key == pygame.K_a:
                    if auto_restart == True:
                        print("Auto restart disabled")
                        auto_restart = False
                    elif auto_restart == False:
                        print("Auto restart enabled")
                        auto_restart = True

                if event.key == pygame.K_h:
                    print ("""+==========Help==========+
Key Inputs:

       h: Help Menu
Spacebar: Pause/Unpause
       r: Reset terrain
       s: Spawn a new random source
       a: Automatically restart simulation if all are dead""")

        if reset_terrain == True:
                reset_terrain = False
                blankGrid(grid)
                spreadOre(grid)

        if pause == True:
            screen.fill(black)
            #draw the grid
            for row in range(grid_size_y):
                for column in range(grid_size_x):
                    color = grid[row][column].color
                    pygame.draw.rect(screen, #Chooses the screen
                                     color, #chooses the color of square
                                     [(MARGIN + WIDTH) * column + MARGIN,
                                      (MARGIN + HEIGHT) * row + MARGIN,
                                      WIDTH,
                                      HEIGHT])
        if pause == False:

            #activates behavior of all cells
            next_grid = copy.deepcopy(grid)
            for row in range(grid_size_y):
                for column in range(grid_size_x):
                    if type(grid[row][column]) != Air:
                        grid[row][column].behavior()
                        if type(grid[row][column]) is Hunter:
                            aliveHunters += 1
                        elif type(grid[row][column]) is Runner:
                            aliveRunners += 1
            grid = copy.deepcopy(next_grid)
            #set screen background
            screen.fill(black)

            #draw the grid
            for row in range(grid_size_y):
                for column in range(grid_size_x):
                    color = grid[row][column].color
                    pygame.draw.rect(screen, #Chooses the screen
                                     color, #chooses the color of square
                                     [(MARGIN + WIDTH) * column + MARGIN,
                                      (MARGIN + HEIGHT) * row + MARGIN,
                                      WIDTH,
                                      HEIGHT])

                                
            print ("round: " + str(round_num))
                #draw creatures
            """for entity in entities:
                    color = red
                    pygame.draw.circle(screen,color,
                                       [entity.x * WIDTH + WIDTH // 2,
                                        entity.y * HEIGHT + HEIGHT // 2],
                                       WIDTH // 2)"""
            round_num += 1
        #limit 30 frames per second
        clock.tick(30)
        #update screen
        pygame.display.flip()

pygame.quit()
