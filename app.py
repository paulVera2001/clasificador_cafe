from flask import Flask, render_template, request, session, jsonify, send_file
from models.modelo_clasificador import predecir_clase
from werkzeug.utils import secure_filename
import shutil
from pathlib import Path
import os
from fpdf import FPDF
from datetime import datetime

app = Flask(__name__, static_url_path='/static')

app.secret_key = 'clave_secreta'
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
    file = request.files["file"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    filepath = str(Path(filepath))
    file.save(filepath)
    resultado = predecir_clase(filepath)
    if 'history' not in session:
        session['history'] = []
    session['history'].append({'file': filepath, 'name': filename, 'result': resultado})
    session.modified = True
    return jsonify({"resultado": resultado}), 200

@app.route('/historial')
def historial():
    history = session.get('history', [])
    return render_template('historial.html', history=history)

@app.route('/borrar_historial', methods=['POST'])
def borrar_historial():
    session.pop('history', None)
    session.modified = True
    carpeta = os.path.join(app.root_path, 'static', 'uploads')
    shutil.rmtree(carpeta)
    os.makedirs(carpeta)
    return jsonify({"message": "Historial eliminado correctamente"}), 200

download_folder = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Sistema Clasificador de Granos de Cafe', ln=True, align='C')
        self.cell(0, 10, 'Historial', ln=True, align='C')
        self.set_font('Arial', '', 11)
        self.cell(0, 5, f'Fecha actual: {datetime.now().strftime("%d/%m/%Y")}', ln=True, align='R')
        self.ln(10)
        self.set_font('Arial', 'B', 10)
        self.set_x(15)  # Centrar tabla ajustando el margen izquierdo
        self.cell(40, 10, 'Imagen', 1, align='C')
        self.cell(100, 10, 'Nombre', 1, align='C')  # Incrementar el ancho de la columna 'Nombre'
        self.cell(40, 10, 'Resultado', 1, align='C')
        self.ln()

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', align='C')

@app.route('/exportar_pdf')
def export_pdf():
    pdf = PDF('P', 'mm', 'A4')  # PDF en formato A4
    pdf.set_auto_page_break(auto=True, margin=15)  # Márgenes inferiores
    pdf.add_page()
    pdf.set_font("Arial", "", 10)

    if 'history' in session:
        for item in session['history']:
            if pdf.get_y() > 260:
                pdf.add_page()
            pdf.set_x(15)  # Centrar tabla ajustando el margen izquierdo
            pdf.cell(40, 40, '', 1)  # Espacio para la imagen
            x = pdf.get_x() - 35  # Posición de la imagen
            y = pdf.get_y() + 5
            pdf.image(item['file'], x=x, y=y, w=30, h=30)
            pdf.set_xy(x + 35, y - 5)

            # Obtener ancho máximo y dividir el texto en líneas
            max_width = 100
            lines = pdf.multi_cell(max_width, 10, item['name'], border=0, align='C', split_only=True)

            # Calcular la altura total de las líneas
            text_height = len(lines) * 10

            # Determinar la altura final de la celda (mínimo 40)
            cell_height = max(40, text_height)

            # Dibujar el borde de la celda manualmente
            pdf.rect(x + 35, y - 5, max_width, cell_height)

            # Calcular posición para centrar el texto verticalmente
            start_y = y - 5 + (cell_height - text_height) / 2

            # Establecer posición inicial para multi_cell y escribir el texto
            pdf.set_xy(x + 35, start_y)
            pdf.multi_cell(max_width, 10, item['name'], border=0, align='C')

            # Mover la posición Y para la siguiente celda
            #pdf.set_y(y - 5)
            pdf.set_xy(x + 35 + max_width, y - 5)
            pdf.cell(40, 40, item['result'], 1, align='C')
            pdf.ln(40)

    pdf_path = os.path.join(download_folder, "historial_cafe.pdf")
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
