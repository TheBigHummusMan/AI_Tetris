import pygame
import argparse, os, shutil, numpy, torch, random
from collections import deque

from torch import dtype
import time
import game
from game import TetrisGameTrain
from model import Linear_QNet, Qtrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1
LR = 0.001

class Agent:
    def __init__(self):
        self.n_game = 0
        self.epsilon = 80  # Randomness of the machine
        self.gamma = 0.9  # Discount rate (should be smaller than 1)
        self.memory = deque(maxlen=MAX_MEMORY)  # Stores AI data
        # input states, 32 hidden layer and 4 outputs
        self.model = Linear_QNet(8, 256, 4)
        self.trainer = Qtrainer(self.model, lr=LR, gamma=self.gamma)
        self.current_piece = []

    def get_state(self, game):
        # there are 8 important data for the game state, number of cleared lines, number of holes, the bunpiness of the board, the total board height, the pices x and y coordinates, the shape of the pices and its rotation
        self.current_piece = game.current_piece.get_stats()
        line_cleared = game.total_rows_cleared
        print("current piece stats :",self.current_piece)
        state = [line_cleared, game.get_number_of_holes(), game.get_bumpiness(), game.get_total_height()] + self.current_piece
        print("\n line_cleared, number of holes, bumpiness, total height, current piece stats: x, y, shape, rotation")
        print(state)
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
            move = random.randint(0, 3)
            final_move[move] = 1
            print("random move")
        
        else:
            # state
            print("ai move")
            state0 = torch.tensor(state, dtype = torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move


def train():

    best_score = 0

    game = TetrisGameTrain()
    agent = Agent()
    while True:
        #print("AI thinking")
        state_old = agent.get_state(game)

        final_move = agent.get_action(state_old)
        print(final_move, "ai ing")

        reward, done, score = game.play_step(final_move)

        new_state = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reward, new_state, done)
        agent.remember(state_old, final_move, reward, new_state, done)
        #time.sleep(0.2)
        if  not game.run:
            game.reset()
            agent.n_game += 1
            agent.train_long_memory()

            if game.score > best_score:
                best_score = agent.score
                agent.model.save()

            print('Game', agent.n_game, 'Score', score, 'Best Score', best_score)


if __name__ == '__main__':
    train()
