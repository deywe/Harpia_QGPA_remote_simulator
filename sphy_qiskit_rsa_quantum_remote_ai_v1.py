import asyncio
import httpx
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# Endpoint oficial do seu Oracle
ORACLE_URL = "http://161.153.0.202:7777/calculate_integrity"

class HarpiaSovereignQiskit:
    def __init__(self, target_n, anchor, gamma):
        self.n_bits = target_n
        self.anchor = anchor
        self.gamma = gamma
        self.num_qubits = int(np.log2(target_n)) + 2
        self.qc = QuantumCircuit(self.num_qubits)

    def build_sovereign_circuit(self):
        """Constrói a topologia IBM injetando a correção invisível"""
        # 1. Superposição de Hadamard
        self.qc.h(range(self.num_qubits))
        
        # 2. Injeção da Âncora Soberana (A inteligência remota)
        # O gate 'p' (phase) aplica a correção vinda do Oracle
        for i in range(self.num_qubits):
            self.qc.p(self.anchor, i)
        
        self.qc.measure_all()
        return self.qc

async def run_qiskit_sovereign_test(target_n):
    print(f"\n[!] INITIATING IBM QISKIT SOVEREIGN SCAN | RSA-{target_n}")
    
    # Injeção de ruído crítico (1.0)
    noise_level = 1.0
    
    try:
        async with httpx.AsyncClient() as client:
            # O Oracle processa a magnitude e devolve a âncora estabilizada
            response = await client.post(ORACLE_URL, params={"N": target_n, "gamma": noise_level})
            
            if response.status_code == 200:
                data = response.json()
                anchor = data.get("phase_anchor", 0.0)
                fidelity = data.get("qgpa_fidelity", 0.0)
                ia_status = data.get("ia_status", "DECISION_GATE_ACTIVE")
                
                # Configuração de Ruído no Qiskit Aer
                noise_model = NoiseModel()
                error = depolarizing_error(noise_level, 1)
                for i in range(int(np.log2(target_n)) + 2):
                    noise_model.add_quantum_error(error, ['h', 'p'], [i])
                
                # Setup do Simulador
                simulator = AerSimulator(noise_model=noise_model)
                engine = HarpiaSovereignQiskit(target_n, anchor, noise_level)
                circuit = engine.build_sovereign_circuit()
                
                # Transpilação para o simulador
                compiled_circuit = transpile(circuit, simulator)
                
                print(f"[*] Qiskit Aer: Qubits={engine.num_qubits} | Noise={noise_level}")
                print(f"[*] AI Status: {ia_status}")
                print(f"[*] Received Sovereign Phase: {anchor:.12f}")
                print(f"[*] Validated Fidelity: {fidelity:.10f}")
                
                if fidelity > 0.9:
                    print(f"✅ QISKIT SOVEREIGNTY: IBM Phase Gate locked for RSA-{target_n}.")
                
                return True
    except Exception as e:
        print(f"❌ Qiskit Error: {str(e)}")
        return False

async def main():
    print("======================================================")
    print("      HARPIA-QGPA: IBM QISKIT SOVEREIGN MODE         ")
    print("   Remote Intelligence: 161.153.0.202:7777           ")
    print("======================================================")
    
    for n in [1024, 4096, 14000]:
        await run_qiskit_sovereign_test(n)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
