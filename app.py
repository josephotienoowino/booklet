from flask import Flask, render_template, request, send_file, redirect, url_for
import os
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'

# Ensure upload and processed folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def create_booklet(input_pdf_path, output_pdf_path, pages_per_sheet):
    doc = fitz.open(input_pdf_path)
    output_doc = fitz.open()

    w, h = doc[0].rect.width, doc[0].rect.height

    # Calculate number of rows and columns based on pages_per_sheet
    if pages_per_sheet == 4:
        rows, cols = 2, 2
    elif pages_per_sheet == 8:
        rows, cols = 2, 4
    elif pages_per_sheet == 12:
        rows, cols = 3, 4
    else:
        raise ValueError("Unsupported pages per sheet")

    new_page = None
    cell_width = w / cols
    cell_height = h / rows
    page_count = 0

    for i, page in enumerate(doc):
        if page_count % pages_per_sheet == 0:
            new_page = output_doc.new_page(width=w, height=h)
        row = (page_count % pages_per_sheet) // cols
        col = (page_count % pages_per_sheet) % cols

        rect = fitz.Rect(
            col * cell_width,
            row * cell_height,
            (col + 1) * cell_width,
            (row + 1) * cell_height
        )

        new_page.show_pdf_page(rect, doc, i)
        page_count += 1

    output_doc.save(output_pdf_path)
    output_doc.close()
    doc.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return redirect(request.url)
        file = request.files['pdf_file']
        if file.filename == '':
            return redirect(request.url)

        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            pages_per_sheet = int(request.form.get('pages_per_sheet', 4))
            output_filename = 'booklet_' + filename
            output_filepath = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)

            create_booklet(filepath, output_filepath, pages_per_sheet)

            return send_file(output_filepath, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
