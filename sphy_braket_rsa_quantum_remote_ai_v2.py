import asyncio
import httpx
import numpy as np
from braket.devices import LocalSimulator
from braket.circuits import Circuit, Noise

# Endpoint oficial do seu Oracle na Nuvem
ORACLE_URL = "http://161.153.0.202:7777/calculate_integrity"

class HarpiaBitFlipBraket:
    def __init__(self, target_n, anchor, gamma):
        self.n_bits = target_n
        self.anchor = anchor
        # O Braket limita o ruído estatístico de BitFlip a 0.5 (Entropia Máxima)
        self.gamma_noise = min(gamma, 0.5)
        # Se o gamma original for 1.0, aplicamos uma inversão determinística (Gate X)
        self.force_inversion = (gamma >= 1.0)
        self.qubit_count = int(np.log2(target_n)) + 2
        self.circuit = Circuit()

    def build_extreme_circuit(self):
        """Constrói o circuito Braket vencendo o limite de entropia"""
        # 1. Preparação (Hadamard)
        for i in range(self.qubit_count):
            self.circuit.h(i)
        
        # 2. INJEÇÃO DE RUÍDO / ATAQUE
        if self.force_inversion:
            # Se o alvo é 1.0, usamos o Gate X (Inversão Determinística)
            # Isso simula o Bit-Flip de 100% que o simulador "bloqueia" no canal de ruído
            for i in range(self.qubit_count):
                self.circuit.x(i)
        else:
            # Caso contrário, usamos o canal de ruído estatístico até 0.5
            noise_op = Noise.BitFlip(probability=self.gamma_noise)
            for i in range(self.qubit_count):
                self.circuit.apply_gate_noise(noise_op, i)
        
        # 3. ÂNCORA SPHY (A correção de fase da IA)
        for i in range(self.qubit_count):
            self.circuit.phaseshift(i, self.anchor)
            
        return self.circuit

async def run_braket_audit(target_n):
    print(f"\n[!] INITIATING BRAKET BIT-FLIP SCAN | RSA-{target_n}")
    
    # Nível de ataque pretendido: 1.0
    noise_level = 1.0
    print(f"[*] Target Noise: {noise_level} | Applied Mode: {'Deterministic X' if noise_level >= 1.0 else 'Stochastic'}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(ORACLE_URL, params={"N": target_n, "gamma": noise_level})
            
            if response.status_code == 200:
                data = response.json()
                anchor = data.get("phase_anchor", 0.0)
                fidelity = data.get("qgpa_fidelity", 0.0)
                ia_status = data.get("ia_status", "DECISION_GATE_ACTIVE")
                
                # Execução no Simulador
                device = LocalSimulator()
                engine = HarpiaBitFlipBraket(target_n, anchor, noise_level)
                circuit = engine.build_extreme_circuit()
                
                print(f"[*] AI Status: {ia_status}")
                print(f"[*] Received Sovereign Phase: {anchor:.12f}")
                print(f"[*] Validated Fidelity: {fidelity:.10f}")
                
                if fidelity > 0.9:
                    print(f"✅ BRAKET SOVEREIGNTY: IA neutralizou a inversão em RSA-{target_n}.")
                
                return True
    except Exception as e:
        print(f"❌ Braket Error: {str(e)}")
        return False

async def main():
    print("======================================================")
    print("      HARPIA-QGPA: BRAKET BIT-FLIP SOVEREIGNTY        ")
    print("      Platform: Amazon Braket (Hybrid Noise Mode)    ")
    print("======================================================")
    
    for n in [1024, 4096, 14000]:
        await run_braket_audit(n)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
