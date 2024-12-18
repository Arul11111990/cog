from flask import Flask, request, jsonify, render_template, send_file
import pyodbc
import fitz
import requests
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
    try:
        data = request.json
        vc_model = data['vc_model']
        vc_moc = data['vc_moc']
        vc_fill_type = data['vc_fill_type']
        vc_eliminators = data['vc_eliminators']
        vc_sweeper_piping = data['vc_sweeper_piping']
        vc_intake = data['vc_intake']
        vc_discharge = data['vc_discharge']

        connection = pyodbc.connect(
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
            r"DBQ=C:/Users/arul.mohan/OneDrive - MKS VISION PVT LTD/Documents/GitHub/cog/db/VT_COG.accdb;"
        )
        cursor = connection.cursor()

        tables = {
            'MOC_COG': ('MOC', vc_moc),
            'FILL_COG': ('FILLTYPE', vc_fill_type),
            'ELIM_COG': ('ELIMTYPE', vc_eliminators),
            'SWP_COG': ('SWP_PIPING', vc_sweeper_piping),
            'INTAKE_ATTN_COG': ('INTAKE_ATTN', vc_intake),
            'DIS_COG': ('DIS_ATTN', vc_discharge),
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
                'x': f"{weighted_cog['x'] / total_mass:.2f}",
                'y': f"{weighted_cog['y'] / total_mass:.2f}",
                'z': f"{weighted_cog['z'] / total_mass:.2f}",
            }
            return jsonify(combined_cog)
        else:
            return jsonify({'error': 'No data found'}), 404

    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        print(f"Unhandled exception: {e}")
        return jsonify({'error': str(e)}), 500

    
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    
        data = request.json
        cog_x = data.get('x')
        cog_y = data.get('y')
        cog_z = data.get('z')

        

        print(f"Generating PDF with COG values: X={cog_x}, Y={cog_y}, Z={cog_z}")
    
    
        # Load the existing PDF template
        pdf_template_path = r"C:\Users\arul.mohan\OneDrive - MKS VISION PVT LTD\Desktop\COG_VT_1.pdf"
        # pdf_template_path="https://raw.githubusercontent.com/Arul11111990/cog/2856c748225974645b69daf696813fa17af6db92/template/COG_VT_1.pdf"

        # Fetch PDF template from GitHub
        """ pdf_template_url = "https://raw.githubusercontent.com/Arul11111990/cog/2856c748225974645b69daf696813fa17af6db92/template/COG_VT_1.pdf"
        response = requests.get(pdf_template_url)

        if response.status_code != 200:
            return jsonify({'error': 'PDF template not found'}), 404
        
        pdf_buffer = BytesIO(response.content)

        doc = fitz.open(pdf_buffer)"""
        
        pdf_buffer = BytesIO() 

        doc = fitz.open(pdf_template_path)
        page = doc[0]  # Assuming text is added to the first page
        
        # Set the page size explicitly (in points, 1 point = 1/72 inch)
        page_size = (842, 595)  # Width, Height in points (A4 landscape)

        # Define text and positions (adjust coordinates as needed)
        page.insert_text((550, 397.5), f"{cog_x}", fontsize=12)
        page.insert_text((620, 397.5), f"{cog_y}", fontsize=12)
        page.insert_text((690, 397.5), f"{cog_z}", fontsize=12)
        
        # Save the updated PDF into memory buffer
        pdf_output = BytesIO()
        doc.save(pdf_output)
        doc.close()
        pdf_output.seek(0)

        return send_file(pdf_output, as_attachment=True, download_name="Updated_COG_Report.pdf")

        """ # Save the updated PDF into memory buffer
        doc.save(pdf_buffer)
        doc.close()
        pdf_buffer.seek(0)

        return send_file(pdf_buffer, as_attachment=True, download_name="Updated_COG_Report.pdf")
 """
    

if __name__ == '__main__':
    app.run(debug=True)


