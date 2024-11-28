# gym_betse/utils/betse_interface.py

class BetseSimulation:
    """
    Interface class for BETSE simulations.
    """
    def __init__(self, config_path):
        self.config_path = config_path
        self.max_steps_per_action = 10  # Example value
        self.max_seq_length = 50  # Example value
        self.load_simulation()

    def load_simulation(self):
        # Load BETSE simulation
        pass

    def reset(self):
        # Reset simulation
        pass

    # action is a vector of parameters given to us by RL- need to determine sim parameters,
    # decide order, and make sure it is consistent across all code
    def apply_action(self, action):
        # Save current config file as yaml and possibly additionally in an organized space
        #    - see also data saving functionality in betse_env
        # Apply action to the simulation
        # edits the config file in-place, no need to return a new file
        pass

    def step(self):
        # Advance simulation
        # run the next simulation with whatever the config file looks like right now
        pass

    def get_observation(self):
        # Get current state (Vmem)
        observation = None  # Replace with actual observation
        return observation

    def get_num_actions(self) -> int:
        num_actions = 5  # Example value (number of discrete actions we allow the agent to take)
        return num_actions

    def get_observation_shape(self) -> int:
        shape = (7,)  # Example for 7-cell system
        return shape

    def is_done(self) -> bool:
        done = False
        return done

    def render(self, mode='human'):
        # Implement rendering if needed
        # optional: call betse's plot function
        pass

    def close(self):
        # Clean up resources
        pass

