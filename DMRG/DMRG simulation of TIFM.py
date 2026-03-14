import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt

# Parameters
number_of_spins = 8
interaction_strength = 1.0
magnetic_field_range = np.linspace(0, 2, 21)

# Pauli Matrices
pauli_z = np.array([[1, 0], [0, -1]])
pauli_x = np.array([[0, 1], [1, 0]])
identity_2x2 = np.eye(2)

# Storage for plotting
list_of_fields = []
list_of_energies = []
list_of_order_params = []
list_of_entropies = []

print("\nDMRG (Lanczos) TFIM Simulation - Full Output\n")
header = (
    f"{'h':>6} | {'E0':>12} | {'Avg|Z|':>8} | {'M_corr':>8} | "
    f"{'S(mid)':>8} | {'top-ent (first 6)':>30}"
)
print(header)
print("-" * len(header))

# Sparse Hamiltonian Builder
def build_sparse_hamiltonian(L, J, h):
    system_dim = 2**L
    hamiltonian_sparse = sp.csr_matrix((system_dim, system_dim))
    
    # 1. ZZ Nearest-Neighbor Interaction
    for i in range(L - 1):
        operators = [identity_2x2] * L
        operators[i], operators[i+1] = pauli_z, pauli_z
        term = operators[0]
        for j in range(1, L):
            term = sp.kron(term, operators[j], format='csr')
        hamiltonian_sparse -= J * term
        
    # 2. Transverse X Field
    for i in range(L):
        operators = [identity_2x2] * L
        operators[i] = pauli_x
        term = operators[0]
        for j in range(1, L):
            term = sp.kron(term, operators[j], format='csr')
        hamiltonian_sparse -= h * term
        
    return hamiltonian_sparse

# Main Simulation Loop
for field_h in magnetic_field_range:
    H_sparse = build_sparse_hamiltonian(number_of_spins, interaction_strength, field_h)
    
    # Solve for Ground State using Lanczos (eigsh)
    # 'SA' finds the Smallest Algebraic eigenvalue
    energy_val, state_vec = eigsh(H_sparse, k=1, which='SA')
    ground_state = state_vec[:, 0]
    
    # Entanglement Entropy & Spectrum 
    mid_point = number_of_spins // 2
    psi_matrix = ground_state.reshape(2**mid_point, 2**mid_point)
    singular_values = np.linalg.svd(psi_matrix, compute_uv=False)
    singular_values = singular_values[singular_values > 1e-12]
    
    probabilities = singular_values**2
    entropy_val = -np.sum(probabilities * np.log(probabilities))
    
    # Entanglement Spectrum (-2 * log(s))
    ent_spectrum = np.sort(-2 * np.log(singular_values))
    spectrum_string = ", ".join(f"{v:.4f}" for v in ent_spectrum[:6])

    #  2. Calculate Order Parameter (M_corr) 
    # We compute the full sum of ZZ correlations
    total_zz_correlation = 0
    local_magnetizations = []
    
    for i in range(number_of_spins):
        # We need the local <Zi> for the table
        ops_i = [identity_2x2] * number_of_spins
        ops_i[i] = pauli_z
        zi_full = ops_i[0]
        for k in range(1, number_of_spins):
            zi_full = sp.kron(zi_full, ops_i[k], format='csr')
        
        mag_i = np.real(ground_state.conj().T @ (zi_full @ ground_state))
        local_magnetizations.append(mag_i)

        for j in range(number_of_spins):
            ops_ij = [identity_2x2] * number_of_spins
            ops_ij[i], ops_ij[j] = pauli_z, pauli_z
            zij_full = ops_ij[0]
            for k in range(1, number_of_spins):
                zij_full = sp.kron(zij_full, ops_ij[k], format='csr')
            total_zz_correlation += np.real(ground_state.conj().T @ (zij_full @ ground_state))

    order_param_m = np.sqrt(max(0, total_zz_correlation / (number_of_spins**2)))
    avg_abs_z = np.mean(np.abs(local_magnetizations))

    # Store results
    list_of_fields.append(field_h)
    list_of_energies.append(energy_val[0])
    list_of_order_params.append(order_param_m)
    list_of_entropies.append(entropy_val)

    print(
        f"{field_h:6.3f} | {energy_val[0]:12.6f} | {avg_abs_z:8.4f} | {order_param_m:8.4f} | "
        f"{entropy_val:8.4f} | {spectrum_string:>30}"
    )

# Plotting
plt.style.use("default") 
fig, axes = plt.subplots(3, 1, figsize=(8, 12), sharex=True)
fig.suptitle(f"DMRG/Lanczos Results for 1D TFIM (L={number_of_spins})", fontsize=14)

axes[0].plot(list_of_fields, list_of_energies, 'o-', color='black')
axes[0].set_ylabel("Ground State Energy")
axes[0].grid(True, linestyle='--')
axes[1].plot(list_of_fields, list_of_order_params, 's-', color='crimson')
axes[1].axvline(x=1.0, color='gray', linestyle=':', label='h=1')
axes[1].set_ylabel("Order Parameter $M_{corr}$")
axes[1].grid(True, linestyle='--')
axes[2].plot(list_of_fields, list_of_entropies, 'd-', color='royalblue')
axes[2].axvline(x=1.0, color='gray', linestyle=':')
axes[2].set_ylabel("Entanglement Entropy")
axes[2].set_xlabel("Transverse Field (h)")
axes[2].grid(True, linestyle='--')
plt.tight_layout(rect=[0, 0.03, 1, 0.96])
plt.show()
