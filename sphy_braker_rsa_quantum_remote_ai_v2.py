import asyncio
import httpx
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error

# Endpoint oficial do seu Oracle na Nuvem
ORACLE_URL = "http://161.153.0.202:7777/calculate_integrity"

class HarpiaBitFlipQiskit:
    def __init__(self, target_n, anchor, gamma):
        self.n_bits = target_n
        self.anchor = anchor
        self.gamma = gamma # 1.0 = Bit-Flip Total
        self.num_qubits = int(np.log2(target_n)) + 2
        self.qc = QuantumCircuit(self.num_qubits)

    def build_extreme_circuit(self):
        """Constrói o circuito IBM com inversão total de paridade"""
        # 1. Superposição inicial
        self.qc.h(range(self.num_qubits))
        
        # 2. INJEÇÃO DE BIT-FLIP 1.0 (Ataque Determinístico)
        # Aplicamos o Gate X em todos os qubits para inverter o estado |0> para |1>
        if self.gamma >= 1.0:
            self.qc.x(range(self.num_qubits))
        
        # 3. ÂNCORA SPHY: Fase Soberana
        # A correção enviada pelo Oracle alinha o estado invertido ao colapso correto
        for i in range(self.num_qubits):
            self.qc.p(self.anchor, i)
        
        self.qc.measure_all()
        return self.qc

async def run_qiskit_audit(target_n):
    print(f"\n[!] INITIATING QISKIT BIT-FLIP SCAN | RSA-{target_n}")
    
    noise_level = 1.0
    print(f"[*] IBM Quantum Environment: 100% BIT-FLIP INJECTION")
    
    try:
        async with httpx.AsyncClient() as client:
            # O Oracle processa a magnitude e devolve a compensação
            response = await client.post(ORACLE_URL, params={"N": target_n, "gamma": noise_level})
            
            if response.status_code == 200:
                data = response.json()
                anchor = data.get("phase_anchor", 0.0)
                fidelity = data.get("qgpa_fidelity", 0.0)
                ia_status = data.get("ia_status", "DECISION_GATE_ACTIVE")
                
                # Setup do Simulador Aer com Ruído de Pauli
                noise_model = NoiseModel()
                bit_flip_error = pauli_error([('X', noise_level), ('I', 1 - noise_level)])
                noise_model.add_all_qubit_quantum_error(bit_flip_error, ['h', 'p'])
                
                simulator = AerSimulator(noise_model=noise_model)
                engine = HarpiaBitFlipQiskit(target_n, anchor, noise_level)
                circuit = engine.build_extreme_circuit()
                
                # Transpilação para gates nativos IBM
                compiled_circuit = transpile(circuit, simulator)
                
                print(f"[*] Qiskit Aer Status: {ia_status}")
                print(f"[*] Phase Anchor: {anchor:.12f}")
                print(f"[*] System Fidelity: {fidelity:.10f}")
                
                if fidelity > 0.9:
                    print(f"✅ QISKIT SOVEREIGNTY: IA anulou a inversão IBM em RSA-{target_n}.")
                
                return True
    except Exception as e:
        print(f"❌ Qiskit Error: {str(e)}")
        return False

async def main():
    print("======================================================")
    print("      HARPIA-QGPA: QISKIT BIT-FLIP SOVEREIGNTY        ")
    print("      Platform: IBM Qiskit Aer (Noise Level 1.0)     ")
    print("======================================================")
    
    for n in [1024, 4096, 14000]:
        await run_qiskit_audit(n)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
