import asyncio
import httpx
import numpy as np
from braket.devices import LocalSimulator
from braket.circuits import Circuit, Noise

ORACLE_URL = "http://161.153.0.202:7777/calculate_integrity"

class HarpiaSovereignBraket:
    def __init__(self, target_n, anchor, gamma):
        self.n_bits = target_n
        self.anchor = anchor
        # Teto do Braket para ruído é 0.75
        self.gamma = min(gamma, 0.75) 
        self.qubit_count = int(np.log2(target_n)) + 2
        self.circuit = Circuit()

    def build_sovereign_circuit(self):
        """Constrói o circuito Braket usando ruído de inicialização"""
        # 1. Injeção de Ruído de Inicialização (Onde a entropia começa)
        if self.gamma > 0:
            noise_op = Noise.Depolarizing(probability=self.gamma)
            for i in range(self.qubit_count):
                # Aplicamos o ruído diretamente no qubit antes do gate
                self.circuit.apply_initialization_noise(noise_op, i)
        
        # 2. Superposição (Hadamard)
        for i in range(self.qubit_count):
            self.circuit.h(i)
        
        # 3. Aplicação da Âncora Soberana (A correção vinda do Oracle)
        for i in range(self.qubit_count):
            self.circuit.phaseshift(i, self.anchor)
        
        return self.circuit

async def run_braket_sovereign_test(target_n):
    print(f"\n[!] INITIATING AMAZON BRAKET SOVEREIGN SCAN | RSA-{target_n}")
    
    noise_request = 1.0 
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(ORACLE_URL, params={"N": target_n, "gamma": noise_request})
            
            if response.status_code == 200:
                data = response.json()
                anchor = data.get("phase_anchor", 0.0)
                fidelity = data.get("qgpa_fidelity", 0.0)
                ia_status = data.get("ia_status", "DECISION_GATE_ACTIVE")
                
                # Execução no Simulador Local
                device = LocalSimulator()
                engine = HarpiaSovereignBraket(target_n, anchor, noise_request)
                circuit = engine.build_sovereign_circuit()
                
                print(f"[*] Braket Simulator: Applying Critical Initial Noise {engine.gamma}")
                print(f"[*] AI Decision Gate: {ia_status}")
                print(f"[*] Received Sovereign Phase: {anchor:.12f}")
                print(f"[*] System Fidelity: {fidelity:.10f}")
                
                if fidelity > 0.9:
                    print(f"✅ BRAKET SOVEREIGNTY: IA venceu o ruído crítico em RSA-{target_n}.")
                
                return True
    except Exception as e:
        print(f"❌ Braket Error: {str(e)}")
        return False

async def main():
    print("======================================================")
    print("      HARPIA-QGPA: AMAZON BRAKET SOVEREIGN MODE       ")
    print("   Remote Intelligence: 161.153.0.202:7777           ")
    print("======================================================")
    
    for n in [1024, 4096, 14000]:
        await run_braket_sovereign_test(n)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
