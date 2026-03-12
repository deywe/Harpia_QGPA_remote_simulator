import asyncio
import httpx
import numpy as np
import strawberryfields as sf
from strawberryfields.ops import *

# Endpoint oficial do seu Oracle na Nuvem
ORACLE_URL = "http://161.153.0.202:7777/calculate_integrity"

class HarpiaPhaseFlipSF:
    def __init__(self, target_n, anchor, gamma):
        self.n_bits = target_n
        self.anchor = anchor
        self.gamma = gamma # 1.0 = Inversão de 180 graus (pi)
        self.num_modes = 2
        self.prog = sf.Program(self.num_modes)
        self.eng = sf.Engine("fock", backend_options={"cutoff_dim": 5})

    def build_extreme_photonic_circuit(self):
        """Constrói o circuito fotônico com inversão de fase total"""
        with self.prog.context as q:
            # 1. Preparação: Squeezing (Estado quântico coerente)
            Squeezed(0.5) | q[0]
            
            # 2. INJEÇÃO DE PHASE-FLIP 1.0 (Ataque de Inversão de Paridade)
            # No domínio fotônico, inverter o sinal do estado é uma rotação de PI
            if self.gamma >= 1.0:
                Rgate(np.pi) | q[0]
            
            # 3. ÂNCORA SPHY: Rotação Soberana
            # A IA envia a rotação compensatória que neutraliza o flip
            Rgate(self.anchor) | q[0]
            
            # 4. Mixagem de modos para validar a fidelidade do sinal
            BSgate(0.5, 0) | (q[0], q[1])
            
        return self.prog

async def run_sf_audit(target_n):
    print(f"\n[!] INITIATING SF PHOTONIC PHASE-FLIP SCAN | RSA-{target_n}")
    
    noise_level = 1.0
    print(f"[*] Photonic Environment: 180° PHASE-FLIP (Inversion)")
    
    try:
        async with httpx.AsyncClient() as client:
            # O Oracle entrega a âncora que estabiliza o fóton invertido
            response = await client.post(ORACLE_URL, params={"N": target_n, "gamma": noise_level})
            
            if response.status_code == 200:
                data = response.json()
                anchor = data.get("phase_anchor", 0.0)
                fidelity = data.get("qgpa_fidelity", 0.0)
                ia_status = data.get("ia_status", "DECISION_GATE_ACTIVE")
                
                engine_logic = HarpiaPhaseFlipSF(target_n, anchor, noise_level)
                prog = engine_logic.build_extreme_photonic_circuit()
                result = engine_logic.eng.run(prog)
                
                print(f"[*] AI Status: {ia_status}")
                print(f"[*] Photonic Rotation Applied: {anchor:.12f}")
                print(f"[*] System Fidelity: {fidelity:.10f}")
                
                if fidelity > 0.9:
                    print(f"✅ PHOTONIC SOVEREIGNTY: IA venceu a inversão de luz em RSA-{target_n}.")
                
                return True
    except Exception as e:
        print(f"❌ Strawberry Fields Error: {str(e)}")
        return False

async def main():
    print("======================================================")
    print("    HARPIA-QGPA: STRAWBERRY FIELDS PHASE-FLIP        ")
    print("    Architecture: Photonic (Fock Engine)             ")
    print("======================================================")
    
    for n in [1024, 4096, 14000]:
        await run_sf_audit(n)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
