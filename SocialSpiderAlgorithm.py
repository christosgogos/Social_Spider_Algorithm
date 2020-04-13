import math
import numpy as np
from numpy import linalg as la
import random
from termcolor import colored
import matplotlib.pyplot as plt

Minimize_problem = True
Maximize_problem = False


class Spider:
    def __init__(self, s, s_previous, fs, vibration, cs, mask):
        self.s = s  # The position of s on the web.
        self.s_previous = s_previous  # The movement that s performed in the previous iteration
        self.fs = fs  # The fitness of the current position of s.
        self.vibration = vibration  # The target vibration of s in the previous iteration.
        self.cs = cs  # The number of iterations since s has last changed its target vibration.
        self.mask = mask  # The dimension mask in the previous iteration.

    def printout(self):
        print("position = "+str(self.s))
        print("previous position = " + str(self.s_previous))
        print("fitness = "+str(self.fs))
        self.vibration.printout()
        print("Cs = "+str(self.cs))
        print("Mask = "+str(self.mask))


class Vibration:
    def __init__(self, position, intensity):
        self.position = position  # the source position or target vibration
        self.intensity = intensity  # source intensity of the vibration

    def set_position_and_intensity(self, position, intensity):
        self.position = position
        self.intensity = intensity

    @staticmethod
    def intensity_position_ps_position_ps(fs):
        return math.log(1/(fs-c)+1)  # I(Ps;Ps; t)

    def printout(self):
        print("Intensity = "+str(self.intensity))


def distance(pa, pb):
    return la.norm(pa - pb, 1)  # D(Pa;Pb)


def intensity_position_pa_position_pb(pa, pb, sd, vibration_pa):  # pa spider a & pb spider b, I(Pa;Pb; t)
    return vibration_pa.intensity*math.exp((-distance(pa.s, pb.s))/(ra * sd))


# Calculate Standard_Deviation σ along each dimension
def standard_deviation():
    pop = [spider.s for spider in spiders]
    return np.sum(np.std(pop, axis=1)) / n


def f(a):
    z = []
    if Minimize_problem:
        z.extend(a)
        return eval(y)
    elif Maximize_problem:
        z.extend(-a)
        return -eval(y)


# there is a  array with 100 elements with one and zero,100*p elements with 0 , 100(1-p) with 1,0=false,1=true
# where p is the probability
def probability(p):
    arr = np.array([0] * int(100 * p) + [1] * int(100 - 100 * p))
    np.random.shuffle(arr)
    rand = random.choice(arr)
    if rand == 0:
        return True
    else:
        return False


def show(generate_vibration):
    for x in range(population):
        print("")
        print("spider" + str(x))
        spiders[x].printout()
        print("generate vibration = " + str(generate_vibration[x].intensity))
        print("")


# if return true then it is out of bounds [a,b]
def out_of_bounds(position):
    for x in range(len(position)):
        if position[x] < bounds[x, 0] or position[x] > bounds[x, 1]:
            return True
    return False


def create_population_of_spiders():
    for x in range(population):
        s = np.zeros(n)
        for x1 in range(n):
            s[x1] = np.random.uniform(bounds[x1, 0], bounds[x1, 1])
        vibration = Vibration(s, 0)
        spiders.append(Spider(s, s, 0, vibration, 0, np.zeros(n)))


def initialization_graphics(graph):
    global ax
    if graph and n==2:
        plt.close('all')
        fig = plt.figure(figsize=(7, 7))
        ax = plt.axes()
        plt.xlim(bounds[0, 0]-1, bounds[0, 1]+1)
        plt.ylim(bounds[1, 0]-1, bounds[1, 1]+1)


def graphics(X, Y):
    if n == 2:
        ax.scatter(X, Y, c='black')
        plt.draw()
        plt.pause(1)
        ax.collections[0].remove()


def social_spider_algorithm(graph):
    global spiders
    spiders = []
    create_population_of_spiders()
    minimize = spiders[0].s
    number_of_iterations = 0
    initialization_graphics(graph)
    # In the iteration phase
    while number_of_iterations <= lim:
        # Calculates the fitness , update the global optimum and generate vibrations
        generate_vibration = []
        for x in range(population):
            spiders[x].fs = f(spiders[x].s)
            if f(minimize) > spiders[x].fs:
                minimize = spiders[x].s
            generate_vibration.append(
                Vibration(spiders[x].s, spiders[x].vibration.intensity_position_ps_position_ps(spiders[x].fs)))

        # show(generate_vibration)
        # print("minimize = " + str(minimize)+"f(minimize) = "+str(f(minimize)))

        # Calculate the intensity of the vibrations V
        # generated by all spiders and Select the strongest vibration
        sd = standard_deviation()
        for x in range(population):
            max_vibration = Vibration(np.zeros(n), -1)
            for t in range(population):
                if x != t:
                    intensity = intensity_position_pa_position_pb(spiders[x], spiders[t], sd, generate_vibration[x])
                    if max_vibration.intensity < intensity:
                        max_vibration.set_position_and_intensity(spiders[t].s, intensity)
            if max_vibration.intensity > spiders[x].vibration.intensity:
                spiders[x].vibration.set_position_and_intensity(max_vibration.position, max_vibration.intensity)
                spiders[x].cs = 0
            else:
                spiders[x].cs += 1

            # change mask or not
            if not probability(pc**spiders[x].cs):
                for p in range(n):
                    if probability(pm):
                        spiders[x].mask[p] = 1
                    else:
                        spiders[x].mask[p] = 0

            # In case all bits are zeros or ones
            if n == np.count_nonzero(spiders[x].mask):  # all ones
                spiders[x].mask[random.randint(0, n - 1)] = 0
            elif np.count_nonzero(spiders[x].mask) == 0:  # all zeros
                spiders[x].mask[random.randint(0, n - 1)] = 1

            p_s_fo = np.array([])  # position  is generated based on the mask for s
            r = random.randint(0, population - 1)
            for d in range(n):
                if spiders[x].mask[d] == 0:
                    p_s_fo = np.append(p_s_fo, spiders[x].vibration.position[d])
                elif spiders[x].mask[d] == 1:
                    p_s_fo = np.append(p_s_fo, generate_vibration[r].position[d])

            # Calculate next position
            R = np.random.uniform(0, 1, n)
            next_position = spiders[x].s + (spiders[x].s - spiders[x].s_previous) * r + (p_s_fo - spiders[x].s) * R
            spiders[x].s_previous = spiders[x].s

            # Address any violated constraints.
            if out_of_bounds(next_position):
                rand_float = random.random()  # random [0,1]
                for t in range(n):
                    if next_position[t] > bounds[t, 1]:
                        next_position[t] = (bounds[t, 1] - spiders[x].s[t]) * rand_float
                    elif next_position[t] < bounds[t, 0]:
                        next_position[t] = (spiders[x].s[t] - bounds[t, 0]) * rand_float

            spiders[x].s = next_position
        if graph and n == 2:
            graphics([atr.s[0] for atr in spiders], [atr.s[1] for atr in spiders])
        number_of_iterations += 1
    return "global minimize = " + str(minimize)+'\n'+"f(minimize) = " + str(f(minimize))


# Sphere function minimum = 0
def test_function_0():
    global c, ra, pc, pm, y, n, population, bounds, lim
    c = 1E-100  # where C is a small constant such  fitness values are larger than C
    set_ra = {1 / 10, 1 / 5, 1 / 4, 1 / 3, 1 / 2, 1, 2, 3, 4, 5}
    ra = random.choice(tuple(set_ra))
    set_pc_and_pm = {0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99}
    pc = random.choice(tuple(set_pc_and_pm))
    pm = random.choice(tuple(set_pc_and_pm))
    print('\n'+"ra = " + str(ra) + '\n' + "pc = " + str(pc) + "  pm = " + str(pm) + '\n')
    y = "z[0]**2 + z[1]**2 + z[2]**2 + z[3]**2 + z[4]**2"
    n = 5  # dimensions
    # solution space or domain of definition [a , b] each dimensions
    bounds = np.array([[-5000, 5000],
                      [-5000, 5000],
                      [-5000, 5000],
                      [-5000, 5000],
                      [-5000, 5000]])
    population = 20
    lim = 3000  # max steps of iterations
    return


# Three-hump camel function minimum = 0
def test_function_1():
    global c, ra, pc, pm, y, n, population, bounds, lim
    c = 1E-100  # where C is a small constant such  fitness values are larger than C
    set_ra = {1 / 10, 1 / 5, 1 / 4, 1 / 3, 1 / 2, 1, 2, 3, 4, 5}
    ra = random.choice(tuple(set_ra))
    set_pc_and_pm = {0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99}
    pc = random.choice(tuple(set_pc_and_pm))
    pm = random.choice(tuple(set_pc_and_pm))
    print('\n'+"ra = " + str(ra) + '\n' + "pc = " + str(pc) + "  pm = " + str(pm) + '\n')
    y = "2*z[0]**2 - 1.05 * z[0]**4 + z[0]**6 /6 + z[0] * z[1] + z[1]**2"
    n = 2
    bounds = np.array([[-5, 5],
                      [-5, 5]])
    population = 10
    lim = 10  # max steps of iterations
    return


# McCormick function minimum = -1.9133
def test_function_2():
    global c, ra, pc, pm, y, n, population, bounds, lim
    c = -100  # where C is a small constant such  fitness values are larger than C
    set_ra = {1 / 10, 1 / 5, 1 / 4, 1 / 3, 1 / 2, 1, 2, 3, 4, 5}
    ra = random.choice(tuple(set_ra))
    set_pc_and_pm = {0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99}
    pc = random.choice(tuple(set_pc_and_pm))
    pm = random.choice(tuple(set_pc_and_pm))
    print('\n'+"ra = " + str(ra) + '\n' + "pc = " + str(pc) + "  pm = " + str(pm) + '\n')
    y = "math.sin(z[0] + z[1]) + (z[0] - z[1])**2 - 1.5 * z[0] + 2.5 * z[1] + 1"
    n = 2
    bounds = np.array([[-1.5, 4],
                       [-3, 4]])
    population = 10
    lim = 1000  # max steps of iterations
    return


# Schaffer function N. 4 minimum = 0.292579
def test_function_3():
    global c, ra, pc, pm, y, n, population, bounds, lim
    c = -100  # where C is a small constant such  fitness values are larger than C
    set_ra = {1 / 10, 1 / 5, 1 / 4, 1 / 3, 1 / 2, 1, 2, 3, 4, 5}
    ra = random.choice(tuple(set_ra))
    set_pc_and_pm = {0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99}
    pc = random.choice(tuple(set_pc_and_pm))
    pm = random.choice(tuple(set_pc_and_pm))
    print('\n'+"ra = " + str(ra) + '\n' + "pc = " + str(pc) + "  pm = " + str(pm) + '\n')
    y = "0.5 + ((math.cos(math.sin(abs(z[0]**2 - z[1]**2)))**2 - 0.5) / (1 + 0.001*(z[0]**2 + z[1]**2))**2)"
    n = 2
    bounds = np.array([[-100, 100],
                       [-100, 100]])
    population = 25
    lim = 2500  # max steps of iterations
    return


# Code for Test

for test in range(20):
    test_function_1()
    print('\n' + colored("Τest "+str(test + 1), 'blue')+'\n'+social_spider_algorithm(False))



# test_function_3()
# social_spider_algorithm(True)

# file = open("test.txt", "w+")
# file.write('\n'+"ra = " + str(ra) + '\n' + "pc = " + str(pc) + "  pm = " + str(pm) + '\n')
# file.write('\n' + "Τest "+str(test + 1)+'\n'+social_spider_algorithm(False))
# file.close()



