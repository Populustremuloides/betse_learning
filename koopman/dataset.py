# koopman/dataset.py

import torch
from torch.utils.data import Dataset
import h5py

class KoopmanDataset(Dataset):
    def __init__(self, filepath='data/dataset.h5'):
        self.filepath = filepath
        self.h5file = h5py.File(self.filepath, 'r')
        self.transitions = self.h5file['transitions']
        self.length = self.transitions['state'].shape[0]

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        state = self.transitions['state'][idx]
        next_states = self.transitions['next_states'][idx]
        seq_len = self.transitions['seq_len'][idx]
        # Truncate to actual sequence length
        next_states = next_states[:seq_len]
        # Convert to tensors
        state = torch.tensor(state, dtype=torch.float32)
        next_states = torch.tensor(next_states, dtype=torch.float32)
        seq_len = torch.tensor(seq_len, dtype=torch.int64)
        return {'state': state, 'next_states': next_states, 'seq_len': seq_len}

    def close(self):
        self.h5file.close()

