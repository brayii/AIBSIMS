#core/gnn_trainer.py

import torch
import torch.nn.functional as F

def train_gnn_policy(gnn, buffer, epochs=2):
    optimizer = torch.optim.Adam(gnn.parameters(), lr=1e-3)
    gnn.train()

    for epoch in range(epochs):
        total_loss = 0
        for sample in buffer:
            graph = sample["graph"]
            label = sample["label"]
            idx = sample["bunny_idx"]

            out = gnn(graph)[idx]

            # simple supervised loss: match FSM/RL expert behavior
            target = torch.tensor([
                label["move"],
                label["breed"],
                label["threat"]
            ], dtype=torch.float)

            loss = F.mse_loss(out, target)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        print(f"[GNN TRAIN] Epoch {epoch+1} loss: {total_loss:.4f}")

    gnn.eval()

