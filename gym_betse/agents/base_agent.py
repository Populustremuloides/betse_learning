# gym_betse/agents/base_agent.py

class BaseAgent:
    """
    Base class for RL agents.
    """
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size

    def act(self, state):
        pass

    def step(self, state, action, reward, next_state, done):
        pass

    def save(self, filepath):
        pass

    def load(self, filepath):
        pass

