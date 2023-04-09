from tqdm import tqdm
from environment import Environment, Status
from agent import Agent
from maze_utils.MM_Maze_Utils import *
from matplotlib import pyplot as plt
from plotting import plot_path

maze = NewMaze(6)
env = Environment(maze)
agent = Agent(env)
agent = Agent(env, learning_rate=0.1, epsilon=0.1)

n_episodes = 500
save_episodes = [0, 1, 5, 10, 50, 100, 200, 500, 1000, 10000]

for episode in tqdm(range(n_episodes)):
    obs = env.reset()
    done = False
    path = [obs]
    while not done:
        # Retrieve an action from the agent
        action = agent.get_action(obs)
        next_obs, reward, status = env.step(action)  # Let environment process agent's action

        # Update the agent's policy with environment's feedback
        agent.update(obs, action, reward, next_obs)
        
        # Update bookkeeping variables
        done = status == Status.WATER_REACHED
        obs = next_obs
        path.append(obs)
        # print(obs)
    if episode in save_episodes:
        agent.q_history[episode] = (agent.q_values.copy(), path)
        plot_path(maze, path)
        print("plotted!")
