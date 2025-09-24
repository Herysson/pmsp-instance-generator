# Gerador de Cenários para Agendamento de Máquinas Paralelas

Este repositório contém um conjunto de scripts em Python para gerar instâncias de problemas de agendamento em máquinas paralelas com tempos de preparação dependentes da sequência. A metodologia de geração de dados é baseada no artigo científico:

> Kurz, M. E., & Askin, R. G. (2001). *Heuristic scheduling of parallel machines with sequence-dependent set-up times*. International Journal of Production Research, 39(16), 3747-3769.

O gerador é capaz de criar 128 tipos de cenários distintos, com um número configurável de réplicas (amostras) para cada um, salvando cada instância em um arquivo `.json` individual e autoexplicativo.

## Estrutura do Cenário

Cada um dos 128 cenários é definido por um código de 7 letras, onde `L` significa nível **Baixo (Low)** e `H` significa nível **Alto (High)**. A ordem das letras corresponde aos seguintes fatores do experimento:

| Posição | Fator                          | Nível Baixo (L)                 | Nível Alto (H)                  |
|:-------:|--------------------------------|---------------------------------|---------------------------------|
|    1    | Ready Times                    | Todas as tarefas em tempo 0     | Chegada dinâmica de tarefas     |
|    2    | Variabilidade do Processamento | Variação baixa (0.94x-1.06x µp) | Variação alta (0.4x-1.6x µp)    |
|    3    | Média do Processamento         | µp = µs (450)                   | µp = 10x µs (4500)              |
|    4    | Estrutura do Setup             | Simétrica                       | Assimétrica                     |
|    5    | Variabilidade do Setup         | Desvio padrão baixo             | Desvio padrão alto              |
|    6    | Número de Máquinas             | 2 máquinas                      | 10 máquinas                     |
|    7    | Média de Tarefas/Máquina       | 3 tarefas                       | 10 tarefas                      |

**Exemplo:** O código `LHHLLHL` representa um cenário com `Ready Times` baixos, `Var. Processamento` alta, `Média Processamento` alta, `Estrutura Setup` simétrica, `Var. Setup` baixa, `N. Máquinas` alta (10), e `Média Tarefas/Máquina` baixa (3).

## Como Usar

### Pré-requisitos
- Python 3.7 ou superior

### Passos para Execução

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
    cd seu-repositorio
    ```

2.  **(Recomendado) Crie e ative um ambiente virtual:**
    ```bash
    # No Windows
    python -m venv venv
    .\venv\Scripts\activate

    # No macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    O projeto utiliza as bibliotecas `numpy` e `tqdm`. Para instalá-las, execute:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o gerador:**
    O script `main.py` é o ponto de entrada. Você pode executá-lo de várias formas:

    * **Para gerar o conjunto de dados completo (128 cenários, 10 réplicas cada):**
        ```bash
        python main.py
        ```
        Isso criará uma pasta `instancias/` com 128 subpastas, contendo um total de 1280 arquivos `.json`.

    * **Para gerar apenas um tipo de cenário específico (ex: 10 réplicas de `LLLLLLL`):**
        ```bash
        python main.py --cenario LLLLLLL
        ```

    * **Para alterar o número de réplicas e a pasta de saída:**
        ```bash
        python main.py --replicas 5 --pasta_saida meus_dados
        ```

    * **Para ver todas as opções disponíveis:**
        ```bash
        python main.py --help
        ```

## Formato de Saída

Cada instância gerada é um arquivo `.json` com a seguinte estrutura:
```json
{
    "configuracao": {
        "codigo_cenario": "LLLLLLL",
        "nivel_ready_time": "baixa",
        "variabilidade_processamento": "baixa",
        "media_processamento": "baixa",
        "estrutura_setup": "simetrica",
        "variabilidade_setup": "baixa",
        "n_maquinas": 2,
        "n_medio_jobs_maquina": 3,
        "n_jobs": 6
    },
    "matriz_setup": [
        [ null, 415.89, 389.21, ... ],
        [ 415.89, null, 408.33, ... ],
        ...
    ],
    "tempos_processamento": [ 452.11, 438.9, 467.23, ... ],
    "ready_times": [ 0.0, 0.0, 0.0, ... ]
}
```
