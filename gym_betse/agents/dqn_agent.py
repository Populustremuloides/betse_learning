# gym_betse/agents/dqn_agent.py

import random
import numpy as np
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
from gym_betse.agents.base_agent import BaseAgent

class DQNAgent(BaseAgent):
    """
    DQN Agent implementation.
    """
    def __init__(self, state_size, action_size):
        super(DQNAgent, self).__init__(state_size, action_size)
        self.memory = deque(maxlen=2000)
        # Hyperparameters
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 64
        self.learning_rate = 1e-3
        # Build network
        self.model = self._build_model()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.loss_fn = nn.MSELoss()

    def _build_model(self):
        model = nn.Sequential(
            nn.Linear(self.state_size, 24),
            nn.ReLU(),
            nn.Linear(24, 24),
            nn.ReLU(),
            nn.Linear(24, self.action_size)
        )
        return model

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        state = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        act_values = self.model(state)
        return torch.argmax(act_values[0]).item()

    def step(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) > self.batch_size:
            self.replay()
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def replay(self):
        minibatch = random.sample(self.memory, self.batch_size)
        states = torch.tensor([e[0] for e in minibatch], dtype=torch.float32)
        actions = torch.tensor([e[1] for e in minibatch], dtype=torch.long)
        rewards = torch.tensor([e[2] for e in minibatch], dtype=torch.float32)
        next_states = torch.tensor([e[3] for e in minibatch], dtype=torch.float32)
        dones = torch.tensor([e[4] for e in minibatch], dtype=torch.float32)
        # Compute target
        target = rewards + self.gamma * torch.max(self.model(next_states), dim=1)[0] * (1 - dones)
        current = self.model(states).gather(1, actions.unsqueeze(1)).squeeze()
        # Compute loss
        loss = self.loss_fn(current, target.detach())
        # Backpropagation
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def save(self, filepath):
        torch.save(self.model.state_dict(), filepath)

    def load(self, filepath):
        self.model.load_state_dict(torch.load(filepath))

