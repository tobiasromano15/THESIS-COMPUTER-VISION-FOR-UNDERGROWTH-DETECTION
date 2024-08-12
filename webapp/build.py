import subprocess
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener las credenciales de Docker desde las variables de entorno
DOCKER_USERNAME = os.getenv('DOCKER_USERNAME')
DOCKER_PASSWORD = os.getenv('DOCKER_PASSWORD')

# Verificar que las credenciales se hayan cargado correctamente
if not DOCKER_USERNAME or not DOCKER_PASSWORD:
    raise ValueError("Docker username or password not found in environment variables")


def build_docker_image(script_name):
    # Iniciar sesión en Docker
    login_result = subprocess.run(['docker', 'login', '-u', DOCKER_USERNAME, '-p', DOCKER_PASSWORD],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if login_result.returncode != 0:
        print('Docker login failed:', login_result.stderr.decode('utf-8'))
        return

    # Define la ruta al Dockerfile correspondiente
    dockerfile_path = f'./{script_name}'

    # Verificar si el directorio existe
    if not os.path.isdir(dockerfile_path):
        print(f'Directory {dockerfile_path} does not exist')
        return

    # Construye la imagen Docker
    build_result = subprocess.run(['docker', 'build', '-t', script_name, dockerfile_path], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    if build_result.returncode != 0:
        print('Error building Docker image:', build_result.stderr.decode('utf-8'))
        return

    print(f'Docker image for {script_name} built successfully')


if __name__ == '__main__':
    script_name = input('Enter the script name to build Docker image (directory containing Dockerfile): ')
    build_docker_image(script_name)
