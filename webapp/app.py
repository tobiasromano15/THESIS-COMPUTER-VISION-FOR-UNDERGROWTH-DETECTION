from flask import Flask, send_file, jsonify
import subprocess
import os
import time

app = Flask(__name__)


@app.route('/run_script/<script_name>', methods=['GET'])
def run_script(script_name):
    # Define la ruta al Dockerfile correspondiente
    dockerfile_path = f'./{script_name}'

    # Construye la imagen Docker
    build_result = subprocess.run(['docker', 'build', '-t', script_name, dockerfile_path])
    if build_result.returncode != 0:
        return jsonify({'error': 'Error building Docker image'}), 500

    # Ejecuta el contenedor y monta el volumen para guardar la imagen generada
    run_result = subprocess.run(['docker', 'run', '--rm', '-v', f'{os.getcwd()}/output:/output', script_name])
    if run_result.returncode != 0:
        return jsonify({'error': 'Error running Docker container'}), 500

    # Asume que el script genera una imagen llamada 'output.png' en el directorio de trabajo
    image_path = f'./output/output.png'

    # Espera hasta que el archivo se haya generado
    timeout = 10  # Timeout de 10 segundos
    while timeout > 0:
        if os.path.exists(image_path):
            break
        time.sleep(1)
        timeout -= 1

    if not os.path.exists(image_path):
        return jsonify({'error': 'Generated image not found'}), 500

    # Devuelve la imagen generada
    return send_file(image_path, mimetype='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
