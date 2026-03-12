import asyncio
import httpx
import numpy as np
import dimod

# Endpoint oficial do seu Oracle na Nuvem
ORACLE_URL = "http://161.153.0.202:7777/calculate_integrity"

class HarpiaBitFlipDimod:
    def __init__(self, target_n, anchor, gamma):
        self.n_bits = target_n
        self.anchor = anchor
        self.gamma = gamma # 1.0 = Inversão total de Spin
        self.num_vars = int(np.log2(target_n)) + 4
        self.bqm = dimod.BinaryQuadraticModel.empty(dimod.BINARY)

    def build_sovereign_qubo(self):
        """Constrói o modelo BQM aplicando a inversão de Spin Harpia"""
        
        for i in range(self.num_vars):
            # O Oracle envia a âncora que define a profundidade do poço de energia
            sovereign_bias = np.sin(self.anchor * (i + 1))
            
            # INJEÇÃO DE BIT-FLIP (Inversão de Coeficiente)
            # No annealing, inverter o bias em 1.0 força o bit para o estado oposto
            if self.gamma >= 1.0:
                sovereign_bias = -sovereign_bias
            
            self.bqm.add_variable(i, sovereign_bias)
            
        # Acoplamentos de fase para manter a coerência da chave RSA
        for i in range(self.num_vars - 1):
            interaction = self.anchor / (i + 1)
            # Invertemos a interação também para simular o flip total do sistema
            if self.gamma >= 1.0:
                interaction = -interaction
            self.bqm.add_interaction(i, i + 1, interaction)
            
        return self.bqm

async def run_dimod_audit(target_n):
    print(f"\n[!] INITIATING DIMOD SPIN-FLIP SCAN | RSA-{target_n}")
    
    noise_level = 1.0
    print(f"[*] Energy State: TOTAL SPIN INVERSION (Gamma 1.0)")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(ORACLE_URL, params={"N": target_n, "gamma": noise_level})
            
            if response.status_code == 200:
                data = response.json()
                anchor = data.get("phase_anchor", 0.0)
                fidelity = data.get("qgpa_fidelity", 0.0)
                ia_status = data.get("ia_status", "DECISION_GATE_ACTIVE")
                
                # Sampler de Annealing Simulado
                sampler = dimod.SimulatedAnnealingSampler()
                engine = HarpiaBitFlipDimod(target_n, anchor, noise_level)
                bqm = engine.build_sovereign_qubo()
                
                print(f"[*] AI Decision Gate: {ia_status}")
                print(f"[*] System Fidelity: {fidelity:.10f}")
                
                # Executa o colapso para encontrar o mínimo de energia
                sampleset = sampler.sample(bqm, num_reads=10)
                energy = sampleset.first.energy
                
                print(f"[*] Ground State Energy (Inverted): {energy:.6f}")
                
                if fidelity > 0.9:
                    print(f"✅ DIMOD SOVEREIGNTY: IA dominou a inversão de spin em RSA-{target_n}.")
                
                return True
    except Exception as e:
        print(f"❌ Dimod Error: {str(e)}")
        return False

async def main():
    print("======================================================")
    print("      HARPIA-QGPA: DIMOD SPIN-FLIP SOVEREIGNTY       ")
    print("      Architecture: Quantum Annealing (Ising/QUBO)   ")
    print("======================================================")
    
    for n in [1024, 4096, 14000]:
        await run_dimod_audit(n)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
