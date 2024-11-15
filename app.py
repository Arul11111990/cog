from flask import Flask, request, jsonify, render_template, send_file
import pyodbc

from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate_cog', methods=['POST'])
def calculate_cog():
    data = request.json
    vc_model = data['vc_model']
    vc_moc = data['vc_moc']
    vc_fill_type = data['vc_fill_type']
    vc_eliminators = data['vc_eliminators']
    vc_sweeper_piping = data['vc_sweeper_piping']
    vc_intake = data['vc_intake']
    vc_discharge = data['vc_discharge']

    try:
        connection = pyodbc.connect(r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:/Users/arul.mohan/OneDrive - MKS VISION PVT LTD/Documents/GitHub/cog/db/VT_COG.accdb;")
        cursor = connection.cursor()

        tables = {
            
            'MOC_COG': ('MOC', vc_moc),
            'FILL_COG': ('FILLTYPE', vc_fill_type),
            'ELIM_COG': ('ELIMTYPE', vc_eliminators),
            'SWP_COG': ('SWP_PIPING', vc_sweeper_piping),
            'INTAKE_ATTN_COG': ('INTAKE_ATTN', vc_intake),
            'DIS_COG': ('DIS_ATTN', vc_discharge)
        }

        total_mass = 0
        weighted_cog = {'x': 0, 'y': 0, 'z': 0}

        for table, (param_col, param_val) in tables.items():
            query = f"SELECT COG_X, COG_Y, COG_Z, MASS FROM {table} WHERE ModelID = ? AND {param_col} = ?"
            cursor.execute(query, (vc_model, param_val))
            result = cursor.fetchone()

            if result:
                cog_x, cog_y, cog_z, mass = result
                weighted_cog['x'] += cog_x * mass
                weighted_cog['y'] += cog_y * mass
                weighted_cog['z'] += cog_z * mass
                total_mass += mass

        cursor.close()
        connection.close()

        if total_mass > 0:
            combined_cog = {
                'x': weighted_cog['x'] / total_mass,
                'y': weighted_cog['y'] / total_mass,
                'z': weighted_cog['z'] / total_mass
            }
            return jsonify(combined_cog)
        else:
            return jsonify({'error': 'No data found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    cog_x = data.get('cog_x')
    cog_y = data.get('cog_y')
    cog_z = data.get('cog_z')

    """ # Create a PDF in memory
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=letter) """
    
    

    """ pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 750, "COG Drawing Generator Results")
    pdf.drawString(100, 730, f"Combined COG Values:")
    pdf.drawString(120, 710, f"X: {cog_x}")
    pdf.drawString(120, 690, f"Y: {cog_y}")
    pdf.drawString(120, 670, f"Z: {cog_z}")

    # Additional details, if needed
    pdf.drawString(100, 640, "Thank you for using the COG Generator.")
    pdf.save()

    # Move the buffer pointer to the beginning
    pdf_buffer.seek(0)
 """
    
    """ pdf_template_path = "path/to/template.pdf"
    doc = fitz.open(pdf_template_path)
    
    # Select the first page to update values
    page = doc[0]

    # Define positions for text fields (x, y coordinates on the page)
    # Adjust these based on your template layout
    positions = {
        'cog_x': (550, 185),  # Example position for COG X
        'cog_y': (620, 185),  # Example position for COG Y
        'cog_z': (690, 185),  # Example position for COG Z
        
        
    }

    # Update text fields on the PDF
    page.insert_text(positions['cog_x'], f"COG X: {cog_x}", fontsize=12)
    page.insert_text(positions['cog_y'], f"COG Y: {cog_y}", fontsize=12)
    page.insert_text(positions['cog_z'], f"COG Z: {cog_z}", fontsize=12)

    # Save the updated PDF to a buffer
    pdf_buffer = BytesIO()
    doc.save(pdf_buffer)
    doc.close()
    pdf_buffer.seek(0)
 """
    # Load the existing PDF template
    pdf_template_path = r"C:\Users\arul.mohan\OneDrive - MKS VISION PVT LTD\Desktop\COG_VT_1.pdf"
    reader = PdfReader(pdf_template_path)
    writer = PdfWriter()

    # Get the first page
    page = reader.pages[0]

    # Update form fields
    form_fields = page.get("/Annots")
    for field in form_fields:
        if field.get("/T") == "cog_x":
            field.update({"/V": f"{cog_x}"})
        elif field.get("/T") == "cog_y":
            field.update({"/V": f"{cog_y}"})
        elif field.get("/T") == "cog_z":
            field.update({"/V": f"{cog_z}"})

    writer.add_page(page)

    # Save the updated PDF
    pdf_buffer = BytesIO()
    writer.write(pdf_buffer)
    pdf_buffer.seek(0)

    return send_file(pdf_buffer, as_attachment=True, download_name="Updated_COG_Report.pdf")

if __name__ == '__main__':
    app.run(debug=True)


