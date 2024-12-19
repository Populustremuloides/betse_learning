# gym_betse/utils/betse_interface.py

from betse.science.wrapper import BetseWrapper
import yaml_friend as betseyaml
import shutil
from matplotlib import pyplot as plt
default_log = "config/experiment_log.txt"
class BetseSimulation:
    """
    Interface class for BETSE simulations.
    TODO: Write unit tests for these.
    TODO: Should a reward function be implemented here? I feel like it fits better in the agent code. Y'all decide.
    I did put a placeholder for it below, though, in very simple form.
    """
    config_path: str

    def __init__(self, config_path, initial_conditions=None, sim_exists=False, goal_state=None):
        self.config_path = config_path
        self.max_steps_per_action = 10  # Example value
        self.max_seq_length = 50  # Example value
        self.model = None
        self.load_simulation()
        self.parameters = betseyaml.get_param_list(self.config_path)
        self.action_log = [] # 2d array, each row is param values at beginning of each sim step
        self.steps_completed = 0

        if goal_state:
            self.goal_state = goal_state
        else:
            self.goal_state = 30 # example target vmem

        if initial_conditions:
            self.curr_action = betseyaml.gather_initial_values(initial_conditions, self.parameters)
            self.action_log.append(self.curr_action)
        else:
            self.curr_action = None

        # create working config
        shutil.copy(config_path, f"temp.yaml")
        self.working_config = "temp.yaml"

        # has simulation has already advanced to a certain point?
        self.sim_exists = sim_exists


    def load_simulation(self):
        if self.model is None:
            self.model = BetseWrapper(self.config_path, log_filename=default_log, log_level="NONE")
            self.model.run_seed(verbose=True)
            self.model.run_init(verbose=True)

    def reset(self):
        self.model = BetseWrapper(self.config_path, log_filename=default_log, log_level="NONE")
        self.model.run_seed(verbose=True)
        self.model.run_init(verbose=True)
        # TODO: probably ought to delete all folders that BETSE generates here

    # action is a vector of parameters given to us by RL- need to determine sim parameters,
    # decide order, and make sure it is consistent across all code
    def apply_action(self, action):
        # Save current config file as yaml and possibly additionally in an organized space
        #    - see also data saving functionality in betse_env
        # Apply action to the simulation
        # edits the config file in-place, no need to return a new file
        self.curr_action = action
        self.action_log.append(self.curr_action)
        betseyaml.update_yaml(self.working_config, self.parameters, self.curr_action, write_path=self.working_config)


    def step(self):
        # Advance simulation
        # run the next simulation with whatever the config file looks like right now
        self.model = BetseWrapper(self.working_config, log_filename=default_log, log_level="NONE")
        #TODO: Test to see if you need to load init here
        try:
            self.model.load_sim(verbose=True)
        except:
            self.model.run_sim(verbose=True)
        self.sim_exists = True
        self.steps_completed += 1


    def get_observation(self):
        # important to know here:
        """
        Taken from BETSE source code (betse/science/sim.py):

        vm_ave : ndarray
        One-dimensional Numpy array indexing each cell such that each item is
        the transmembrane voltage spatially situated at the centre of the cell
        indexed by that item for the current sampled time step.
    vm_ave_time : list
        Two-dimensional list of all transmembrane voltages averaged from all
        cell membranes onto cell centres over all sampled time steps, whose:

        #. First dimension indexes each sampled time step.
        #. Second dimension indexes each cell such that each item is the
           transmembrane voltage spatially situated at the centre of the cell
           indexed by that item for this time step.

           Equivalently, this array is the concatenation of all :attr:`vm_ave`
        arrays over all time steps.

        How and when we collect observations given these two data structures is up to us,
        and subject to some experimentation
        """
        # Get current state (Vmem)
        observation = self.model.phase.sim.vm_ave  # Replace with actual observation
        return observation


    #TODO: With our toy model with fixed action count, this function is not necessary yet
    #TODO: Also, where is my
    def get_num_actions(self) -> int:
        num_actions = 5  # Example value (number of discrete actions we allow the agent to take)
        return num_actions

    def get_observation_shape(self) -> int:
        shape = self.get_observation().shape() # Example for 7-cell system
        return shape

    def is_done(self) -> bool:
        #TODO: I believe the max_steps_per_action is the only stopping condition we need,
        #TODO: and in the scope of this toy model, max_steps_per_action will probably be 1
        #TODO: therefore this is probably fine for now.
        done = False
        return done

    def render(self, mode='human'):
        # Implement rendering if needed
        # optional: call betse's plot function
        #TODO: If we call the plot function, this may work:
        xc = self.model.phase.cells.cell_centres[:, 0]
        yc = self.model.phase.cells.cell_centres[:, 1]

        plt.figure()
        plt.tripcolor(xc, yc, self.model.phase.sim.vm_ave_time[-1], shading='gouraud') # idk what gouraud is
        plt.axis('equal')
        plt.colorbar()
        plt.show()
        #maybe save figs to config/RESULTS ?

    def close(self):
        # Clean up resources

        # delete working config
        shutil.rmtree(self.working_config)

        #TODO: BETSE's native cleanup procedures may suffice here
        pass

    def compute_goal_dist(self): # TODO: idk man, we're gonna have to get creative with this function if we want to incorporate masks n stuff.
        # sum of squared errors
        dist = 0
        for voltage in self.get_observation():
            dist += abs((voltage - self.goal_state))**2
        return dist


    # You all are my heroes. Good luck with this project! I'm jealous of the nobel prize winners you all will become.

