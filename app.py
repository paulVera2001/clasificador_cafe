from flask import Flask, render_template, request, session, jsonify, send_file, url_for
from models.modelo_clasificador import predecir_clase
from werkzeug.utils import secure_filename
import os
import shutil
import pdfkit
from datetime import datetime
from pathlib import Path

app = Flask(__name__, static_url_path='/static')

app.secret_key = 'clave_secreta'  # Necesario para usar sesiones
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/main")
def main():
    return render_template("main.html")


@app.route("/clasificar", methods=["POST"])
def clasificar():
    """Maneja la carga de imágenes y clasificación."""
    file = request.files["file"]

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    filepath = str(Path(filepath))  # Asegura una ruta compatible con el SO. Cambia \ por /
    file.save(filepath)
    #print(f"Imagen guardada en: {filepath}")
    
    resultado = predecir_clase(filepath)

    #session.clear() #Borrar datos de sesion para pruebas en servidor local
    
    # Guardar en historial (sin base de datos)
    if 'history' not in session:
        session['history'] = []

    session['history'].append({'file': filepath, 'name': filename, 'result': resultado})
    session.modified = True
    
    return jsonify({"resultado": resultado}), 200


@app.route('/historial')
def historial():
    history = session.get('history', [])
    return render_template('historial.html', history=history)


@app.route('/exportar_pdf')
def exportar_pdf():
    history = session.get('history', [])
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    
    # Obtener el root path de la aplicación
    app_root_path = app.root_path.replace('\\', '/')
    
    # Renderizar historial_pdf.html con los datos
    rendered_html = render_template('historial_pdf.html', history=history, fecha_actual=fecha_actual, app_root_path=app_root_path)
    
    # Guardar HTMLs
    temp_html_path = os.path.join(app.static_folder, 'uploads', 'historial_pdf_rendered.html')
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)
    

    # Ruta del PDF de salida
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'historial.pdf')
    

    # Ruta de wkhtmltopdf para Windows, usa aveces \\ en lugar de /
    #config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    # Ruta de wkhtmltopdf para Linux, siempre usa /
    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')

    # Configuración para el PDF
    options = {
        "enable-local-file-access": ""
    }
    # Generar el PDF
    try:
        pdfkit.from_file(temp_html_path, pdf_path, configuration=config, options=options)
    except Exception as e:
        print(f"Error generando PDF: {e}")
    return send_file(pdf_path, as_attachment=True, download_name="historial.pdf")


@app.route('/borrar_historial', methods=['POST'])
def borrar_historial():
    session.pop('history', None)  # Elimina la variable de sesión 'history'
    session.modified = True # Asegura que se registre el cambio
    carpeta = os.path.join(app.root_path, 'static', 'uploads')
    shutil.rmtree(carpeta)  # Elimina la carpeta y todo su contenido
    os.makedirs(carpeta)  # Vuelve a crear la carpeta vacía
    
    return jsonify({"message": "Historial eliminado correctamente"}), 200


if __name__ == '__main__':
    app.run(debug=True)
