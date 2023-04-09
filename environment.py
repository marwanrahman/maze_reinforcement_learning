from enum import Enum
import numpy as np
from random import sample

class Action(Enum):
    MOVE_LEFT = [-1, 0]
    MOVE_RIGHT = [1, 0]
    MOVE_UP = [0, -1]
    MOVE_DOWN = [0, 1]

class Status(Enum):
    SEARCHING = 0
    WATER_REACHED = 1

class Environment:
    def __init__(self, maze) -> None:
        self.maze = maze
        self.cell_actions = self.generate_cell_actions()
        self.n_cells = len(self.cell_actions)
        self.current_cell = 0
        self.visited = set()
        self.status = Status.SEARCHING

    def reset(self):
        """Reset the environment"""
        self.current_cell = 0
        self.visited = set()
        self.status = Status.SEARCHING
        return self.current_cell
    
    def step(self, action):
        """Take a step with the specified action"""
        if action not in self.cell_actions[self.current_cell]:
            print("Move not allowed!")
            return
        
        next_coord = np.add(action.value, [self.maze.xc[self.current_cell], self.maze.yc[self.current_cell]])
        self.current_cell = self.maze.ce[tuple(next_coord)]

        if self.current_cell == 165: # reached water
            reward = 10
            self.status = Status.WATER_REACHED
        elif self.current_cell in self.visited: # penalty for going to a cell already visited
            reward = -0.25
        else:
            reward = 0

        self.visited.add(self.current_cell)

        return self.current_cell, reward, self.status

    def sample_actions(self):
        """randomly sample an action from allowable actions for current cell"""
        return sample(self.cell_actions[self.current_cell], 1)[0]
    
    def generate_cell_actions(self):
        """Returns a list of lists, where each cell has a list of allowable actions"""
        cell_actions = []
        for i in range(len(self.maze.xc)):
            cell_actions.append(self.get_actions_allowed(i))
        return cell_actions
        
    def get_actions_allowed(self, cell_idx):
        """Returns the moves allowed from the current cell based on the maze walls and boundaries."""
        x = self.maze.xc[cell_idx]
        y = self.maze.yc[cell_idx]

        moves = []
        if [x, y - 0.5] not in self.maze.wall_midpoints and y - 1 >= 0:
            moves.append(Action.MOVE_UP)
        if [x, y + 0.5] not in self.maze.wall_midpoints and y + 1 <= 14:
            moves.append(Action.MOVE_DOWN)
        if [x - 0.5, y] not in self.maze.wall_midpoints and x - 1 >= 0:
            moves.append(Action.MOVE_LEFT)
        if [x + 0.5, y] not in self.maze.wall_midpoints and x + 1 <= 14:
            moves.append(Action.MOVE_RIGHT)

        return moves
    