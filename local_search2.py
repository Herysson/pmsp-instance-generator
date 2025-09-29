import copy
import json
import argparse

# --- 1. CARREGAMENTO E PREPARAÇÃO DOS DADOS ---

def carregar_instancia_de_json(caminho_arquivo):
    """
    Lê um arquivo de instância .json, converte as estruturas de dados e
    prepara os dados para o algoritmo, incluindo a criação da linha '0' da matriz de setup.
    """
    with open(caminho_arquivo, 'r') as f:
        dados = json.load(f)

    config = dados['configuracao']
    n_jobs = config['n_jobs']

    # Converte listas para dicionários com chaves de 1 a N_JOBS
    processing_times = {i + 1: val for i, val in enumerate(dados['tempos_processamento'])}
    release_dates = {i + 1: val for i, val in enumerate(dados['ready_times'])}
    
    # Converte a matriz (lista de listas) para um dicionário aninhado com chaves inteiras
    setup_matrix_dict = {}
    matriz_lista = dados['matriz_setup']
    for i in range(n_jobs):
        setup_matrix_dict[i + 1] = {}
        for j in range(n_jobs):
            valor = matriz_lista[i][j] if matriz_lista[i][j] is not None else 0
            setup_matrix_dict[i + 1][j + 1] = valor

    # Cria a linha '0' da matriz de setup (setup do estado inicial para a primeira tarefa)
    setup_matrix_dict['0'] = {}
    for j in range(1, n_jobs + 1):
        # O setup inicial para 'j' é o maior tempo de setup de qualquer outra tarefa para 'j'
        max_setup_to_j = 0
        for i in range(1, n_jobs + 1):
            if i == j: continue
            max_setup_to_j = max(max_setup_to_j, setup_matrix_dict[i][j])
        setup_matrix_dict['0'][j] = max_setup_to_j

    return config, processing_times, setup_matrix_dict, release_dates

# --- 2. FUNÇÕES DO ALGORITMO ---
def calculate_sequence_time(sequence, processing_times, setup_matrix, release_dates):
    """Calcula o tempo total de conclusão para uma dada sequência de tarefas em uma máquina."""
    completion_time = 0
    last_task = '0'
    if not sequence:
        return 0
    
    for task_id in sequence:
        start_time = max(completion_time, release_dates[task_id])
        setup_time = setup_matrix[last_task][task_id]
        proc_time = processing_times[task_id]
        completion_time = start_time + setup_time + proc_time
        last_task = task_id
        
    return completion_time

def solve_with_ffd(config, processing_times, setup_matrix, release_dates):
    """Gera uma solução inicial usando uma abordagem baseada em First Fit Decreasing (FFD)."""
    n_machines = config['n_maquinas']
    sorted_tasks = sorted(processing_times.keys(), key=lambda task: processing_times[task], reverse=True)
    
    machines = {m_id: [] for m_id in range(1, n_machines + 1)}
    
    for task_id in sorted_tasks:
        potential_times = {}
        for machine_id in machines:
            temp_sequence = machines[machine_id] + [task_id]
            potential_times[machine_id] = calculate_sequence_time(temp_sequence, processing_times, setup_matrix, release_dates)
        
        best_machine = min(potential_times, key=potential_times.get)
        machines[best_machine].append(task_id)
        
    return machines

def local_search(initial_sequences, config, processing_times, setup_matrix, release_dates):
    """Aplica a busca local (melhor vizinho) para tentar melhorar uma solução inicial."""
    current_solution = initial_sequences
    n_machines = config['n_maquinas']
    machine_ids = list(range(1, n_machines + 1))
    
    machine_times = {m_id: calculate_sequence_time(seq, processing_times, setup_matrix, release_dates) for m_id, seq in current_solution.items()}
    current_makespan = max(machine_times.values()) if machine_times else 0
    
    iteration = 0
    while True:
        iteration += 1
        best_neighbor_solution = None
        best_neighbor_makespan = current_makespan

        # (A lógica de busca nas vizinhanças 1, 2 e 3 permanece a mesma)
        # Vizinhança 1: Transferência
        for m_from in machine_ids:
            for m_to in machine_ids:
                if m_from == m_to: continue
                for i in range(len(current_solution[m_from])):
                    neighbor = copy.deepcopy(current_solution)
                    task_to_move = neighbor[m_from].pop(i)
                    neighbor[m_to].append(task_to_move)
                    neighbor_times = {m_id: calculate_sequence_time(seq, processing_times, setup_matrix, release_dates) for m_id, seq in neighbor.items()}
                    neighbor_makespan = max(neighbor_times.values())
                    if neighbor_makespan < best_neighbor_makespan:
                        best_neighbor_makespan = neighbor_makespan
                        best_neighbor_solution = neighbor
        
        # Vizinhança 2: Troca Inter-Máquinas
        for m1_idx in range(n_machines):
            for m2_idx in range(m1_idx + 1, n_machines):
                m1_id, m2_id = machine_ids[m1_idx], machine_ids[m2_idx]
                for i in range(len(current_solution[m1_id])):
                    for j in range(len(current_solution[m2_id])):
                        neighbor = copy.deepcopy(current_solution)
                        neighbor[m1_id][i], neighbor[m2_id][j] = neighbor[m2_id][j], neighbor[m1_id][i]
                        neighbor_times = {m_id: calculate_sequence_time(seq, processing_times, setup_matrix, release_dates) for m_id, seq in neighbor.items()}
                        neighbor_makespan = max(neighbor_times.values())
                        if neighbor_makespan < best_neighbor_makespan:
                            best_neighbor_makespan = neighbor_makespan
                            best_neighbor_solution = neighbor

        # Vizinhança 3: Troca Intra-Máquina
        for m_id in machine_ids:
            seq_len = len(current_solution[m_id])
            if seq_len < 2: continue
            for i in range(seq_len):
                for j in range(i + 1, seq_len):
                    neighbor = copy.deepcopy(current_solution)
                    neighbor[m_id][i], neighbor[m_id][j] = neighbor[m_id][j], neighbor[m_id][i]
                    neighbor_times = {m_id: calculate_sequence_time(seq, processing_times, setup_matrix, release_dates) for m_id, seq in neighbor.items()}
                    neighbor_makespan = max(neighbor_times.values())
                    if neighbor_makespan < best_neighbor_makespan:
                        best_neighbor_makespan = neighbor_makespan
                        best_neighbor_solution = neighbor
        
        # Lógica de atualização modificada
        if best_neighbor_solution is None:
            print("=> Ótimo local encontrado. Nenhuma melhoria adicional.")
            break
        else:
            makespan_anterior = current_makespan
            current_solution = best_neighbor_solution
            current_makespan = best_neighbor_makespan
            melhoria_iteracao = makespan_anterior - current_makespan
            
            # NOVO PRINT DE ITERAÇÃO
            print(f"=> Iteração {iteration}: Melhoria encontrada! Novo Makespan: {current_makespan:.2f} (Ganho: {melhoria_iteracao:.2f})")

    # NOVO RETORNO: Agora retorna o número de iterações também
    return current_solution, current_makespan, iteration

def calcular_ddlb(config, processing_times, setup_matrix, release_dates):
    """
    Calcula o Data Dependent Lower Bound (DDLB) com base na fórmula do artigo.
    DDLB = max(Limite_Carga_Trabalho, Limite_Caminho_Critico)
    """
    n_jobs = config['n_jobs']
    n_machines = config['n_maquinas']
    
    # --- Calcula o Limite 1: Carga de Trabalho Mínima ---
    soma_trabalho_minimo = 0
    for i in range(1, n_jobs + 1):
        # Encontra o menor setup saindo da tarefa i para qualquer outra tarefa j
        min_setup_de_i = min(setup_matrix[i][j] for j in range(1, n_jobs + 1) if i != j)
        soma_trabalho_minimo += processing_times[i] + min_setup_de_i
        
    limite_carga_trabalho = soma_trabalho_minimo / n_machines

    # --- Calcula o Limite 2: Caminho Crítico Mínimo ---
    max_caminho_critico = 0
    for i in range(1, n_jobs + 1):
        # A fórmula do artigo usa o setup mínimo *saindo* da tarefa i
        min_setup_de_i = min(setup_matrix[i][j] for j in range(1, n_jobs + 1) if i != j)
        
        caminho_critico_i = release_dates[i] + processing_times[i] + min_setup_de_i
        max_caminho_critico = max(max_caminho_critico, caminho_critico_i)
        
    # O DDLB é o maior dos dois limites calculados
    ddlb = max(limite_carga_trabalho, max_caminho_critico)
    
    return ddlb

# --- 3. ORQUESTRAÇÃO E EXECUÇÃO PRINCIPAL ---

def run_scenario_from_file(file_path):
    """Orquestra o processo: carregar, resolver e exibir resultados para um arquivo."""
    print("="*50)
    print(f"EXECUTANDO CENÁRIO DO ARQUIVO: {file_path}")
    print("="*50)
    
    try:
        config, proc_times, setup_mat, release_dts = carregar_instancia_de_json(file_path)
    except FileNotFoundError:
        print(f"ERRO: O arquivo '{file_path}' não foi encontrado.")
        return
    except Exception as e:
        print(f"ERRO ao carregar ou processar o arquivo: {e}")
        return

    # Gerar Solução Inicial
    print("\n[FASE 1: GERANDO SOLUÇÃO INICIAL COM FFD]")
    initial_solution = solve_with_ffd(config, proc_times, setup_mat, release_dts)
    initial_times = {m_id: calculate_sequence_time(seq, proc_times, setup_mat, release_dts) for m_id, seq in initial_solution.items()}
    makespan_initial = max(initial_times.values()) if initial_times else 0
    
    print("\n--- Solução Inicial Encontrada ---")
    for m_id, seq in initial_solution.items():
        print(f"Máquina {m_id}: Seq={seq}, Tempo={initial_times[m_id]:.0f}")
    print(f"Makespan Inicial: {makespan_initial:.2f}")

    # Aplicar Busca Local
    print("\n[FASE 2: APLICANDO BUSCA LOCAL PARA MELHORIA]")
    # ATUALIZAÇÃO: Captura o número de iterações retornado pela função
    final_solution, final_makespan, total_iteracoes = local_search(initial_solution, config, proc_times, setup_mat, release_dts)
    
    # Calcular DDLB
    ddlb = calcular_ddlb(config, proc_times, setup_mat, release_dts)
    ratio_ms_ddlb = final_makespan / ddlb if ddlb > 0 else 0
    
    # Exibir Resultado Final
    final_times = {m_id: calculate_sequence_time(seq, proc_times, setup_mat, release_dts) for m_id, seq in final_solution.items()}
    
    print("\n" + "="*50)
    print(f"RESULTADO FINAL PARA {config.get('codigo_cenario', 'Cenário Desconhecido')}")
    print("="*50)
    print("--- Solução Após Busca Local ---")
    for m_id, seq in final_solution.items():
        print(f"Máquina {m_id}: Seq={seq}, Tempo={final_times[m_id]:.0f}")
    
    # BLOCO DE MÉTRICAS ATUALIZADO
    print("\n--- Métricas de Avaliação ---")
    print(f"Makespan Final (MS): {final_makespan:.2f}")
    print(f"Limite Inferior (DDLB): {ddlb:.2f}")
    print(f"Razão MS/DDLB: {ratio_ms_ddlb:.4f}")
    print(f"Melhoria de Makespan sobre a solução inicial: {makespan_initial - final_makespan:.2f}")
    print(f"Quantidade de iterações realizadas: {total_iteracoes}")
    print("\n")

if __name__ == "__main__":
    # Configura o parser de argumentos para receber o caminho do arquivo
    parser = argparse.ArgumentParser(description="Resolve o Problema de Agendamento a partir de um arquivo de instância JSON.")
    
    # Define "caminho_arquivo" como um argumento posicional obrigatório
    parser.add_argument("caminho_arquivo", type=str, help="O caminho para o arquivo .json da instância do problema.")
    
    # Lê os argumentos fornecidos na linha de comando
    args = parser.parse_args()
    
    # Chama a função principal passando o caminho do arquivo lido
    run_scenario_from_file(args.caminho_arquivo)