# Variational Quantum Eigensolver (VQE) Simulation of the Transverse Field Ising Model

This script implements a **Variational Quantum Eigensolver (VQE)** to approximate the **ground state of the 1D Transverse Field Ising Model (TFIM)** for different values of the transverse field strength `h`.

The simulation uses:

- **Qiskit** to build and simulate quantum circuits  
- **SciPy** for classical optimization  
- **NumPy** for numerical operations  
- **Matplotlib** for visualization  

The script computes:

- Ground state energy  
- Average magnetization  
- Correlation-based order parameter  
- Entanglement entropy  
- Entanglement spectrum  

---

# What is VQE?

The **Variational Quantum Eigensolver (VQE)** is a hybrid quantum–classical algorithm used to approximate the **lowest eigenvalue (ground state energy)** of a Hamiltonian.

The algorithm works as follows:

1. A **parameterized quantum circuit (ansatz)** prepares a quantum state.
2. The expectation value of the Hamiltonian is measured for that state.
3. A **classical optimizer** adjusts the circuit parameters to reduce the energy.
4. This process repeats until the energy stops decreasing.

This approach relies on the **variational principle**, which states:

$$ 
E(\psi) = \langle \psi | H | \psi \rangle \ge E_{ground}
$$

Meaning the expectation value of any trial state is always **greater than or equal to the true ground state energy**.

By minimizing this expectation value, we approximate the **ground state energy**.

---

# Why VQE is used here

The **Transverse Field Ising Model (TFIM)** is a fundamental model in condensed matter physics that exhibits a **quantum phase transition**.

The Hamiltonian is

$$ \[
H = -J \sum_i Z_i Z_{i+1} - h \sum_i X_i
\] $$

where

- $J$ is the interaction strength between neighbouring spins  
- $h$ is the transverse magnetic field  
- $Z_i Z_{i+1}$ describes the spin–spin interaction  
- $X_i$ represents the transverse field acting on each spin 

When $h$ is small, the system prefers aligned spins (**ferromagnetic phase**).  
When $h$ becomes large, the transverse field dominates (**paramagnetic phase**).

VQE allows us to approximate the **ground state for each value of $h$** and observe how:

- energy  
- magnetization  
- correlations  
- entanglement  

change as the system moves through the phase transition.

---

# Bootstrapping Optimization

Instead of randomly initializing parameters for every value of `h`, the script uses **bootstrapping**.

The optimized parameters obtained for one field value are used as the **initial guess for the next field value**.

Because the ground state varies smoothly with $h$, this greatly improves convergence.

Benefits:

- Faster optimization  
- More stable results  
- Reduced risk of getting trapped in poor local minima  

---

# Script Structure

## 1. System Parameters

```python
number_of_qubits = 8
interaction_strength = 1.0
transverse_field_range = np.linspace(0, 2, 21)
circuit_layers = 3
```

These parameters define the physical system.

- `number_of_qubits` → number of spins $L$  
- `interaction_strength` → coupling constant $J$
- `transverse_field_range` → values of $h$ to scan  
- `circuit_layers` → depth of the variational circuit  

The number of variational parameters is

```python
total_parameters = (1 + circuit_layers) * number_of_qubits
```

This corresponds to one rotation layer plus several repeated layers.

---

# 2. Constructing the TFIM Hamiltonian

```python
def build_tfim_hamiltonian(L, J, h):
```

This function constructs the TFIM Hamiltonian using **Pauli operators**.

Two types of terms are included:

### Interaction term

$$
J Z_i Z_{i+1}
$$

which couples neighbouring spins.

### Transverse field term

$$
h X_i
$$

which represents the external magnetic field acting on each spin.

The Hamiltonian is represented using **Qiskit's `SparsePauliOp`**, which efficiently stores Pauli operators.

---

# 3. Variational Ansatz Circuit

```python
def ansatz(angles, L, reps):
```

This function builds the **parameterized quantum circuit** used in VQE.

The structure of the circuit is:

### Initial rotation layer

Each qubit receives a rotation

```
RY(angle)
```

This prepares a flexible starting state.

### Repeated entangling blocks

Each block contains

1. **Entangling CNOT chain**

```
CX(0,1)
CX(1,2)
CX(2,3)
...
```

2. **Parameterized RY rotations**

```
RY(angle)
```

These layers allow the circuit to generate **entangled many-body quantum states**.

---

# 4. Energy Objective Function

```python
def energy_objective(angles, hamiltonian, L, reps):
```

This function calculates the **expectation value of the Hamiltonian** for a given set of circuit parameters.

Steps performed:

1. Build the ansatz circuit  
2. Convert the circuit into a **statevector**  
3. Compute  

$$
E = \langle \psi | H | \psi \rangle
$$

The optimizer repeatedly calls this function while searching for parameters that minimize the energy.

---

# 5. Observable Measurements

After finding the approximate ground state, the script calculates several observables.

```python
def compute_observables(quantum_state, L):
```

### Average Magnetization

$$
|Z| = \frac{1}{L} \sum_i |\langle Z_i \rangle|
$$

This measures how strongly spins align with the \(Z\)-axis.

---

### Correlation Order Parameter

$$
M_{corr} = \sqrt{\frac{1}{L^2} \sum_{ij} \langle Z_i Z_j \rangle}
$$

This captures long-range spin correlations.

If spins remain correlated across the system, this value stays large.

---

### Entanglement Entropy

The state is bipartitioned into two halves and singular values are computed.

$$
S = -\sum_i \lambda_i^2 \log(\lambda_i^2)
$$

Higher entropy means stronger quantum entanglement between the two halves.

---

### Entanglement Spectrum

The script also reports the **first six levels of the entanglement spectrum**, which provides deeper information about the internal structure of the quantum state.

---

# 6. Classical Optimization

The parameters of the circuit are optimized using

```
SLSQP (Sequential Least Squares Programming)
```

Key settings used:

```
maxiter = 2000
ftol = 1e-9
```

SLSQP is a gradient-based optimizer that performs well for smooth optimization problems with many parameters.

---

# Results

The following table shows the numerical results obtained from the VQE simulation.

| h | Energy E0 | Avg \|Z\| | M_corr | Entropy |
|---|---|---|---|---|
| 0.0 | -7.0000 | 0.9958 | 1.0000 | 0.0150 |
| 0.1 | -7.0250 | 0.9978 | 0.9981 | 0.0000 |
| 0.2 | -7.1000 | 0.9912 | 0.9923 | 0.0000 |
| 0.3 | -7.2265 | 0.9792 | 0.9819 | 0.0004 |
| 0.4 | -7.4047 | 0.9613 | 0.9667 | 0.0011 |
| 0.5 | -7.6372 | 0.9350 | 0.9449 | 0.0028 |
| 0.6 | -7.9339 | 0.0000 | 0.9090 | 0.6720 |
| 0.7 | -8.2957 | 0.0000 | 0.8577 | 0.6263 |
| 0.8 | -8.7337 | 0.0000 | 0.7832 | 0.5328 |
| 0.9 | -9.2491 | 0.0000 | 0.7032 | 0.4198 |
| 1.0 | -9.8266 | 0.0000 | 0.6418 | 0.3332 |
| 1.1 | -10.4486 | 0.0000 | 0.5973 | 0.2722 |
| 1.2 | -11.1028 | 0.0000 | 0.5643 | 0.2280 |
| 1.3 | -11.7812 | 0.0000 | 0.5390 | 0.1948 |
| 1.4 | -12.4781 | 0.0000 | 0.5190 | 0.1689 |
| 1.5 | -13.1895 | 0.0000 | 0.5029 | 0.1484 |
| 1.6 | -13.9126 | 0.0000 | 0.4897 | 0.1317 |
| 1.7 | -14.6452 | 0.0000 | 0.4785 | 0.1178 |
| 1.8 | -15.3855 | 0.0000 | 0.4691 | 0.1063 |
| 1.9 | -16.1324 | 0.0000 | 0.4610 | 0.0964 |
| 2.0 | -16.8847 | 0.0000 | 0.4540 | 0.0880 |

---

# Plot of Results

Insert the generated plot below.

![VQE TFIM Results](figures/vqe_TFIM.png)

The figure contains three panels:

1. **Ground State Energy vs Transverse Field**
2. **Order Parameter vs Transverse Field**
3. **Entanglement Entropy vs Transverse Field**

The peak in entanglement entropy near the critical region indicates the **quantum phase transition**.

---

# Key Observations

- Ground state energy decreases as the transverse field increases.
- The order parameter gradually decreases, indicating the loss of ferromagnetic order.
- Entanglement entropy peaks near the phase transition region.
- The system transitions from an ordered phase to a paramagnetic phase.

These results match the expected behaviour of the **transverse field Ising model**.

---

# Dependencies

Install required packages:

```
pip install numpy scipy matplotlib qiskit
```

---

# Running the Script

Run the program using

```
python VQE_diagonalization_of_TFIM.py
```

The script will print the numerical results and display the plots.

