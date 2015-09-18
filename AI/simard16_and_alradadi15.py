  # -*- coding: latin-1 -*-
import random
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *


##
#AIPlayer
#Description: The responsibility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "HeuristicAI")

    ##
    #getPlacement
    #Description: The getPlacement method corresponds to the
    #action taken on setup phase 1 and setup phase 2 of the game.
    #In setup phase 1, the AI player will be passed a copy of the
    #state as currentState which contains the board, accessed via
    #currentState.board. The player will then return a list of 10 tuple
    #coordinates (from their side of the board) that represent Locations
    #to place the anthill and 9 grass pieces. In setup phase 2, the player
    #will again be passed the state and needs to return a list of 2 tuple
    #coordinates (on their opponent’s side of the board) which represent
    #Locations to place the food sources. This is all that is necessary to
    #complete the setup phases.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is
    #       requesting a placement from the player.(GameState)
    #
    #Return: If setup phase 1: list of ten 2-tuples of ints -> [(x1,y1), (x2,y2),…,(x10,y10)]
    #       If setup phase 2: list of two 2-tuples of ints -> [(x1,y1), (x2,y2)]
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        if currentState.phase == SETUP_PHASE_1:    #placing ant hill, path, and grass
            numToPlace = 9
            moves = []
            moves.append((0,0)) #anthill at right corner
            moves.append((9,0)) #tunnel at left corner
            currentState.board[0][0].constr = ANTHILL
            currentState.board[9][0].constr = TUNNEL
            for i in range (0,9):
                moves.append((i,3)) # place grass in a straight row
                currentState.board[i][3].constr = GRASS
            return moves

        elif currentState.phase == SETUP_PHASE_2:
            buildings = getConstrList(currentState, PLAYER_ONE,(ANTHILL,TUNNEL))  #stuff on foe's side
            constructions = getConstrList(currentState, None, (GRASS,ANTHILL,TUNNEL,FOOD))
            buildingLocations = []
            constrLocations = []
            foodBestLocations = []
            for i in buildings: ## add ANTHILL and TUNNEL coordinates into a list
                buildingLocations.append(i.coords)
            for i in constructions: ## add GRASS, ANTHILL, TUNNEL, FOOD coordinates into a list
                constrLocations.append(i.coords)
                cost1 = 0 #movement cost to food1
                cost2 = 0 #movement cost to food2
                foodBestLocation = None
                secondBest = None
            for x in range(0,10):
                for y in range(6,10):
                    average = None
                    if (x, y) in constrLocations:
                        pass # if spot is not empty do nothing
                    else: # measure the average distance from ANTHILL and TUNNEL and choose the farthest
                        distanceFromAnthill = stepsToReach(currentState, (x,y), buildingLocations[0])
                        distanceFromTunnel = stepsToReach(currentState, (x,y), buildingLocations[1])
                        average = (distanceFromAnthill + distanceFromTunnel)/2.0
                    if(average > cost1):
                        cost1 = average
                        secondBest = foodBestLocation
                        foodBestLocation = (x,y)
                    elif(average > cost2):
                        cost2 = average
                        secondBest = (x,y)
        return [foodBestLocation, secondBest]

    ##
    #getMove
    #Description: The getMove method corresponds to the play phase of the game
    #and requests from the player a Move object. All types are symbolic
    #constants which can be referred to in Constants.py. The move object has a
    #field for type (moveType) as well as field for relevant coordinate
    #information (coordList). If for instance the player wishes to move an ant,
    #they simply return a Move object where the type field is the MOVE_ANT constant
    #and the coordList contains a listing of valid locations starting with an Ant
    #and containing only unoccupied spaces thereafter. A build is similar to a move
    #except the type is set as BUILD, a buildType is given, and a single coordinate
    #is in the list representing the build location. For an end turn, no coordinates
    #are necessary, just set the type as END and return.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is
    #       requesting a move from the player.(GameState)
    #
    #Return: Move(moveType [int], coordList [list of 2-tuples of ints], buildType [int]
    ##
    def getMove(self, currentState):
        workerAnt = getAntList(currentState, PLAYER_TWO, [(WORKER)])
        queenAnt = getAntList(currentState, PLAYER_TWO, [(QUEEN)])
        droneAnt = getAntList(currentState, PLAYER_TWO, [(DRONE)])
        tunnel = getConstrList(currentState, PLAYER_TWO, [(TUNNEL)])
        dronePresent = False

        legalMoves = listAllLegalMoves(currentState)

        construction = getConstrList(currentState, None, [(FOOD)])
        food1 = construction[0].coords
        food2 = construction[1].coords
        tunnelCoords = tunnel[0].coords

        # queens movement
        for i in range(0, len(queenAnt)):
            p2inventory = currentState.inventories[PLAYER_TWO]
            queen = queenAnt[i]
            if queen.hasMoved == False and queen.coords == (0,0):
                return Move(MOVE_ANT, [(0,0),(1,0)], None)
            # elif queen.hasMoved == False and queen.coords == (1,0):
            #     return Move(MOVE_ANT, [(1,0),(0,0)], None)
            if (queen.hasMoved == False and currentState.inventories[PLAYER_TWO].foodCount > 1):
                return Move(BUILD, [(0,0)], DRONE)
            # elif queen.coords == (1,0) and p2inventory.foodCount >= 2 and dronePresent == False:
            #     dronePresent = True
            #     return Move(BUILD, [(0,0)], DRONE)

        # for drones
        for droneAnt in droneAnt:
            if droneAnt.hasMoved == False:
                location = droneAnt.coords
                indexesOfLegalMoves = []
                locationOfAntHill = currentState.inventories[PLAYER_ONE].getQueen().coords

                legalMovesForAnt = []
                for x in legalMoves:
                    if (x.moveType == MOVE_ANT):
                        foo = x.coordList
                        legalMovesForAnt.append(foo)
                        indexesOfLegalMoves = [x for x, y in enumerate(legalMovesForAnt) if y[0] == location]

                # SHORTEST PATH!
                winner = None
                distance = []
                for i in range(0,len(indexesOfLegalMoves),1):
                    tmpMove = legalMovesForAnt[indexesOfLegalMoves[i]]
                    tmpMoveDestination = tmpMove[-1]
                    distance.append(stepsToReach(currentState, tmpMoveDestination, locationOfAntHill))

                winner = distance.index(min(distance))

                return Move(MOVE_ANT, legalMovesForAnt[winner], None)

        # movement for worker ants
        for ant in workerAnt:
            print "Number of worker ants:" + str(len(workerAnt))
            location = ant.coords
            print "ANT: " + str(location)
            indexesOfLegalMoves = []

            # find the closest fruit
            if (stepsToReach(currentState, location, food1) < stepsToReach(currentState, location, food2)):
                closestFruit = food1
            else: closestFruit = food2

            # if the ant is NOT carrying food
            if (ant.carrying == False and ant.hasMoved == False):
                legalMovesForAnt = []
                for x in legalMoves:
                    if (x.moveType == MOVE_ANT):
                        foo = x.coordList
                        legalMovesForAnt.append(foo)
                        indexesOfLegalMoves = [x for x, y in enumerate(legalMovesForAnt) if y[0] == location]

                distanceList = []
                # SHORTEST PATH!
                winner = None
                distance = []
                for i in range(0,len(indexesOfLegalMoves),1):
                    tmpMove = legalMovesForAnt[indexesOfLegalMoves[i]]
                    tmpMoveDestination = tmpMove[-1]
                    distance.append(stepsToReach(currentState, tmpMoveDestination, closestFruit))

                winner = distance.index(min(distance))

                return Move(MOVE_ANT, legalMovesForAnt[winner], None)

            # If ant is carrying food
            if (ant.carrying == True and ant.hasMoved == False):
                legalMovesForAnt = []
                for x in legalMoves:
                    if (x.moveType == MOVE_ANT):
                        foo = x.coordList
                        legalMovesForAnt.append(foo)
                        indexesOfLegalMoves = [x for x, y in enumerate(legalMovesForAnt) if y[0] == location]

                distanceList = []
                # SHORTEST PATH!
                winner = None
                distance = []
                for i in range(0,len(indexesOfLegalMoves),1):
                    tmpMove = legalMovesForAnt[indexesOfLegalMoves[i]]
                    tmpMoveDestination = tmpMove[-1]
                    distance.append(stepsToReach(currentState, tmpMoveDestination, tunnelCoords))

                winner = distance.index(min(distance))

                return Move(MOVE_ANT, legalMovesForAnt[winner], None)
            else:
                return Move(END, None, None)


    ##
    #getAttack
    #Description: The getAttack method is called on the player whenever an ant completes
    #a move and has a valid attack. It is assumed that an attack will always be made
    #because there is no strategic advantage from withholding an attack. The AIPlayer
    #is passed a copy of the state which again contains the board and also a clone of
    #the attacking ant. The player is also passed a list of coordinate tuples which
    #represent valid locations for attack. Hint: a random AI can simply return one of
    #these coordinates for a valid attack.
    #
    #Parameters:
    #   currentState - The current state of the game at the time the Game is requesting
    #       a move from the player. (GameState)
    #   attackingAnt - A clone of the ant currently making the attack. (Ant)
    #   enemyLocation - A list of coordinate locations for valid attacks (i.e.
    #       enemies within range) ([list of 2-tuples of ints])
    #
    #Return: A coordinate that matches one of the entries of enemyLocations. ((int,int))
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        print (enemyLocations)
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #registerWin
    #Description: The last method, registerWin, is called when the game ends and simply
    #indicates to the AI whether it has won or lost the game. This is to help with
    #learning algorithms to develop more successful strategies.
    #
    #Parameters:
    #   hasWon - True if the player has won the game, False if the player lost. (Boolean)
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
