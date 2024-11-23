# gym_betse/utils/data_storage.py

import os
import h5py
import numpy as np

class DataStorage:
    """
    Class for storing simulation data using HDF5.
    """
    def __init__(self, storage_path='data/', filename='dataset.h5', state_size=None, max_seq_length=50):
        self.storage_path = storage_path
        self.filename = filename
        self.filepath = os.path.join(self.storage_path, self.filename)
        self.state_size = state_size
        self.max_seq_length = max_seq_length
        self.initialize_storage()

    def initialize_storage(self):
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        self.h5file = h5py.File(self.filepath, 'a')
        if 'transitions' not in self.h5file:
            grp = self.h5file.create_group('transitions')
            maxshape = (None,)
            grp.create_dataset('state', shape=(0, self.state_size), maxshape=(None, self.state_size), dtype='float32', chunks=True)
            grp.create_dataset('action', shape=maxshape, maxshape=(None,), dtype='int32', chunks=True)
            grp.create_dataset('next_states', shape=(0, self.max_seq_length, self.state_size), maxshape=(None, self.max_seq_length, self.state_size), dtype='float32', chunks=True)
            grp.create_dataset('reward', shape=maxshape, maxshape=(None,), dtype='float32', chunks=True)
            grp.create_dataset('done', shape=maxshape, maxshape=(None,), dtype='bool', chunks=True)
            grp.create_dataset('seq_len', shape=maxshape, maxshape=(None,), dtype='int32', chunks=True)
        else:
            self.max_seq_length = self.h5file['transitions']['next_states'].shape[1]

    def store_transition(self, state, action, next_states, reward, done):
        grp = self.h5file['transitions']
        idx = grp['state'].shape[0]
        seq_len = next_states.shape[0]
        # Resize datasets
        grp['state'].resize((idx + 1, self.state_size))
        grp['action'].resize((idx + 1,))
        grp['next_states'].resize((idx + 1, self.max_seq_length, self.state_size))
        grp['reward'].resize((idx + 1,))
        grp['done'].resize((idx + 1,))
        grp['seq_len'].resize((idx + 1,))
        # Pad next_states
        padded_next_states = np.zeros((self.max_seq_length, self.state_size), dtype='float32')
        padded_next_states[:seq_len] = next_states
        # Store data
        grp['state'][idx] = state
        grp['action'][idx] = action
        grp['next_states'][idx] = padded_next_states
        grp['reward'][idx] = reward
        grp['done'][idx] = done
        grp['seq_len'][idx] = seq_len

    def close(self):
        self.h5file.close()

