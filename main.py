import os
import hough2
from pruebasviejas import dividirimagenes
from concurrent.futures import ProcessPoolExecutor
import dilatacion


def generate_with_lines_filename(file_path):
    # Divide la ruta en directorio, nombre base, y extensión
    directory, filename = os.path.split(file_path)
    name, ext = os.path.splitext(filename)

    # Crea el nuevo nombre de archivo agregando "with_lines" antes de la extensión
    new_filename = f"{name}_with_lines{ext}"

    # Combina el directorio con el nuevo nombre de archivo
    new_file_path = os.path.join(directory, new_filename)

    return new_file_path
def dilatation():
    imagenes = [os.path.join('subimagenes', f) for f in os.listdir('subimagenes') if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff'))]
    print(imagenes)
    with ProcessPoolExecutor() as executor:
        #resultados = list(executor.map(hough2.process_image_and_save, imagenes))
        resultados = list(executor.map(dilatacion.dilatacion, imagenes))
        #for filename in os.listdir('subimagenes'):
    #file_path = os.path.join('subimagenes/',filename)
    #hough.process_image_and_save(file_path,file_path)

def divide(file_path):
    dividirimagenes.dividir_y_guardar_subimagenes(file_path, 4, 2, 'subimagenes')
    dilatation()
def main(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            hough2.process_image_and_save(file_path)
            dilatacion.dilatacion(file_path)
            #unirimagenes.unir_subimagenes('subimagenes/',4,2,'result/imagen_unida.png')



if __name__ == "__main__":
    """    parser = argparse.ArgumentParser(description="Iterar sobre archivos en un directorio.")
    parser.add_argument('directory', type=str, help="Ruta del directorio a iterar")

    args = parser.parse_args()
    """
    #main(args.directory)
    main("C:/Users/Tobi/Desktop/TESIS/plantitas")