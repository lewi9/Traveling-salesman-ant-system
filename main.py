
## traveling saleman

import numpy as np
from tqdm import tqdm

class Ant:
    def __init__(self, startCity):
        self.startCity = startCity
        self.tabooList = [startCity,]
        self.currentCity = startCity

## Paths to files with matrix: distance and cost    
mainDir = "data/cities-70-"
distanceDir = mainDir + "distance.txt"
costDir = mainDir + "cost.txt"
paretoFrontDir = "results/paretoFront71.txt"
delim = " "
matricesNumber = 1

## Parameters of algorithm
maxCycle = 400

antsInCity = 150

alpha = pheromoneWeight = 1
beta = cityVisibility = 2
q = exploitationOrExploration = 0.4
vaporizeFactor = 0.05
pheromoneZero = 0.1

## Read data from files
distance = np.genfromtxt(distanceDir, delimiter=delim)

#cost = np.genfromtxt(costDir, delimiter=delim)
cost = np.genfromtxt(costDir, delimiter=delim)

print("Distance matrix:")
print(distance)
print("\nCost matrix:")
print(cost)

## Init variables  
distanceCopy = distance
distanceMax = np.max(distance)
distance = distance/np.max(distance)

costCopy = cost
costMax = np.max(cost)
cost = cost/np.max(cost)

matrices = [distance, cost]

cities = cost.shape[0]

maxes = [distanceMax, costMax]
paretoFront = []
paretoPath = []

## Build pheromone matrix with initial value
pheromone = np.ones((cities, cities)) * pheromoneZero

ants = []

print(f"Biggest distance beetwen two cities: {distanceMax}")

## Algorithm
for k in tqdm(range(maxCycle), ascii=True, desc="Main"):

    if k%10 == 9:
        print(f"Iter: {k+1}")
        paretoFrontCopy = np.copy(paretoFront)
        for i in range(len(paretoFrontCopy)):
            for j in range(matricesNumber):
                paretoFrontCopy[i][j] *= maxes[j]
        saveToFile = np.reshape(paretoFrontCopy, (len(paretoFrontCopy),matricesNumber))
        # not saveToFile *= maxes, because I have defined maxes in 1x2 dim, and when matricesNumber == 1 error occured
        
        np.savetxt(paretoFrontDir, saveToFile, delimiter='\t')
    localPheromone = np.copy(pheromone)    
    ## create ants
    for i in range(cities):
        for j in range(antsInCity):
            ants.append(Ant(i))

    ## travel through the cities
    for i in range(cities-1):
        newLocalPheromone = np.copy(localPheromone)*(1-vaporizeFactor)
        for ant in ants:
            avalaibleCities = [x for x in np.arange(cities) if x not in ant.tabooList]

            ## calculate probability to choose the city
            sumHeuristic = 0
            for j in range(matricesNumber):
                sumHeuristic += matrices[j][ant.currentCity][avalaibleCities] ** beta
            sumTotal = np.sum( localPheromone[ant.currentCity][avalaibleCities] ** alpha / sumHeuristic )
            probabilityVector = localPheromone[ant.currentCity][avalaibleCities] ** alpha / sumHeuristic / sumTotal

            ## if exploration pick with probability, else pick the best
            if np.random.sample() < q:
                destinationCity = int(np.random.choice(avalaibleCities, 1, p=probabilityVector))
            else:
                destinationCity = avalaibleCities[list(probabilityVector).index(np.max(probabilityVector))]
            ant.currentCity = destinationCity
            ant.tabooList.append(destinationCity)
            newLocalPheromone[ant.tabooList[-2]][ant.tabooList[-1]] +=  vaporizeFactor*pheromoneZero
        localPheromone = np.copy(newLocalPheromone)
            
    ## check that all roads are the same and add pheromone
    for ant in ants:
        path = np.zeros((matricesNumber,1))

        ## calculate travel parametr e.g. distance, cost
        for i in range(cities):
            index = i-1
            for j in range(matricesNumber):
                path[j] += matrices[j][ant.tabooList[index]][ant.tabooList[i]]

        ## update pareto solutions
        indexes = []
        flagAdd = 1
        for i in range(len(paretoFront)):
            validArray = np.linspace(0,0,matricesNumber)
            for j in range(matricesNumber):
                if path[j] < paretoFront[i][j]:
                    validArray[j] = 1
                elif path[j] > paretoFront[i][j]:
                    validArray[j] = -1
            if 1 in validArray and not -1 in validArray:
                indexes.append(i)
            if -1 in validArray and not 1 in validArray:
                flagAdd = 0
            if not 1 in validArray and not -1 in validArray:
                flagAdd = 0
        paretoFront = [i for j,i in enumerate(paretoFront) if j not in indexes]
        paretoPath = [i for j,i in enumerate(paretoPath) if j not in indexes]
        if flagAdd == 1:
            paretoFront.append(path)
            paretoPath.append(ant.tabooList)

    ## update pheromones for pareto path
    pheromone *= (1-vaporizeFactor)
    for elem, value in zip(paretoPath,paretoFront):
        for i in range(cities):
            index = i-1
            pheromoneAmount = 0
            for d in value:
                pheromoneAmount += d
            pheromone[elem[index]][elem[i]] += vaporizeFactor/pheromoneAmount*matricesNumber
    
    ants.clear()

for i in range(len(paretoFront)):
    for j in range(matricesNumber):
        paretoFront[i][j] *= maxes[j]
for elem, elem2 in zip(paretoFront, paretoPath):
    print(f"Path: {elem2}")
    print(f"Cost: {elem}")
saveToFile = np.reshape(paretoFront, (len(paretoFront),matricesNumber))
np.savetxt(paretoFrontDir, saveToFile, delimiter='\t')
