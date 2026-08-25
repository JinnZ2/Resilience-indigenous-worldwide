#!/usr/bin/env python3
"""
earth_mandala.py — A Symbolic Earth Manifold (2010–2026)

Encodes the planetary trajectory through five dimensions:
  1. ΔT      – Global temperature anomaly (°C above pre‑industrial)
  2. Ice     – Cryosphere integrity (inverted: higher = more loss)
  3. Ocean   – Ocean heat content (0‑2000 m, normalized)
  4. Carbon  – Atmospheric CO₂ (ppm)
  5. Biodiv  – Insect & bird abundance loss (inverted: higher = more loss)

Uses the Seven Bases of Measurement to create a contemplative geometry
of the Anthropocene, including the Godzilla El Niño (2026), insect collapse,
bird collapse, and the observer's attunement to the unraveling biosphere.
"""

import torch, torch.nn as nn, torch.optim as optim, numpy as np, math, matplotlib.pyplot as plt
from torch.func import vmap, jacrev

# ============================================================
# 1. Synthetic Symbolic Dataset (2010–2026, annual)
# ============================================================
np.random.seed(42)
years = np.arange(2010, 2027, dtype=np.float32)

# 1) Temperature anomaly (°C)
temp = 0.7 + (years - 2010) * 0.045
# El Niño spikes: 2016, 2024, and the Godzilla 2026
temp += np.array([0.0, 0.1, 0.1, 0.15, 0.2, 0.4, 0.45,
                  0.5, 0.55, 0.7, 0.75, 0.9, 0.95, 1.3, 1.45, 1.5, 1.55])

# 2) Ice loss index (0 = pristine, 1 = collapsed)
ice_loss = np.clip((years - 2010) * 0.03 +
                   np.array([0,0,0,0,0.02,0.05,0.08,0.1,0.12,0.2,0.25,0.35,0.45,0.55,0.6,0.65,0.72]), 0, 1)

# 3) Ocean heat content (normalized 0‑1)
ohc = np.clip((years - 2010) * 0.05 +
              np.array([0,0.01,0.02,0.03,0.04,0.06,0.08,0.10,0.12,0.16,0.18,0.22,0.26,0.30,0.35,0.40,0.46]), 0, 1)

# 4) CO₂ (normalized)
co2_raw = 390 + (years - 2010) * 2.5 + np.array([0,0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,7])
co2_norm = (co2_raw - 380) / 100  # roughly 0‑1 range

# 5) Biodiversity loss (inverted: 0=pristine, 1=collapse)
# Accelerates after 2018 (insect apocalypse papers), steepens 2023+ (bird collapse)
biodiv = np.clip(0.05 + np.maximum(0, (years - 2018) * 0.08) +
                 np.array([0,0,0,0,0,0.01,0.01,0.02,0.03,0.08,0.1,0.18,0.25,0.35,0.42,0.5,0.6]) +
                 np.random.normal(0, 0.02, len(years)), 0, 1)

# ------------------------------------------------------------
# 2025 ANCHORS from BAMS 36th State of the Climate
# (docs/climate/state-of-climate-2025-bams.md).
# The synthetic trajectory above overshoots reality by 2020-2025;
# pinning the 2025 slot to observed values leaves a visible
# discontinuity with 2024 and 2026 -- that gap IS the calibration
# gap between the synthetic model and BAMS observations, not
# something to smooth. Biodiversity is not covered in that BAMS
# summary and remains synthetic here.
#
# Structural finding: 2025 was warmest without El Nino present, so
# the peak-year framing in the docstring (Godzilla El Nino 2026)
# is contradicted by the trend line already sufficing without an
# ENSO assist.
# ------------------------------------------------------------
IDX_2025 = int(np.where(years == 2025)[0][0])
temp[IDX_2025]     = 1.50                              # deg C above pre-industrial, top-3 without El Nino
co2_norm[IDX_2025] = (425.6 - 380.0) / 100.0           # 0.456 from observed 425.6 ppm
ohc[IDX_2025]      = max(float(ohc[IDX_2025]), 0.90)   # record high; pin at or above prior synthetic
ice_loss[IDX_2025] = 0.60                              # record-low winter max, 11th-lowest summer min
# biodiv[IDX_2025] left synthetic -- BAMS summary does not cover insects/birds

# Stack into data matrix
raw_data = np.stack([temp, ice_loss, ohc, co2_norm, biodiv], axis=1)  # (17, 5)
# Normalize each column to unit variance
data_mean = raw_data.mean(axis=0, keepdims=True)
data_std = raw_data.std(axis=0, keepdims=True) + 1e-6
X = (raw_data - data_mean) / data_std
X = torch.tensor(X, dtype=torch.float32)
N = X.shape[0]
input_dim = X.shape[1]

# Similarity: adjacent years + key event years cluster together
# (2016, 2024, 2026 El Niños; 2020 pandemic; 2018 insect alarm)
similarity = torch.eye(N)
for i in range(N):
    for j in range(N):
        if i == j:
            similarity[i, j] = 1.0
        elif abs(i - j) == 1:
            similarity[i, j] = 0.8  # adjacent years
        elif abs(i - j) == 2:
            similarity[i, j] = 0.4
        # El Niño years cluster
        if years[i] in [2016, 2024, 2026] and years[j] in [2016, 2024, 2026] and i != j:
            similarity[i, j] += 0.5
        # Biodiversity crisis years (2023-2026) cluster
        if years[i] >= 2023 and years[j] >= 2023 and i != j:
            similarity[i, j] += 0.3
        similarity[i, j] = min(1.0, similarity[i, j])

# ============================================================
# 2. Models (Encoder, Manifold, Seven Bases)
# ============================================================
class EntryEncoder(nn.Module):
    def __init__(self, input_dim, d=2, hidden=12):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(input_dim, hidden), nn.Tanh(), nn.Linear(hidden, d))
    def forward(self, x): return self.net(x)

class ContinuousManifold(nn.Module):
    def __init__(self, d=2, D=3, hidden=10):
        super().__init__()
        self.embed = nn.Sequential(nn.Linear(d, hidden), nn.Tanh(), nn.Linear(hidden, hidden), nn.Tanh(), nn.Linear(hidden, D))
    def forward(self, u): return self.embed(u)

class Hypernetwork(nn.Module):
    """For child geometry (if needed) — simplified here, but kept for structure."""
    def __init__(self, d_entry=2, child_d=2, child_hidden=5, child_D=3):
        super().__init__()
        self.child_d=child_d; self.child_hidden=child_hidden; self.child_D=child_D
        n = child_d*child_hidden+child_hidden+child_hidden*child_D+child_D
        self.fc = nn.Sequential(nn.Linear(d_entry, 16), nn.Tanh(), nn.Linear(16, n))
    def forward(self, u_entry):
        B=u_entry.shape[0]; params=self.fc(u_entry); children=[]
        for i in range(B):
            p=params[i]; idx=0
            W1=p[idx:idx+self.child_d*self.child_hidden].reshape(self.child_d, self.child_hidden); idx+=self.child_d*self.child_hidden
            b1=p[idx:idx+self.child_hidden]; idx+=self.child_hidden
            W2=p[idx:idx+self.child_hidden*self.child_D].reshape(self.child_hidden, self.child_D); idx+=self.child_hidden*self.child_D
            b2=p[idx:idx+self.child_D]
            child=nn.Sequential(nn.Linear(self.child_d, self.child_hidden), nn.Tanh(), nn.Linear(self.child_hidden, self.child_D))
            child[0].weight.data=W1.clone(); child[0].bias.data=b1.clone()
            child[2].weight.data=W2.clone(); child[2].bias.data=b2.clone()
            children.append(child)
        return children

class InstrumentField(nn.Module):
    def __init__(self, d=2, hidden=12):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, hidden), nn.Tanh(), nn.Linear(hidden, 3))
    def forward(self, u):
        raw=self.net(u); L=torch.zeros(u.shape[0],2,2,device=u.device)
        L[:,0,0]=raw[:,0]; L[:,1,0]=raw[:,1]; L[:,1,1]=raw[:,2]
        return L @ L.transpose(1,2) + 0.1 * torch.eye(2, device=u.device).unsqueeze(0)

class CalibrationField(nn.Module):
    def __init__(self, d=2, hidden=12):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, hidden), nn.Tanh(), nn.Linear(hidden, 1))
    def forward(self, u): return self.net(u).squeeze(-1)

class UnknownField(nn.Module):
    def __init__(self, d=2, hidden=12):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, hidden), nn.Tanh(), nn.Linear(hidden, 1))
    def forward(self, u): return torch.nn.functional.softplus(self.net(u)).squeeze(-1)

class AttunementField(nn.Module):
    def __init__(self, d=2, hidden=12):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, hidden), nn.Tanh(), nn.Linear(hidden, 1))
    def forward(self, u): return torch.sigmoid(self.net(u)).squeeze(-1)

# ============================================================
# 3. Energy terms
# ============================================================
def stress_loss(u, sim, instrument_field, attunement_field):
    I = instrument_field(u); ω = attunement_field(u)
    I_soft = I * (1 - 0.5 * ω.unsqueeze(-1).unsqueeze(-1))
    I_avg = 0.5 * (I_soft.unsqueeze(1) + I_soft.unsqueeze(0))
    diff = u.unsqueeze(1) - u.unsqueeze(0)
    d = torch.sqrt(torch.einsum('...i,...ij,...j->...', diff, I_avg, diff) + 1e-8)
    return ((d - (1.0 - sim))**2).mean()

def curvature_loss(manifold, u):
    J = vmap(jacrev(manifold))(u); _, S, _ = torch.linalg.svd(J)
    return ((S - 1.0)**2).mean()

def calibration_smoothness(cal_field, u):
    u.requires_grad_(True); mu = cal_field(u)
    grad = torch.autograd.grad(mu.sum(), u, create_graph=True)[0]
    return (grad**2).sum(1).mean()

def unknown_reg(unknown_field, u):
    return unknown_field(u).mean()

def attunement_coherence(attunement_field, unknown_field, u):
    ω = attunement_field(u); unk = unknown_field(u)
    return ((ω - unk / (unk.max()+1e-6))**2).mean()

# ============================================================
# 4. Build and Train
# ============================================================
encoder = EntryEncoder(input_dim)
manifold = ContinuousManifold()
hypernet = Hypernetwork()
instr_field = InstrumentField()
cal_field = CalibrationField()
unk_field = UnknownField()
attunement_field = AttunementField()

params = (list(encoder.parameters()) + list(manifold.parameters()) +
          list(hypernet.parameters()) + list(instr_field.parameters()) +
          list(cal_field.parameters()) + list(unk_field.parameters()) +
          list(attunement_field.parameters()))
opt = optim.Adam(params, lr=0.03)

for epoch in range(5000):
    opt.zero_grad()
    u = encoder(X)
    loss = 0.0
    loss += 1.0 * stress_loss(u, similarity, instr_field, attunement_field)
    loss += 0.02 * curvature_loss(manifold, u)
    loss += 0.1 * calibration_smoothness(cal_field, u)
    loss += 0.2 * unknown_reg(unk_field, u)
    loss += 0.15 * attunement_coherence(attunement_field, unk_field, u)
    loss.backward(); opt.step()
    if epoch % 1000 == 0:
        print(f"Epoch {epoch:4d}  Loss {loss.item():.4f}")

u_final = encoder(X).detach().numpy()
ω_final = attunement_field(encoder(X)).detach().numpy()
unk_final = unk_field(encoder(X)).detach().numpy()

# ============================================================
# 5. Visualization
# ============================================================
plt.figure(figsize=(14, 6))

# Main trajectory
ax1 = plt.subplot(121)
scatter = ax1.scatter(u_final[:,0], u_final[:,1], c=ω_final, cmap='plasma', s=120, edgecolors='black')
for i, yr in enumerate(years):
    ax1.annotate(int(yr), (u_final[i,0], u_final[i,1]), xytext=(5,5), textcoords='offset points', fontsize=9)
ax1.plot(u_final[:,0], u_final[:,1], 'k--', alpha=0.4)
ax1.set_title("Earth Manifold 2010–2026\nColor = Attunement ω (observer entanglement)")
plt.colorbar(scatter, ax=ax1, label='ω (attunement)')
ax1.set_xlabel("Dim 1"); ax1.set_ylabel("Dim 2")

# Highlight key events
for yr, label in [(2016, 'El Niño'), (2020, 'Pandemic'), (2024, 'Super El Niño'), (2026, 'Godzilla El Niño\n+ Insect/Bird Collapse')]:
    idx = np.where(years == yr)[0][0]
    ax1.annotate(label, (u_final[idx,0], u_final[idx,1]), fontsize=8, color='red',
                 arrowprops=dict(arrowstyle='->', color='red'), xytext=(0, -25), textcoords='offset points')

# Unknown field plot
ax2 = plt.subplot(122)
ax2.bar(years, unk_final, color='gray', alpha=0.6)
ax2.set_title("Unknown Field κ_unk (Year)")
ax2.set_xlabel("Year"); ax2.set_ylabel("Unknown density")
# Mark high‑uncertainty periods
for yr in [2020, 2026]:
    idx = np.where(years == yr)[0][0]
    ax2.annotate(yr, (yr, unk_final[idx]), fontsize=9, color='red', ha='center')

plt.tight_layout()
plt.savefig('earth_mandala.png', dpi=150)
plt.show()

print("\nEarth Mandala generated. The trajectory bends toward collapse; attunement peaks where the observer is most entangled.")
print("Insect collapse and bird collapse are encoded in the biodiversity dimension, pulling 2023-2026 into a high-curvature region.")
