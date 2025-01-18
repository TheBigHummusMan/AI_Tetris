import argparse,os,shutil,numpy,torch,random
from collections import deque
import game 
from model import Linear_QNet, Qtrainer

MAX_MEMORY = 100_000
BATCH_SIZE = 1000

LR = 0.001

class Agent:
    def __init__(self):
        self.n_game = 0
        self.epsilon = 0 #randomnes of the machine
        self.gamma = 0.9 #discount rate can be 0.8, must be smaller than 1
        self.memory = deque(maxlen=MAX_MEMORY) # stores ai data 
        #self.model = Linear_QNet(number of input states,hidden can be any,output)
        self.trainer = Qtrainer(self.model, lr=LR, gamma=self.gamma)

    def get_State(self,game):
        #TODO need to add all states to a list
        pass
    def remember(self,state,action,reward,next_state,done):
        self.memory.append((state,action,reward,next_state,done))

    def train_long_memory(self):
        if len(self.memory)>BATCH_SIZE:
            mini_sample = random.sample(self.memory,BATCH_SIZE)
        else: 
            mini_sample = self.memory
        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self,state,action,reward,next_state,done):
        self.trainer.train_step(state,action,reward,next_state,done)

    def get_action(self,state):
        # makes it so that the machine starts off by doing random moves but after training, it does random moves less frequently
        self.epsilon = 100 - self.n_game
        final_move = [0,0,0]
        if random.randint(0,200)<self.epsilon:
            move = random.randint(0,2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move]=1

        return final_move

    def train():
        plot_scores = []
        plot_mean_score = []
        total_score = 0
        best_score = 0
        agent = Agent ()
        game = game()
        while (True):
            #get old and current state
            state_old = agent.get_State(game)

            #get move based off the state
            final_move = agent.get_action(state_old)

            #perform more, update state
            reward,done,score = game.play_step(final_move)
            new_state = agent.get_State(game)

            #train short memory
            agent.train_short_memory(state_old,final_move,reward,new_state,done)

            agent.remember(state_old,final_move,reward,new_state,done)
            
            if done:
                # train long memory
                game.main()
                agent.n_game+=1
                agent.train_long_memory()
                if score > best_score:
                    best_score=score
                    agent.model.save()
                print('game'+agent.n_game+'score'+score+'record'+ best_score)
                # TODO training fuctions


    if __name__ == '__main__':
        train()