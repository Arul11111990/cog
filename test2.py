from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

def create_overlay(cog_x, cog_y, cog_z):
    overlay = "overlay.pdf"
    c = canvas.Canvas(overlay, pagesize=(842, 595))  # Default A4 size (width, height in points)

    # Customize font, size, and color
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)  # Black text

    # Coordinates to place text (adjust to fit template)
    c.drawString(550, 185, f"{cog_x:.2f}")
    c.drawString(620, 185, f"{cog_y:.2f}")
    c.drawString(690, 185, f"{cog_z:.2f}")

    c.save()
    return overlay

def merge_pdfs(base_pdf, overlay_pdf, output_pdf=r"C:\Users\arul.mohan\OneDrive - MKS VISION PVT LTD\Desktop\updated_template.pdf"):
    reader = PdfReader(base_pdf)
    overlay = PdfReader(overlay_pdf)
    writer = PdfWriter()

    # Assume adding overlay only on the first page
    for i, page in enumerate(reader.pages):
        if i == 0:  # Only on the first page
            page.merge_page(overlay.pages[0])
        writer.add_page(page)

    with open(output_pdf, "wb") as out_file:
        writer.write(out_file)

# Update COG values on a PDF template
base_pdf = r"C:\Users\arul.mohan\OneDrive - MKS VISION PVT LTD\Desktop\COG_VT_1.pdf"
cog_values = {'x': 1.23, 'y': 4.56, 'z': 7.89}  # Example values
overlay_pdf = create_overlay(cog_values['x'], cog_values['y'], cog_values['z'])
merge_pdfs(base_pdf, overlay_pdf)
print("PDF updated with combined COG values!")
