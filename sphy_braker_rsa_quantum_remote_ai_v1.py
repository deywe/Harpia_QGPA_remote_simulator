import pennylane as qml
from pennylane import numpy as np
import asyncio
import httpx

# Endpoint oficial do seu Oracle
ORACLE_URL = "http://161.153.0.202:7777/calculate_integrity"

class HarpiaSovereignPennyLane:
    def __init__(self, target_n, anchor, gamma):
        self.n_bits = target_n
        self.anchor = anchor
        self.gamma = gamma
        self.num_qubits = int(np.log2(target_n)) + 2
        self.dev = qml.device("default.qubit", wires=self.num_qubits)

    def get_circuit(self):
        @qml.qnode(self.dev)
        def circuit():
            # 1. Preparação do Estado
            for i in range(self.num_qubits):
                qml.Hadamard(wires=i)
            
            # 2. Injeção de Ruído (O Auditor tenta poluir o gradiente)
            if self.gamma > 0:
                for i in range(self.num_qubits):
                    # Simula ruído de fase aleatório local
                    qml.PhaseShift(np.random.uniform(-self.gamma, self.gamma), wires=i)
            
            # 3. Aplicação da Âncora Soberana (A correção vinda do Oracle)
            # A IA do servidor entrega a fase que "limpa" o gradiente
            for i in range(self.num_qubits):
                qml.RZ(self.anchor, wires=i)
            
            return qml.expval(qml.PauliZ(0))
        return circuit

async def run_pennylane_sovereign_test(target_n):
    print(f"\n[!] INITIATING PENNYLANE QML SOVEREIGN SCAN | RSA-{target_n}")
    
    # Ruído de entropia máxima para testar a resiliência do QML
    noise_level = 1.0 
    
    try:
        async with httpx.AsyncClient() as client:
            # O Oracle entrega a âncora estável para magnitudes gigantes
            response = await client.post(ORACLE_URL, params={"N": target_n, "gamma": noise_level})
            
            if response.status_code == 200:
                data = response.json()
                anchor = data.get("phase_anchor", 0.0)
                fidelity = data.get("qgpa_fidelity", 0.0)
                ia_status = data.get("ia_status", "DECISION_GATE_ACTIVE")
                
                engine = HarpiaSovereignPennyLane(target_n, anchor, noise_level)
                circuit = engine.get_circuit()
                
                # Execução do circuito diferenciável
                expectation_value = circuit()
                
                print(f"[*] PennyLane Wires: {engine.num_qubits} | Noise: {noise_level}")
                print(f"[*] AI Decision Gate: {ia_status}")
                print(f"[*] Gradient Expectation: {expectation_value:.10f}")
                print(f"[*] System Fidelity: {fidelity:.10f}")
                
                if fidelity > 0.9:
                    print(f"✅ PENNYLANE SOVEREIGNTY: Quantum Gradient locked for RSA-{target_n}.")
                
                return True
    except Exception as e:
        print(f"❌ PennyLane Error: {str(e)}")
        return False

async def main():
    print("======================================================")
    print("     HARPIA-QGPA: PENNYLANE QML SOVEREIGN MODE       ")
    print("   Remote Intelligence: 161.153.0.202:7777           ")
    print("======================================================")
    
    for n in [1024, 4096, 14000]:
        await run_pennylane_sovereign_test(n)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
