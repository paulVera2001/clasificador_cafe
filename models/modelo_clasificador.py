import tensorflow as tf
import numpy as np
from keras.utils import load_img, img_to_array

# Ruta del modelo entrenado
MODEL_PATH = "models/Modelo_clasificador_cafe_cnn_camPro_117a500muestrasParaCadaDefecto.h5"

# Cargar el modelo una sola vez al inicio para evitar recargarlo en cada solicitud
modelo = tf.keras.models.load_model(MODEL_PATH)
#print(modelo.summary())  # Verifica la estructura del modelo

def predecir_clase(imagen_path):
    """Carga la imagen y la pasa por el modelo para hacer la clasificación."""
    imagen = load_img(imagen_path, target_size=(200, 200))
    imagen_array = img_to_array(imagen)
    imagen_array = np.expand_dims(imagen_array, axis=0)
    
    prediccion = modelo.predict(imagen_array)
    
    clase_predicha = np.argmax(prediccion, axis=-1)[0] # Índice con mayor probabilidad
    
    return "Defectuoso" if clase_predicha==0 else "Normal"

