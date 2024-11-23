# koopman/train_koopman.py

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from koopman.models import KoopmanModel
from koopman.dataset import KoopmanDataset

def custom_collate_fn(batch):
    batch_state = torch.stack([item['state'] for item in batch])
    batch_seq_len = torch.stack([item['seq_len'] for item in batch])
    max_seq_len = max([item['seq_len'] for item in batch])
    state_size = batch[0]['state'].shape[0]
    batch_next_states = torch.zeros(len(batch), max_seq_len, state_size)
    for i, item in enumerate(batch):
        seq_len = item['seq_len']
        batch_next_states[i, :seq_len] = item['next_states']
    return {'state': batch_state, 'next_states': batch_next_states, 'seq_len': batch_seq_len}

def train_koopman_model():
    state_size = 7  # Adjust accordingly
    lifted_size = 50
    batch_size = 32
    num_epochs = 100
    learning_rate = 1e-3

    dataset = KoopmanDataset(filepath='data/dataset.h5')
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=custom_collate_fn)

    model = KoopmanModel(state_size=state_size, lifted_size=lifted_size)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    model.train()
    for epoch in range(num_epochs):
        epoch_loss = 0.0
        for batch in dataloader:
            state = batch['state'].to(device)
            next_states = batch['next_states'].to(device)
            seq_len = batch['seq_len'].to(device)
            batch_size, max_seq_len, _ = next_states.shape

            optimizer.zero_grad()
            lifted_state = model(state)
            total_loss = 0.0

            for t in range(max_seq_len - 1):
                lifted_state = model.predict_next_lifted(lifted_state)
                reconstructed_state = model.reconstruct(lifted_state)
                actual_next_state = next_states[:, t+1, :]
                mask = (seq_len > t+1).float().unsqueeze(1).to(device)
                loss = criterion(reconstructed_state * mask, actual_next_state * mask)
                total_loss += loss

            total_loss.backward()
            optimizer.step()
            epoch_loss += total_loss.item()

        print(f"Epoch {epoch+1}/{num_epochs}, Loss: {epoch_loss/len(dataloader)}")

    torch.save(model.state_dict(), 'models/koopman_model.pth')

if __name__ == "__main__":
    train_koopman_model()

