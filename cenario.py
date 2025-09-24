# Arquivo: cenario.py

import numpy as np
import math
import json
import copy

# --- CONSTANTES E FATORES DO EXPERIMENTO ---
MEDIA_SETUP_BASE = 450
NIVEL_ALTO = 'alta'
NIVEL_BAIXO = 'baixa'
ESTRUTURA_SIMETrica = 'simetrica'
ESTRUTURA_ASSIMETrica = 'assimetrica'
FATORES_E_NIVEIS = {
    'ready_times': [NIVEL_BAIXO, NIVEL_ALTO],
    'variabilidade_processamento': [NIVEL_BAIXO, NIVEL_ALTO],
    'media_processamento': [NIVEL_BAIXO, NIVEL_ALTO],
    'estrutura_setup': [ESTRUTURA_SIMETrica, ESTRUTURA_ASSIMETrica],
    'variabilidade_setup': [NIVEL_BAIXO, NIVEL_ALTO],
    'n_maquinas': [2, 10],
    'n_medio_jobs_maquina': [3, 10]
}

class Cenario:
    """
    Representa uma instância completa de um problema de agendamento,
    encapsulando sua configuração e os dados gerados.
    """
    def __init__(self, codigo_cenario):
        """
        Construtor da classe. Cria um cenário com base em um código de 7 letras.

        Parâmetros:
            codigo_cenario (str): 
                Um código de 7 letras onde L=Baixo (Low) e H=Alto (High).
                A ordem das letras é a seguinte:
                1. Ready Times
                2. Var. Processamento
                3. Média Processamento
                4. Estrutura Setup (L=Simétrica, H=Assimétrica)
                5. Var. Setup
                6. N. Máquinas
                7. Média Jobs/Máquina
        """
        if len(codigo_cenario) != 7 or not all(c in 'LHlh' for c in codigo_cenario):
            raise ValueError("O código do cenário deve ter 7 letras (L/H).")
        
        self.codigo = codigo_cenario.upper()
        self._configurar_atributos()
        
        self.matriz_setup = None
        self.tempos_processamento = None
        self.ready_times = None

    def _configurar_atributos(self):
        letras = [0 if letra == 'L' else 1 for letra in self.codigo]
        self.nivel_ready_time = FATORES_E_NIVEIS['ready_times'][letras[0]]
        self.variabilidade_processamento = FATORES_E_NIVEIS['variabilidade_processamento'][letras[1]]
        self.media_processamento = FATORES_E_NIVEIS['media_processamento'][letras[2]]
        self.estrutura_setup = FATORES_E_NIVEIS['estrutura_setup'][letras[3]]
        self.variabilidade_setup = FATORES_E_NIVEIS['variabilidade_setup'][letras[4]]
        self.n_maquinas = FATORES_E_NIVEIS['n_maquinas'][letras[5]]
        self.n_medio_jobs_maquina = FATORES_E_NIVEIS['n_medio_jobs_maquina'][letras[6]]
        self.n_jobs = self.n_maquinas * self.n_medio_jobs_maquina

    def gerar_dados(self, verbose=True): 
        self.matriz_setup = self._gerar_matriz_setup()
        self.tempos_processamento = self._gerar_tempos_processamento()
        self.ready_times = self._gerar_ready_times()
        
        if verbose:
            print(f"Dados para o cenário '{self.codigo}' gerados com sucesso.")

    def _gerar_matriz_setup(self):
        if self.variabilidade_setup == NIVEL_ALTO: sigma_s = (1.5 * MEDIA_SETUP_BASE) / 9
        else: sigma_s = 0.5 * ((1.5 * MEDIA_SETUP_BASE) / 9)
        min_time = MEDIA_SETUP_BASE - math.sqrt(3) * sigma_s
        max_time = MEDIA_SETUP_BASE + math.sqrt(3) * sigma_s
        matriz = np.zeros((self.n_jobs, self.n_jobs), dtype=np.float64)
        for i in range(self.n_jobs):
            for j in range(self.n_jobs):
                if i == j: matriz[i, j] = np.inf; continue
                simetrica = self.estrutura_setup == ESTRUTURA_SIMETrica
                if simetrica and i < j:
                    tempo = round(np.random.uniform(min_time, max_time), 2)
                    matriz[i, j], matriz[j, i] = tempo, tempo
                elif not simetrica:
                    matriz[i, j] = round(np.random.uniform(min_time, max_time), 2)
        return matriz

    def _gerar_tempos_processamento(self):
        mu_p = MEDIA_SETUP_BASE if self.media_processamento == NIVEL_BAIXO else 10 * MEDIA_SETUP_BASE
        if self.variabilidade_processamento == NIVEL_BAIXO: limites = (0.94 * mu_p, 1.06 * mu_p)
        else: limites = (0.4 * mu_p, 1.6 * mu_p)
        tempos = np.random.uniform(low=limites[0], high=limites[1], size=self.n_jobs)
        return np.round(tempos, 2)

    def _gerar_ready_times(self):
        if self.nivel_ready_time == NIVEL_BAIXO: return np.zeros(self.n_jobs)
        mu_p = MEDIA_SETUP_BASE if self.media_processamento == NIVEL_BAIXO else 10 * MEDIA_SETUP_BASE
        nm = self.n_jobs / self.n_maquinas
        if nm <= 1: return np.zeros(self.n_jobs)
        limite_superior = (nm - 1) * (mu_p + MEDIA_SETUP_BASE)
        tempos_gerados = np.random.uniform(low=0, high=limite_superior, size=self.n_jobs)
        return np.round(tempos_gerados - np.min(tempos_gerados), 2)

    def to_dict(self):
        if self.matriz_setup is None: self.gerar_dados()
        dados = {"configuracao": {"codigo_cenario": self.codigo,"nivel_ready_time": self.nivel_ready_time,"variabilidade_processamento": self.variabilidade_processamento,"media_processamento": self.media_processamento,"estrutura_setup": self.estrutura_setup,"variabilidade_setup": self.variabilidade_setup,"n_maquinas": self.n_maquinas,"n_medio_jobs_maquina": self.n_medio_jobs_maquina,"n_jobs": self.n_jobs},"matriz_setup": self.matriz_setup.tolist(),"tempos_processamento": self.tempos_processamento.tolist(),"ready_times": self.ready_times.tolist()}
        matriz = dados['matriz_setup']
        for i in range(len(matriz)):
            for j in range(len(matriz[i])):
                if matriz[i][j] == float('inf'): matriz[i][j] = None
        return dados

    def salvar_em_json(self, caminho_arquivo, verbose=True): # Adicionado o parâmetro verbose
        dados_para_salvar = self.to_dict()
        with open(caminho_arquivo, 'w') as f:
            json.dump(dados_para_salvar, f, indent=4)
        
        # Mensagem agora é condicional
        if verbose:
            print(f"Instância salva com sucesso em: {caminho_arquivo}")
        
    def __str__(self):
        return (f"<Cenario código='{self.codigo}' | Máquinas={self.n_maquinas}, Tarefas={self.n_jobs} | Dados {'Gerados' if self.matriz_setup is not None else 'Não Gerados'}>")