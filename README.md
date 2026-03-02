# Transverse-Field Ising Model Phase Scan (DMRG with Quimb)

This project studies the **1D Transverse-Field Ising Model (TFIM)** using
Density Matrix Renormalization Group (DMRG) with the `quimb` tensor network library.

The goal is to numerically observe the quantum phase transition by scanning the
transverse field strength and measuring:

- Ground state magnetization (order parameter)
- Entanglement entropy (quantum correlations)

---

## Model

The Hamiltonian of the 1D transverse-field Ising model is:

H = - J ∑ Zᵢ Zᵢ₊₁ - h ∑ Xᵢ

where:

- `J` is the nearest-neighbour coupling (set to 1.0)
- `h` is the transverse field strength
- `Zᵢ` and `Xᵢ` are Pauli operators

At zero temperature, this model exhibits a quantum phase transition at:

h = 1  (for J = 1)

- For h < 1 → Ferromagnetic (ordered phase)
- For h > 1 → Paramagnetic (disordered phase)

---

## What the Code Does

1. Builds the TFIM Hamiltonian as a Matrix Product Operator (MPO).
2. Runs DMRG to approximate the ground state as a Matrix Product State (MPS).
3. Computes:
   - Average Z-magnetization across all sites
   - Entanglement entropy at the center bond
4. Repeats for different values of the transverse field `h`.
5. Plots magnetization and entropy versus `h`.

---

## Parameters

Inside the script:

```python
L = 40                       # Number of lattice sites
h_values = np.linspace(0, 2, 20)
