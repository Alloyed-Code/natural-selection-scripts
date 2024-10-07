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
dark_grey = (85, 85, 85)
light_grey = (170, 170, 170)
white = (255, 255, 255) #air
brown = (205, 133, 63)
blue = (0, 255, 255)
red = (150, 0 ,0)
grey_brown = (150, 88, 67)
dark_blue = (0, 122, 122)
cellMax = 3


mutation_chance = 400


max_chain = 64


class tile ():
    #just a tile
    color = black
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def behavior(self):
        return
    def affectResources(self, energy, depth):
        return False
    def checkSourceCoords(self, depth):
        return False

class block (tile):
    #square stuff?
    def __init__(self, x, y, kind):
        tile.__init__(self,x,y)
        self.block_type = kind
        if self.block_type == 0: #air
              self.color = white
        elif self.block_type == 1: #
            self.color = brown
        elif self.block_type == 2: #
            self.color = red
        elif self.block_type == 3: #
            self.color = grey_brown

    def __deepcopy__(self, memodict={}):
        copy_object = block(self.x, self.y, self.block_type)
        return copy_object
    def behavior(self):
        return
                
class entity (tile):
    #everything that has genetics and changes
    def __init__(self, x, y, genes):
        tile.__init__(self, x, y)
        self.genes = genes
    def die(self):
        next_grid[self.y][self.x] = block(self.x,self.y,3)
    def __deepcopy__(self, memodict={}):
        copy_object = source(self.x,self.y,self.genes,self.energy)
        copy_object.spawned = self.spawned
        copy_object.age = self.age
        copy_object.age_limit = self.age_limit
        copy_object.score = self.score
        return copy_object


#========array for the grid==========#
grid = []
next_grid = []
for row in range(grid_size_y): #range is grid height
    #adds column list for every row
    grid.append([])
    next_grid.append([])
    for column in range(grid_size_x): #range is grid width
        grid[row].append(block(column,row,1)) #all cells start as air
        next_grid[row].append(block(column,row,0))

#========array for entities==========#
entities = []


def initialGenes():
    genome = []
    for chromosome in range(16): #16 chromosomes per genome
        genome.append([])
        for gene in range(4): #4 different directions 0 up, 1 right, 2 down, 3 left
            genome[chromosome].append([])
            for condition in range(cellMax + 1): #conditions equal to different cells where 0 = air etc
                genome[chromosome][gene].append(randomGene(31))
            
    genome.append([]) #special 17th chromosome for initial source building
    for gene in range(4): #direction
        genome[16].append(randomGene(31))
    return genome



#blanks grid to earth
def blankGrid(grid):
    for row in range(grid_size_y):
            for column in range(grid_size_x):
                if not isinstance(grid[row][column], entity):
                    grid[row][column] = block(column,row,1)
def setAir(grid):
    for row in range(grid_size_y): #sets air to everywhere level 32 and less
                    for column in range(grid_size_x):
                        if row > 32:
                            break
                        if not isinstance(grid[row][column], entity):
                            grid[row][column] = block(column,row,0)


def randomValue(coord):
    rand_coord = random.randint(0,coord - 1)
    return rand_coord

def checkSpace(x,y):
    if 0 <= x and x < grid_size_x and 0 <= y and y < grid_size_y: 
        return next_grid[y][x]
    elif 0 <= y and y < grid_size_y:
        return next_grid[y][wrapHandler(x)]
    else:
        return 99 #bedrock/arena border

def wrapHandler(x):
    if x >= grid_size_x: #wrap right
        return 0
    elif x < 0: #wrap left
        return grid_size_x -1
    return x
        

def mutation(current, gene_max):
    #1 in ? chance of mutation
    if random.randint(1,mutation_chance) == 1:
        #print ("Mutation!")
        return randomGene(gene_max)
    else:
        return current

def randomGene(gene_max):
    return random.randint(0,gene_max)

def passGenes(genes):
    for chromosome in range(16): #16 chromosomes per genome
        for gene in range(4): #4 different directions 0 up, 1 right, 2 down, 3 left
            for direction in range(cellMax+1):
                genes[chromosome][gene][direction] = mutation(genes[chromosome][gene][direction], 31)
    for gene in range(4): #direction
            genes[16][gene] = mutation(genes[16][gene], 15)
    return genes


    
#initialize game
pygame.init()
#set size of screen
window_size = [grid_size_x * WIDTH, grid_size_y * HEIGHT]
screen = pygame.display.set_mode(window_size)
#Title
pygame.display.set_caption("The Petri")
#stop program button
done = False
#screen update speed
clock = pygame.time.Clock()

# Initialization functions
#setAir(grid)

# -------- Main Loop -----------
while not done:
    round_num = 0
    pause = False
    reset_terrain = False
    wait_round = False
    auto_restart = False
    # -------- Round Loop -----------
    while not done:
        alive = 0
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
                #setAir(grid)

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
                    #if type(grid[row][column]) is not block:
                    if type(grid[row][column]) == type(next_grid[row][column]):
                        if type(grid[row][column]) is source or type(grid[row][column]) is seed or type(grid[row][column]) is feeler:
                            alive += 1
                        grid[row][column].behavior()
            """for s in sources:
                grid[s[0]-1][s[1]-1].behavior
                alive+=1
            for f in feelers:
                grid[f[0]][f[1]].behavior"""
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

            if wait_round == True:
                if auto_restart == True:
                    print("All dead, spawning new")
                    wait_round = False
                    blankGrid(grid)
                    spreadOre(grid)
                    #setAir(grid)
                    round_num = 0
                    for n in range(spawn_new_total):
                        random_x = random.randint(0, grid_size_x -1)
                        random_y = random.randint(0, grid_size_y -1)
                        #spawn new
                        alive += 1
                    
            print ("round: " + str(round_num))
                #draw creatures
            """for entity in entities:
                    color = red
                    pygame.draw.circle(screen,color,
                                       [entity.x * WIDTH + WIDTH // 2,
                                        entity.y * HEIGHT + HEIGHT // 2],
                                       WIDTH // 2)"""
            if alive == 0:
                wait_round = True
            round_num += 1
        #limit 30 frames per second
        clock.tick(30)
        #update screen
        pygame.display.flip()

pygame.quit()
