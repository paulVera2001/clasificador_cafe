

from flask import Flask, render_template, request, session, jsonify, send_file
from models.modelo_clasificador import predecir_clase
from werkzeug.utils import secure_filename
import os
import shutil
import pdfkit
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
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
    """Maneja la carga de imágenes, validaciones y clasificación."""
    if "file" not in request.files:
        return jsonify({"error": "No se envió ninguna imagen"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No se seleccionó ninguna imagen"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    filepath = str(Path(filepath))  # Asegura una ruta compatible con el SO
    #filepath = filepath.replace("\\", "/") 
    file.save(filepath)
    #print(f"Imagen guardada en: {filepath}")
    
    resultado = predecir_clase(filepath)

    #session.clear() #Borrar datos de sesion
    
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

    # Renderizar historial_pdf.html con los datos
    rendered_html = render_template('historial_pdf.html', history=history, fecha_actual=fecha_actual)

    # Guardar el HTML renderizado en un archivo temporal
    temp_html_path = os.path.join(app.config['UPLOAD_FOLDER'], 'historial_pdf_rendered.html')
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    # Renderizar header.html con la fecha actual
    rendered_header = render_template('header.html', fecha_actual=fecha_actual)
    temp_header_path = os.path.join(app.config['UPLOAD_FOLDER'], 'header_rendered.html')
    with open(temp_header_path, "w", encoding="utf-8") as f:
        f.write(rendered_header)

    # Ruta del PDF de salida
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'historial.pdf')

    # Ruta de wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

    # Configuración para el PDF
    options = {
        'enable-local-file-access': '',
        'header-html': temp_header_path,  # ✅ Usa el header personalizado
        'header-spacing': '5',
        'footer-right': 'Página [page] de [topage]',
        'footer-spacing': '5',
        'margin-top': '25mm',  # Ajusta espacio para el header
        'margin-bottom': '15mm',
        'page-size': 'A4',
        'dpi': 300
    }

    # Generar el PDF
    pdfkit.from_file(temp_html_path, pdf_path, configuration=config, options=options)

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
    port = int(os.environ.get("PORT", 5000))
    print(f"Ejecutando en el puerto: {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

#if __name__ == '__main__':
#    app.run(debug=True)
