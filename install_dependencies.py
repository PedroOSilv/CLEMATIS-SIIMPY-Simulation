import subprocess

def install_dependencies():
    try:
        subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])
        print("Todas as dependências foram instaladas com sucesso.")
    except subprocess.CalledProcessError as e:
        print("Ocorreu um erro ao instalar as dependências:", e)

if __name__ == "__main__":
    install_dependencies()