from enum import Enum
import numpy as np
from random import sample

class Action(Enum):
    MOVE_LEFT = [-1, 0]
    MOVE_RIGHT = [1, 0]
    MOVE_UP = [0, -1]
    MOVE_DOWN = [0, 1]

class Turn(Enum):
    RIGHT_TURN = -1
    LEFT_TURN = 1

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
        self.last_turn = None
        self.last_action = Action.MOVE_RIGHT
        self.current_run = 0 # counts number of times current action has been taken
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
        
        reward = self.get_reward(action)
        self.visited.add(self.current_cell)
        return self.current_cell, reward, self.status
    
    def get_reward(self, action):
        """determine the reward of taking the given action"""
        reward = 0
        if self.last_turn is not None:
            moves_dict = {Action.MOVE_RIGHT: 1, Action.MOVE_DOWN: 2, Action.MOVE_LEFT: 3, Action.MOVE_UP: 4}

            diff = moves_dict[self.last_action] % len(moves_dict) - moves_dict[action] % len(moves_dict)
            # same as last turn, negative reward
            if diff == self.last_turn.value:
                reward = -0.1
                self.current_run = 0
            # moving forward
            elif diff == 0:
                self.current_run += 1
            # moving opposite direction
            else:
                self.current_run = 0
            
            if diff in [-1, 1]:
                self.last_turn = Turn(diff)
        else:
            # right turn at the start
            if action == Action.MOVE_DOWN:
                self.last_turn = Turn.RIGHT_TURN
            # left turn
            elif action == Action.MOVE_UP:
                self.last_turn = Turn.LEFT_TURN

        if self.current_run >= 4:
            # penalize moving ahead instead of making a turn at a junction (if it has been moving straight for a while)
            if len(self.cell_actions[self.current_cell]) > 1 and action == self.last_action:
                reward = -0.1

        next_coord = np.add(action.value, [self.maze.xc[self.current_cell], self.maze.yc[self.current_cell]])
        self.current_cell = self.maze.ce[tuple(next_coord)]

        if self.current_cell == 165: # reached water
            reward = 10
            self.status = Status.WATER_REACHED
        elif self.current_cell in self.visited: # penalty for going to a cell already visited
            reward = -0.25

        return reward

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
    