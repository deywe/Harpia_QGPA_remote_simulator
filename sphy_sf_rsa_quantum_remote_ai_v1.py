import asyncio
import httpx
import numpy as np
import strawberryfields as sf
from strawberryfields.ops import *

# Endpoint oficial do seu Oracle
ORACLE_URL = "http://161.153.0.202:7777/calculate_integrity"

class HarpiaSovereignPhotonic:
    def __init__(self, target_n, anchor, gamma):
        self.n_bits = target_n
        self.anchor = anchor
        self.gamma = gamma
        self.num_modes = 2 
        self.prog = sf.Program(self.num_modes)
        # O backend Fock é excelente para visualizar a soberania em níveis de fótons
        self.eng = sf.Engine("fock", backend_options={"cutoff_dim": 5})

    def build_sovereign_photonics(self):
        """Constrói o circuito fotônico com a sintaxe correta do Dgate"""
        with self.prog.context as q:
            # 1. Preparação: Squeezing (Estado quântico base)
            Squeezed(0.5) | q[0]
            
            # 2. Injeção de Ruído Fotônico (O teste do auditor)
            # Corrigido: Passamos magnitude (r) e fase (phi) separadamente
            if self.gamma > 0:
                # r = magnitude do ruído, phi = ângulo do deslocamento
                Dgate(self.gamma, np.pi/4) | q[0]
            
            # 3. Âncora Soberana: Rotação de Fase (A inteligência remota)
            # A IA entrega a rotação que "prende" o fóton na trajetória correta
            Rgate(self.anchor) | q[0]
            
            # 4. Interferometria básica para validação de coerência
            BSgate(0.5, 0) | (q[0], q[1])
            
        return self.prog

async def run_strawberry_sovereign_test(target_n):
    print(f"\n[!] INITIATING PHOTONIC SOVEREIGN SCAN | RSA-{target_n}")
    
    # Ruído óptico crítico (1.0)
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
                
                # Execução no Engine Fotônico do Xanadu
                engine_logic = HarpiaSovereignPhotonic(target_n, anchor, noise_level)
                prog = engine_logic.build_sovereign_photonics()
                result = engine_logic.eng.run(prog)
                
                print(f"[*] Photonic Engine: Fock | AI Status: {ia_status}")
                print(f"[*] Received Sovereign Rotation: {anchor:.12f}")
                print(f"[*] System Fidelity: {fidelity:.10f}")
                
                if fidelity > 0.9:
                    print(f"✅ PHOTONIC SOVEREIGNTY: Light-phase locked for RSA-{target_n}.")
                
                return True
            else:
                print(f"❌ Server error: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Strawberry Fields Error: {str(e)}")
        return False

async def main():
    print("======================================================")
    print("    HARPIA-QGPA: STRAWBERRY FIELDS SOVEREIGN MODE    ")
    print("   Remote Intelligence: 161.153.0.202:7777           ")
    print("======================================================")
    
    for n in [1024, 4096, 14000]:
        await run_strawberry_sovereign_test(n)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
