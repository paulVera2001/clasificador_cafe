import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
from keras.utils import load_img, img_to_array

modelo = None  # Evita cargarlo al inicio

def predecir_clase(imagen_path):
    global modelo
    if modelo is None:  # Cargar solo si aún no se ha cargado
        # Cargar el modelo una sola vez al inicio para evitar recargarlo en cada solicitud
        modelo = load_model("models/Modelo_clasificador_cafe_cnn_camPro_117a500muestrasParaCadaDefecto.h5")
        #print(modelo.summary())  
        
    """Carga la imagen y la pasa por el modelo para hacer la clasificación."""
    imagen = load_img(imagen_path, target_size=(200, 200))
    imagen_array = img_to_array(imagen)
    imagen_array = np.expand_dims(imagen_array, axis=0)
    
    prediccion = modelo.predict(imagen_array)
    
    clase_predicha = np.argmax(prediccion, axis=-1)[0] # Índice con mayor probabilidad
    
    return "Defectuoso" if clase_predicha==0 else "Normal"

