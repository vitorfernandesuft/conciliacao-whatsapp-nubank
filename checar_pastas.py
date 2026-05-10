dir
import os

def listar_estrutura(diretorio_pai, indentacao=0, pastas_ignoradas=None):
    if pastas_ignoradas is None:
        pastas_ignoradas = ['.venv', '__pycache__', '.git', '.vscode']
    
    # Lista o conteúdo do diretório
    try:
        itens = os.listdir(diretorio_pai)
    except PermissionError:
        return

    for item in itens:
        caminho_completo = os.path.join(diretorio_pai, item)
        
        # Verifica se deve ignorar a pasta
        if item in pastas_ignoradas:
            print('  ' * indentacao + f'|-- {item}/ (conteúdo ignorado)')
            continue

        if os.path.isdir(caminho_completo):
            print('  ' * indentacao + f'|-- {item}/')
            # Se for a pasta de mídias, não listamos os arquivos individuais (são milhares)
            if item == 'midias':
                print('  ' * (indentacao + 1) + '|-- [milhares de arquivos de imagem e cache]')
            else:
                listar_estrutura(caminho_completo, indentacao + 1, pastas_ignoradas)
        else:
            # Lista apenas arquivos relevantes (scripts, configurações e docs)
            if item.endswith(('.py', '.toml', '.lock', '.txt', '.xlsx', '.pdf', '.gitignore')):
                print('  ' * indentacao + f'|-- {item}')

if __name__ == "__main__":
    # Roda no diretório atual
    print(f"Estrutura de: {os.path.abspath(os.getcwd())}\n")
    listar_estrutura('.')
