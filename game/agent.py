import pygame
import argparse, os, shutil, numpy, torch, random
from collections import deque

from torch import dtype

import game
from game import TetrisGameTrain
from model import Linear_QNet, Qtrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_game = 0
        self.epsilon = 80  # Randomness of the machine
        self.gamma = 0.9  # Discount rate (should be smaller than 1)
        self.memory = deque(maxlen=MAX_MEMORY)  # Stores AI data
        self.model = Linear_QNet(8, 256, 4)
        self.trainer = Qtrainer(self.model, lr=LR, gamma=self.gamma)
        self.current_piece = None

    def set_state(self, game):
        self.current_piece = game.current_piece
        line_cleared = game.total_rows_cleared
        print(self.current_piece)
        state = [line_cleared, game.get_number_of_holes(), game.get_bumpiness(), game.get_total_height()] + self.current_piece
        return state

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        final_move = [0, 0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        
        else:
            # state
            state0 = torch.tensor(state, dtype = torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

def train():
    plot_scores = []
    plot_mean_score = []
    total_score = 0
    best_score = 0

    #globals imported here
    screen_width = 800
    screen_height = 700
    play_width = 300    # 300 // 10  gives 30 width per block
    play_height = 600   # 600 // 20 gives 30 height per block
    block_size = 30

    game = TetrisGameTrain()
    agent = Agent()
    while True:

        print("birds and 911")
        state_old = agent.set_state(game)

        final_move = agent.get_action(state_old)

        #reward, done, score = game.play_step(final_move)
        new_state = agent.set_state(game)

        agent.train_short_memory(state_old, final_move, game.reward, new_state, game.run)
        agent.remember(state_old, final_move, game.reward, new_state, game.run)
        
        if not game.run:

            agent.n_game += 1
            agent.train_long_memory()

            if game.score > best_score:
                best_score = agent.score
                agent.model.save()

            print(f'Game {agent.n_game}, Score {game.score}, Best Score {best_score}')


if __name__ == '__main__':
    train()
