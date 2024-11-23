# gym_betse/envs/betse_env.py

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from gym_betse.utils.betse_interface import BetseSimulation
from gym_betse.utils.data_storage import DataStorage

class BetseEnv(gym.Env):
    """
    Custom Gymnasium environment for BETSE simulations.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, config_path='config/betse_config.yml'):
        super(BetseEnv, self).__init__()

        # Initialize BETSE simulation
        self.simulation = BetseSimulation(config_path)

        # Define action and observation spaces
        self.action_space = spaces.Discrete(self.simulation.get_num_actions())
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=self.simulation.get_observation_shape(),
            dtype=np.float32
        )

        # Initialize data storage
        self.data_storage = DataStorage(
            state_size=self.observation_space.shape[0],
            max_seq_length=self.simulation.max_seq_length
        )

        # Other initialization
        self.current_state = None
        self.max_steps_per_action = self.simulation.max_steps_per_action

    def reset(self):
        self.simulation.reset()
        self.current_state = self.simulation.get_observation()
        return self.current_state, {}

    def step(self, action):
        # Apply action and collect sequence of states
        next_states = []
        self.simulation.apply_action(action)

        for _ in range(self.max_steps_per_action):
            self.simulation.step()
            state = self.simulation.get_observation()
            next_states.append(state)
            if self.simulation.is_done():
                break

        next_states = np.array(next_states)  # Shape: [seq_len, state_size]
        reward = self.compute_reward(next_states[-1])
        done = self.simulation.is_done()

        # Store transition
        self.data_storage.store_transition(
            state=self.current_state,
            action=action,
            next_states=next_states,
            reward=reward,
            done=done
        )

        # Update current state
        self.current_state = next_states[-1]

        return self.current_state, reward, done, False, {}

    def render(self, mode='human'):
        self.simulation.render(mode)

    def close(self):
        self.simulation.close()
        self.data_storage.close()

    def compute_reward(self, observation):
        # Implement your reward function
        reward = 0.0
        return reward

