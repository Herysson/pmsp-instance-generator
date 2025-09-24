import os
import itertools
import argparse  # Nova biblioteca para argumentos de linha de comando
from tqdm import tqdm  # Nova biblioteca para barras de progresso
from cenario import Cenario

def main(args):
    """
    Função principal que executa a geração em lote com base nos argumentos fornecidos.
    """
    print("--- Iniciando a Geração em Lote de Cenários ---")
    
    # Se um cenário específico foi solicitado, use apenas ele. Caso contrário, gere todos.
    if args.cenario:
        codigos_de_cenario = [args.cenario]
        print(f"Modo de geração: Apenas o cenário específico '{args.cenario}' será gerado.")
    else:
        niveis = ['L', 'H']
        combinacoes = itertools.product(niveis, repeat=7)
        codigos_de_cenario = [''.join(p) for p in combinacoes]
        print("Modo de geração: Todos os 128 cenários serão gerados.")

    total_instancias = len(codigos_de_cenario) * args.replicas
    print(f"Serão geradas {total_instancias} instâncias no total.")
    print(f"({len(codigos_de_cenario)} cenários distintos x {args.replicas} réplicas cada um).")
    print(f"Os arquivos serão salvos na pasta: '{args.pasta_saida}/'")
    
    input("\nPressione Enter para começar a geração...")

    # Usamos tqdm para criar uma barra de progresso para os cenários
    for codigo in tqdm(codigos_de_cenario, desc="Cenários"):
        caminho_cenario_dir = os.path.join(args.pasta_saida, codigo)
        os.makedirs(caminho_cenario_dir, exist_ok=True)

        # Loop interno para as réplicas (pode ter sua própria barra de progresso)
        for i in range(1, args.replicas + 1):
            try:
                cenario_obj = Cenario(codigo)
                
                # Chamamos com verbose=False para silenciar a saída
                cenario_obj.gerar_dados(verbose=False)
                
                nome_arquivo = f"{codigo}_{i}.json"
                caminho_completo = os.path.join(caminho_cenario_dir, nome_arquivo)
                
                # Chamamos com verbose=False para silenciar a saída
                cenario_obj.salvar_em_json(caminho_completo, verbose=False)

            except Exception as e:
                # Erros ainda serão impressos, o que é importante
                tqdm.write(f"\nERRO ao gerar a instância {i} para o cenário {codigo}: {e}")

    print("\n--- Geração em lote concluída com sucesso! ---")

if __name__ == "__main__":
    # Configura o parser de argumentos
    parser = argparse.ArgumentParser(description="Gerador de Cenários de Teste para Agendamento de Máquinas Paralelas.")
    
    parser.add_argument('--replicas', type=int, default=10,
                        help='Número de réplicas (amostras) a serem geradas para cada cenário.')
    
    parser.add_argument('--pasta_saida', type=str, default='instancias',
                        help='Nome da pasta principal onde as instâncias serão salvas.')
    
    parser.add_argument('--cenario', type=str, default=None,
                        help='Gera apenas um tipo de cenário específico (ex: LLLLLLL). Se não for fornecido, gera todos os 128.')

    args = parser.parse_args()
    main(args)