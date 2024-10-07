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
grid_size_x = 256
grid_size_y = 64
#Colors
black = (0, 0, 0) #bad/undefined
dark_grey = (85, 85, 85) #infrastructure
light_grey = (170, 170, 170) #feelers
white = (255, 255, 255) #air
brown = (205, 133, 63) #earth
blue = (0, 255, 255) #source
red = (150, 0 ,0) #ore
grey_brown = (150, 88, 67) #abandoned infrastructure
cellMax = 3

source_energy_drain = -1
source_metal_drain = -1
infr_energy_drain = 0
infr_metal_drain = 0
solar_power = 5
ore_constant = 8
ore_rand_max = 8
metal_cost_constant = -2
ore_gain = 25
age_limit = 75
starting_metal = 500
starting_energy = 100

class tile ():
    #can be either a tile or part of something living
    color = black
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def behavior(self):
        return
    def affectResources(self, metal, energy, depth):
        return False
    def checkSourceCoords(self):
        return False

class block (tile):
    #surrounding around living things ie air, earth, anything that will not update
    def __init__(self, x, y, kind):
        tile.__init__(self,x,y)
        self.block_type = kind
        if self.block_type == 0: #air
              self.color = white
        elif self.block_type == 1: #earth
            self.color = brown
        elif self.block_type == 2: #ore
            self.color = red
        elif self.block_type == 3: #abandoned infrastructure
            self.color = grey_brown

    def __deepcopy__(self, memodict={}):
        copy_object = block(self.x, self.y, self.block_type)
        return copy_object
    def behavior(self):
        if self.block_type == 3:
            chance = random.randint(0,10)
            #chance = 10
            if chance == 10:
                air = 0
                earth = 0
                space = checkSpace(self.x,self.y-1)#up
                if not isinstance(space, entity) and type(space) != int:
                    if space.block_type == 0:
                        air += 1
                    elif space.block_type == 1 or space.block_type == 2:
                        earth += 1
                elif space == 99:
                    earth += 1
                    air += 1
                space = checkSpace(self.x + 1,self.y)#right
                if not isinstance(space, entity) and type(space) != int:
                    if space.block_type == 0:
                        air += 1
                    elif space.block_type == 1 or space.block_type == 2:
                        earth += 1
                elif space == 99:
                    earth += 1
                    air += 1
                space = checkSpace(self.x,self.y + 1)#down
                if not isinstance(space, entity) and type(space) != int:
                    if space.block_type == 0:
                        air += 1
                    elif space.block_type == 1 or space.block_type == 2:
                        earth += 1
                elif space == 99:
                    earth += 1
                    air += 1
                space = checkSpace(self.x - 1,self.y)#left
                if not isinstance(space, entity) and type(space) != int:
                    if space.block_type == 0:
                        air += 1
                    elif space.block_type == 1 or space.block_type == 2:
                        earth += 1
                elif space == 99:
                    earth += 1
                    air += 1

                if air >= 2:
                    next_grid[self.y][self.x] = block(self.x,self.y, 0)
                elif earth >= 2:
                    chance = random.randint(0,ore_rand_max)
                    if chance == ore_constant:
                        next_grid[self.y][self.x] = block(self.x,self.y, 2)
                    else:
                        next_grid[self.y][self.x] = block(self.x,self.y, 1)
                

class entity (tile):
    #everything that has genetics
    def __init__(self, x, y, genes):
        tile.__init__(self, x, y)
        self.genes = genes
    def die(self):
        next_grid[self.y][self.x] = block(self.x,self.y,3)

class source(entity):
    #stores the metal and energy of the base
    color = blue
    age = 0
    score = 0
    age_limit = random.randint(40,80)
    def __init__(self, x, y, genes, energy, metal):
        entity.__init__(self, x, y, genes)
        self.spawned = False
        self.energy = energy
        self.metal = metal

    def __deepcopy__(self, memodict={}):
        copy_object = source(self.x,self.y,self.genes,self.energy,self.metal)
        copy_object.spawned = self.spawned
        copy_object.age = self.age
        copy_object.age_limit = self.age_limit
        copy_object.score = self.score
        return copy_object

    def affectResources(self, metal, energy, depth):
        self.energy += energy
        self.metal += metal
        if metal > 0:
            self.score += metal
        if energy > 0:
            self.score += energy
        if self.metal < 0:
            self.metal = 0
            #print("No Metal!")
            return False
        if self.energy < 0:
            self.energy = 0
            #print("No Energy!")
            return False
        return True

    def checkSourceCoords(self):
        return (self.x,self.y)

    def behavior(self):
        #drains a little resources and dies if can't
        if self.spawned == False: #initial deployment of feelers
            space = checkSpace(self.x,self.y-1)
            #up
            if isinstance(space, block):
                next_grid[self.y-1][self.x] = feeler(self.x, self.y-1, self.genes,
                                                self.x, self.y, self.genes[16][0][space.block_type])
                self.spawned = True
                #feelers.append((self.y-1,self.x))
            #right
                space = checkSpace(self.x+1,self.y)
            if isinstance(space, block):
                next_grid[self.y][wrapHandler(self.x+1)] = feeler(wrapHandler(self.x+1), self.y, self.genes,
                                                self.x, self.y, self.genes[16][1][space.block_type])
                self.spawned = True
                #feelers.append((self.y,wrapHandler(self.x+1)))
            #down
                space = checkSpace(self.x,self.y+1)
            if isinstance(space, block):
                next_grid[self.y+1][self.x] = feeler(self.x, self.y+1, self.genes,
                                                self.x, self.y, self.genes[16][2][space.block_type])
                self.spawned = True
                #feelers.append((self.y+1,self.x))
            #left
                space = checkSpace(self.x-1,self.y)
            if isinstance(space, block):
                next_grid[self.y][wrapHandler(self.x-1)] = feeler(wrapHandler(self.x-1), self.y, self.genes,
                                                self.x, self.y, self.genes[16][3][space.block_type])
                self.spawned = True
                #feelers.append((self.y,wrapHandler(self.x-1)))
        self.age += 1
        #print(self.energy)
        #print(self.metal)
        if self.affectResources(source_metal_drain,source_energy_drain, 0) == False:
            dead_sources.append(self)
            self.die()
        elif self.age > age_limit:
            #print("old")
            dead_sources.append(self)
            self.die()
        else:
            next_grid[self.y][self.x] = grid[self.y][self.x]
    
class infrastructure(entity):
    #connects sources to feelers and collects energy
    color = dark_grey
    def __init__(self, x, y, genes, connected_x, connected_y):
        entity.__init__(self, x, y, genes)
        self.connected_x = connected_x
        self.connected_y = connected_y

    def __deepcopy__(self, memodict={}):
        copy_object = infrastructure(self.x, self.y, self.genes, self.connected_x, self.connected_y)
        return copy_object

    def affectResources(self, metal, energy, depth):
        if depth < 20:
            return grid[self.connected_y][self.connected_x].affectResources(metal, energy, depth + 1)
        return False

    def checkSourceCoords(self):
        return grid[self.connected_y][self.connected_x].checkSourceCoords()

    def behavior(self):
        #drains resources and collects energy if air above infrastructure
        energy_change = solar(self.x,self.y) + infr_energy_drain
        metal_change = infr_metal_drain
        if self.affectResources(metal_change, energy_change, 0) == False:
            self.die()

class feeler(entity):
    #expands based on base genetics and collects metal
    color = light_grey
    def __init__(self, x, y, genes, connected_x, connected_y, state):
        self.state = state
        entity.__init__(self, x, y, genes)
        self.connected_x = connected_x
        self.connected_y = connected_y

    def __deepcopy__(self, memodict={}):
        copy_object = feeler(self.x, self.y, self.genes, self.connected_x, self.connected_y, self.state)
        return copy_object

    def affectResources(self, metal, energy, depth):
        if depth < 20:
            return grid[self.connected_y][self.connected_x].affectResources(metal, energy, depth + 1)
        return False

    def checkSourceCoords(self):
        return grid[self.connected_y][self.connected_x].checkSourceCoords()

    def behavior(self):
        #depending on state, consult genes and local tiles to find if it constructs to adjacents
        #drains resources based on adj construction
        #becomes infrastructure
        dependent = True
        dependent = self.construct(self.x,self.y-1,0)
        dependent = self.construct(self.x+1,self.y,1)
        dependent = self.construct(self.x,self.y+1,2)
        dependent = self.construct(self.x-1,self.y,3)

        #spawn = random.randint(0,1)
        spawn = 1
        if spawn == 1 and not dependent:
            next_grid[32][self.x] = source(self.x,32,passGenes(self.genes),starting_metal,starting_energy)        
        next_grid[self.y][self.x] = infrastructure(self.x,self.y,self.genes,self.connected_x,self.connected_y)

    def construct(self, x, y, direction):
        space = checkSpace(x,y)
        if type(space) is block:
            if self.genes[self.state][direction][space.block_type] < 16:
                construction_type = space.block_type
                if construction_type == 3:
                    metal_cost = 1
                    energy_cost = -1
                elif construction_type == 2:
                    metal_cost = ore_gain
                    energy_cost = construction_type +1
                else:
                    metal_cost = metal_cost_constant
                    energy_cost = construction_type +1
                if self.affectResources(metal_cost,energy_cost, 0) == True:
                    next_grid[y][wrapHandler(x)] = feeler(wrapHandler(x),y,self.genes,self.x,self.y,self.genes[self.state][direction][space.block_type])
                    #feelers.append((y,wrapHandler(x)))
                    return True
                else: 
                    return False
        elif type(space) is source and notHomeSource(space,self):
            if self.genes[self.state][direction][3] < 16:
                metal_cost = space.metal
                energy_cost = space.energy
                self.affectResources(metal_cost,energy_cost, 0)
                next_grid[y][wrapHandler(x)] = feeler(wrapHandler(x),y,self.genes,self.x,self.y,self.genes[self.state][direction][3])
        return True

#========array for the grid==========#
grid = []
next_grid = []
for row in range(grid_size_y): #range is grid height
    #adds column list for every row
    grid.append([])
    next_grid.append([])
    for column in range(grid_size_x): #range is grid width
        grid[row].append(block(row,column,1)) #all cells start as earth
        next_grid[row].append(block(row,column,1))

#sources = []
#feelers = []
dead_sources = []

def solar(x,y):
    if y > 0 and y < 30:
        if type(grid[y-1][x]) is block:
            if grid[y-1][x].block_type == 0:
                return solar_power
    return 0

def notHomeSource(checked, checker):
    coords = checker.checkSourceCoords()
    if coords is not False:
        if coords[0] == checked.x and coords[1] == checked.y:
            return False
    return True

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
        genome[16].append([])
        for condition in range(cellMax + 1):
            genome[16][gene].append(randomGene(16))
    return genome

#randomly disperses diamonds
def spreadOre (grid):
    for row in range(grid_size_y):
        for column in range(grid_size_x):
            random_num = random.randint(0, ore_rand_max)
            #random_num = random.randint(0, grid_size_y)
            #if random_num <= row // ore_constant:
            if random_num >= ore_constant:
                if not isinstance(grid[row][column], entity):
                    grid[row][column] = block(column,row,2)
#blanks grid to earth
def blankGrid(grid):
    for row in range(grid_size_y):
            for column in range(grid_size_x):
                if not isinstance(grid[row][column], entity):
                    grid[row][column] = block(row,column,1)
def setAir(grid):
    for row in range(grid_size_y): #sets air to everywhere level 32 and less
                    for column in range(grid_size_x):
                        if row > 32:
                            break
                        if not isinstance(grid[row][column], entity):
                            grid[row][column] = block(row,column,0)


def randomValue(coord):
    rand_coord = random.randint(0,coord - 1)
    return rand_coord

def checkSpace(x,y):
    if 0 <= x < grid_size_x and 0 <= y < grid_size_y: 
        return grid[y][x]
    elif 0 <= y < grid_size_y:
        return grid[y][wrapHandler(x)]
    else:
        return 99 #bedrock/arena border

def wrapHandler(x):
    if x >= grid_size_x: #wrap right
        return 0
    elif x < 0: #wrap left
        return grid_size_x -1
    return x
        

def mutation(current, gene_max):
    #1 in 200 chance of mutation
    if random.randint(1,200) == 200:
        print ("Mutation!")
        return randomGene(gene_max)
    else:
        return current

def randomGene(gene_max):
    return random.randint(0,gene_max)

def passGenes(genes):
    for chromosome in range(16): #16 chromosomes per genome
        for gene in range(4): #4 different directions 0 up, 1 right, 2 down, 3 left
            for condition in range(cellMax + 1): #conditions equal to different cells where 0 = air etc
                genes[chromosome][gene][condition] = mutation(genes[chromosome][gene][condition], 31)
    for gene in range(4): #direction
        for condition in range(cellMax + 1):
            genes[16][gene][condition] = mutation(genes[16][gene][condition], 15)
    return genes


    
#initialize game
pygame.init()
#set size of screen
window_size = [grid_size_x * WIDTH, grid_size_y * HEIGHT]
screen = pygame.display.set_mode(window_size)
#Title
pygame.display.set_caption("The Synthetic World")
#stop program button
done = False
#screen update speed
clock = pygame.time.Clock()

# Initialization functions
spreadOre(grid)
setAir(grid)

#grid[32][grid_size_x // 5] = source(grid_size_x // 5,32,initialGenes(),starting_metal,starting_energy)
grid[32][grid_size_x * 2 // 5] = source(grid_size_x * 2 // 5,32,initialGenes(),starting_metal,starting_energy)
grid[32][grid_size_x * 3 // 5] = source(grid_size_x * 3 // 5,32,initialGenes(),starting_metal,starting_energy)
#grid[32][grid_size_x * 4 // 5] = source(grid_size_x * 4 // 5,32,initialGenes(),starting_metal,starting_energy)

# -------- Main Loop -----------
while not done:
    round_num = 0
    generation = 0
    pause = False
    reset_terrain = False
    wait_round = False
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
                        print("Metal: " + str(grid[row][column].metal))
                        print("Energy: " + str(grid[row][column].energy))
                        print("Age: " + str(grid[row][column].age))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    if pause == True:
                        pause = False
                    elif pause == False:
                        pause = True
                if event.key == pygame.K_r:
                    reset_terrain = True

        if reset_terrain == True:
                reset_terrain = False
                blankGrid(grid)
                spreadOre(grid)
                setAir(grid)

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
                        if type(grid[row][column]) is source:
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
                wait_round = False
                round_num = 0
                generation += 1
                first = 0
                second = 0
                for s in dead_sources:
                    if first == 0:
                        first = s
                    elif s.score > first.score:
                        if second != 0:
                            if first.score > second.score:
                                second = first
                        else:
                            second = first
                        first = s
                    elif second == 0:
                        second = s
                    elif s.score > second.score:
                        second = s
                
                print ("Top Score: " + str(first.score))
                dead_sources = []
                #blankGrid(grid)
                #spreadOre(grid)
                #setAir(grid)
                xpos = 1
                grid[32][grid_size_x -1] = source(grid_size_x -1,32,first.genes,starting_metal,starting_energy)
                for new_source in range(2):
                    #xpos = randomValue(grid_size_x)
                    #grid[32][xpos] = source(xpos,32,passGenes(first.genes),starting_metal,starting_energy)
                    grid[32][grid_size_x * xpos // 5] = source(grid_size_x * xpos // 5,32,passGenes(first.genes),starting_metal,starting_energy)
                    xpos += 1
                if second != 0:
                    for new_source in range(2):
                        #xpos = randomValue(grid_size_x)
                        #grid[32][xpos] = source(xpos,32,passGenes(second.genes),starting_metal,starting_energy)
                        grid[32][grid_size_x * xpos // 5] = source(grid_size_x * xpos // 5,32,passGenes(second.genes),starting_metal,starting_energy)
                        xpos += 1
                    
            print ("round: " + str(round_num) + " Generation: " + str(generation))
                #draw creatures
            """for entity in entities:
                    color = red
                    pygame.draw.circle(screen,color,
                                       [entity.x * WIDTH + WIDTH // 2,
                                        entity.y * HEIGHT + HEIGHT // 2],
                                       WIDTH // 2)"""
            #if alive == 0 and round_num > 1:
                #wait_round = True
            round_num += 1
        #limit 30 frames per second
        clock.tick(30)
        #update screen
        pygame.display.flip()

pygame.quit()
