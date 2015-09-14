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
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    if i == 0:
                        x = 0
                        y = 0
                    elif i == 1:
                        x = 9
                        y = 0
                    else:
                        x = random.randint(0, 9)
                        y = random.randint(0, 3)
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:
            # numToPlace = 2
            # moves = []
            # for i in range(0, numToPlace):
            #     move = None
            #     while move == None:
            #         x = random.randint(0, 9)
            #         y = random.randint(6, 9)
            #
            #         if currentState.board[x][y].constr == None and (x, y) not in moves:
            #             move = (x, y)
            #             currentState.board[x][y].constr == True
            #     moves.append(move)
            # return moves
            if(self.playerId == 0):
                pid = 1
            elif(self.playerId == 1):
                pid = 0
            buildings = getConstrList(currentState, pid,(ANTHILL,TUNNEL))
            constructions = getConstrList(currentState, None, (GRASS,ANTHILL,TUNNEL,FOOD))
            buildingLocations = []
            constrLocations = []
            foodBestLocations = []
            for i in buildings: ## add ANTHILL and TUNNEL coordinates into a list
                buildingLocations.append(i.coords)
            for i in constructions: ## add constructions coordinates into a list
                constrLocations.append(i.coords)
                cost1 = 0 #movement cost
                cost2 = 0
                foodBestLocation = None
                secondBest = None
            for x in range(0,10):
                for y in range(6,10):
                    if (x, y) in constrLocations:
                        pass
                    else:
                        distanceFromAnthill = stepsToReach(currentState, (x,y), buildingLocations[0])
                        distanceFromTunnel = stepsToReach(currentState, (x,y), buildingLocations[1])
                        average = (distanceFromAnthill + distanceFromTunnel)/2.0

                        if(average > cost1): ## measeures the movment cost for the first food
                            cost1 = average
                            secondBest = foodBestLocation
                            foodBestLocation = (x,y)
                        elif(average > cost2): ## second food
                            cost2 = average
                            secondBest = (x,y)
            return [foodBestLocation, secondBest]


        else:
            return [(0, 0)]


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


        movementMoves = listAllMovementMoves(currentState)

        construction = getConstrList(currentState, None, [(FOOD)])
        food1 = construction[0].coords
        food2 = construction[1].coords
        tunnelCoords = tunnel[0].coords

        # movement for queen
        # for ant in queenAnt:


        # movement for worker ants
        for ant in workerAnt:
            location = ant.coords
            legalMoves = listAllLegalMoves(currentState)
            # find the closest fruit
            if (stepsToReach(currentState, location, food1) < stepsToReach(currentState, location, food2)):
                closestFruit = food1
            else: closestFruit = food2
            print closestFruit

            # if the ant is carrying food
            if (ant.carrying == False):
                if (stepsToReach(currentState, location, closestFruit) <= 2 and ant.hasMoved == False):
                    return Move(MOVE_ANT, [(location),(closestFruit)], None)
                else:
                    return movementMoves[random.randint(0,len(legalMoves) - 1)]
            else:
                if (stepsToReach(currentState, location, tunnelCoords) <= 2 and ant.hasMoved == False):
                    return Move(MOVE_ANT, [(location),(tunnelCoords)], None)
                else:
                    return movementMoves[random.randint(0,len(legalMoves) - 1)]






        # # for coord in listAdjacent(ant.coords):
        # #     constrHere = getConstrAt(currentState, coord)
        #
        # myInventory = getCurrPlayerInventory(currentState)
        # myAntHill = myInventory.getAnthill()
        # # if (getAntAt(currentState, hill.coords) ==  None):
        #



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
