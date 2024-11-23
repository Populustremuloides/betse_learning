# koopman/models.py

import torch
import torch.nn as nn

class KoopmanModel(nn.Module):
    def __init__(self, state_size, lifted_size):
        super(KoopmanModel, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(state_size, 128),
            nn.ReLU(),
            nn.Linear(128, lifted_size)
        )
        self.K = nn.Parameter(torch.randn(lifted_size, lifted_size))
        self.decoder = nn.Sequential(
            nn.Linear(lifted_size, 128),
            nn.ReLU(),
            nn.Linear(128, state_size)
        )

    def forward(self, state):
        lifted_state = self.encoder(state)
        return lifted_state

    def predict_next_lifted(self, lifted_state):
        next_lifted_state = torch.matmul(lifted_state, self.K)
        return next_lifted_state

    def reconstruct(self, lifted_state):
        reconstructed_state = self.decoder(lifted_state)
        return reconstructed_state

