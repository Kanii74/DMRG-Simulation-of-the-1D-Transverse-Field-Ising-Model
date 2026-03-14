import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from scipy.optimize import minimize

# Parameters
number_of_qubits = 8
interaction_strength = 1.0
transverse_field_range = np.linspace(0, 2, 21)
circuit_layers = 3  # Depth of the circuit
total_parameters = (1 + circuit_layers) * number_of_qubits 

print(f"\nAdvanced VQE TFIM (SLSQP + Bootstrapping)\n")

table_header = (
    f"{'h':>6} | {'E0':>12} | {'Avg|Z|':>8} | {'M_corr':>8} | "
    f"{'S(mid)':>8} | {'top-ent (first 6)':>30}"
)
print(table_header)
print("-" * len(table_header))

# Storage for plotting
list_of_fields = []
list_of_energies = []
list_of_order_parameters = []
list_of_entropies = []

# TIFM Hamiltonian
def build_tfim_hamiltonian(L, J, h):
    paulis, coefficients = [], []
    for i in range(L - 1):
        label = ["I"] * L
        label[i], label[i + 1] = "Z", "Z"
        paulis.append("".join(label))
        coefficients.append(-J)
    for i in range(L):
        label = ["I"] * L
        label[i] = "X"
        paulis.append("".join(label))
        coefficients.append(-h)
    return SparsePauliOp(paulis, coefficients)

# ansatz function (parameterized quantum circuit using rotation and entangling gates for optimization)
def ansatz(angles, L, reps):
    quantum_circuit = QuantumCircuit(L)
    parameter_index = 0

    # Initial rotation layer
    for i in range(L):
        quantum_circuit.ry(angles[parameter_index], i)
        parameter_index = parameter_index + 1

    # Entangling + Rotation layers
    for _ in range(reps):
        for i in range(L - 1):
            quantum_circuit.cx(i, i + 1)
        for i in range(L):
            quantum_circuit.ry(angles[parameter_index], i)
            parameter_index = parameter_index + 1
    return quantum_circuit

def energy_objective(angles, hamiltonian, L, reps):
    quantum_circuit = ansatz(angles, L, reps)
    quantum_state = Statevector.from_instruction(quantum_circuit)
    return np.real(quantum_state.expectation_value(hamiltonian))

def compute_observables(quantum_state, L):
    state_data = quantum_state.data
    pauli_z, identity = np.array([[1, 0], [0, -1]]), np.eye(2)
    
    # Helper for operators
    def build_operator(op, site):
        operator_list = [op if i == site else identity for i in range(L)]
        output_matrix = operator_list[0]
        for m in operator_list[1:]: output_matrix = np.kron(output_matrix, m)
        return output_matrix

    # Measurements
    magnetizations, z_operators = [], []
    for i in range(L):
        zi_matrix = build_operator(pauli_z, i)
        z_operators.append(zi_matrix)
        magnetizations.append(np.real(np.vdot(state_data, zi_matrix @ state_data)))
    
    average_magnetization = np.mean(np.abs(magnetizations))
    correlation_sum = sum(np.real(np.vdot(state_data, (z_operators[i] @ z_operators[j]) @ state_data)) for i in range(L) for j in range(L))
    correlation_order_parameter = np.sqrt(max(0, correlation_sum / (L ** 2)))

    # Entanglement Spectrum
    density_matrix_reshape = state_data.reshape(2**(L//2), 2**(L//2))
    singular_values = np.linalg.svd(density_matrix_reshape, compute_uv=False)
    singular_values = singular_values[singular_values > 1e-12]
    entanglement_entropy = -np.sum(singular_values**2 * np.log(singular_values**2))
    entanglement_spectrum = np.sort(-2 * np.log(singular_values))
    spectrum_string = ", ".join(f"{v:.4f}" for v in entanglement_spectrum[:6])

    return average_magnetization, correlation_order_parameter, entanglement_entropy, spectrum_string


# VQE Loop with Bootstrapping methodology

# Starting with a random guess for the first h value
optimized_angles = np.random.rand(total_parameters) * 0.1 

for field_strength in transverse_field_range:
    model_hamiltonian = build_tfim_hamiltonian(number_of_qubits, interaction_strength, field_strength)
    
    # SLSQP (Sequential Least Suares Programming) is robust for higher dimesnions as it is gradient-based 
    optimization_result = minimize(
        energy_objective,
        optimized_angles,
        args=(model_hamiltonian, number_of_qubits, circuit_layers),
        method="SLSQP",
        options={'maxiter': 2000, 'ftol': 1e-9}
    )
    
    # Update current_best_params for the NEXT value of h (Bootstrapping methodology)
    optimized_angles = optimization_result.x

    final_circuit = ansatz(optimization_result.x, number_of_qubits, circuit_layers)
    final_state = Statevector.from_instruction(final_circuit)
    avg_mag, m_corr, entropy, top_ent = compute_observables(final_state, number_of_qubits)

    # appending the values
    list_of_fields.append(field_strength)
    list_of_energies.append(optimization_result.fun)
    list_of_order_parameters.append(m_corr)
    list_of_entropies.append(entropy)

    print(f"{field_strength:6.3f} | {optimization_result.fun:12.6f} | {avg_mag:8.4f} | {m_corr:8.4f} | {entropy:8.4f} | {top_ent:>30}")

# Plots for Display
plt.style.use("ggplot")
fig, axes = plt.subplots(3, 1, figsize=(8, 12), sharex=True)

axes[0].plot(list_of_fields, list_of_energies, 'o-', color='black', label='VQE (SLSQP)')
axes[0].set_ylabel("Ground State Energy")
axes[0].set_title("VQE Results (Bootstrapped) for TIFM")
axes[1].plot(list_of_fields, list_of_order_parameters, 's-', color='crimson')
axes[1].set_ylabel("Order Parameter $M_{corr}$")
axes[2].plot(list_of_fields, list_of_entropies, 'd-', color='royalblue')
axes[2].set_ylabel("Entanglement Entropy")
axes[2].set_xlabel("Transverse Field h")
# Makes the background completely white and ensures labels aren't cutoff
plt.style.use("default") 
plt.tight_layout()
plt.show()
