from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
import pyodbc
from PyPDF2 import PdfWriter, PdfReader
import tkinter as tk
from tkinter import ttk, messagebox

# SharePoint Credentials
sharepoint_url = "https://bacglobal.sharepoint.com/sites/NAEngineeringExternal"
folder_url = "/sites/NAEngineeringExternal/Series V  Part Matrix  PCG/VT0-VT1/test"
username = "amohan@ad.bac.work"  # Replace with your SharePoint username
password = "Happy_BAC@02"           # Replace with your SharePoint password

# Local Paths
local_accdb_path = "VT_COG.accdb"
local_pdf_path = "COG_VT_1.pdf"

# Function to download files from SharePoint
def download_file(ctx, server_relative_url, local_path):
    try:
        with open(local_path, "wb") as local_file:
            ctx.web.get_file_by_server_relative_url(server_relative_url).download(local_file).execute_query()
            print(f"Downloaded: {local_path}")
    except Exception as e:
        print(f"Error downloading {local_path}: {e}")

# Function to connect to ACCDB and fetch data
def connect_accdb(accdb_path):
    try:
        conn_str = (
            r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
            f"DBQ={accdb_path};"
        )
        conn = pyodbc.connect(conn_str)
        print("Connected to Access Database")
        return conn
    except Exception as e:
        print(f"Error connecting to ACCDB file: {e}")
        return None

# Function to append content to a PDF
def append_to_pdf(template_path, output_path, new_content_pdf):
    try:
        template = PdfReader(template_path)
        new_content = PdfReader(new_content_pdf)
        writer = PdfWriter()

        # Add Template Pages
        for page in template.pages:
            writer.add_page(page)

        # Add New Content
        for page in new_content.pages:
            writer.add_page(page)

        # Write to Output
        with open(output_path, "wb") as output:
            writer.write(output)
        print(f"PDF saved to {output_path}")
    except Exception as e:
        print(f"Error appending PDF: {e}")

# Main Function
def main(vc_model, vc_moc, vc_fill_type, vc_eliminators, vc_sweeper_piping, vc_intake, vc_discharge):
    try:
        # Step 1: Connect to SharePoint
        ctx = ClientContext(sharepoint_url).with_credentials(UserCredential(username, password))

        # Step 2: Download ACCDB and PDF Files
        download_file(ctx, f"{folder_url}/VT_COG.accdb", local_accdb_path)
        download_file(ctx, f"{folder_url}/COG_VT_1.pdf", local_pdf_path)

        # Step 3: Process ACCDB File
        conn = connect_accdb(local_accdb_path)
        if conn:
            cursor = conn.cursor()
            print("Fetching data from database:")
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

        for table, (parameter_column, parameter_value) in tables.items():
            query = f"SELECT COG_X, COG_Y, COG_Z, MASS FROM {table} WHERE ModelID = ? AND {parameter_column} = ?"
            cursor.execute(query, (vc_model, parameter_value))
            result = cursor.fetchone()

            if result:
                cog_x, cog_y, cog_z, mass = result
                weighted_cog['x'] += cog_x * mass
                weighted_cog['y'] += cog_y * mass
                weighted_cog['z'] += cog_z * mass
                total_mass += mass
            else:
                print(f"No data found for {parameter_value} in {table}.")
            
            
            cursor.close()
            conn.close()
            
            if total_mass > 0:
                combined_cog = {
                'x': weighted_cog['x'] / total_mass,
                'y': weighted_cog['y'] / total_mass,
                'z': weighted_cog['z'] / total_mass
                }
                return combined_cog
            else:
                return None
    except Exception as e:
        return f"Error: {str(e)}"

def display_combined_cog_details():
    vc_model = vc_model_var.get()
    vc_moc = vc_moc_var.get()
    vc_fill_type = vc_fill_type_var.get()
    vc_eliminators = vc_eliminators_var.get()
    vc_sweeper_piping = vc_sweeper_piping_var.get()
    vc_intake = vc_intake_var.get()
    vc_discharge = vc_discharge_var.get()

    if all([vc_model, vc_moc, vc_fill_type, vc_eliminators, vc_sweeper_piping, vc_intake, vc_discharge]):
        cog_values = main(vc_model, vc_moc, vc_fill_type, vc_eliminators, vc_sweeper_piping, vc_intake, vc_discharge)
        
        if isinstance(cog_values, dict):  
            result_label.config(text=f"Combined COG X: {cog_values['x']:.2f}, Y: {cog_values['y']:.2f}, Z: {cog_values['z']:.2f}")
            overlay_pdf = create_overlay(cog_values['x'], cog_values['y'], cog_values['z'])
            merge_pdfs(base_pdf, overlay_pdf)
            print("PDF updated with combined COG values!")
        else:
            messagebox.showerror("Data Error", cog_values)
    else:
        messagebox.showwarning("Input Error", "Please select all parameters.")

# Function to create dropdowns
def create_dropdown(label_text, options, variable):
    label = ttk.Label(frame, text=label_text, style="CustomLabel.TLabel")
    label.grid(row=len(frame.winfo_children()) // 2, column=0, pady=5, sticky="w")
    dropdown = ttk.Combobox(frame, textvariable=variable, values=options, state="readonly", width=20, style="CustomCombobox.TCombobox")
    dropdown.grid(row=(len(frame.winfo_children()) // 2) - 1, column=1, pady=5, sticky="w")

def create_overlay(cog_x, cog_y, cog_z):
    overlay = "overlay.pdf"
    c = canvas.Canvas(overlay, pagesize=(842, 595))  # A4 size (width, height in points)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(550, 185, f"{cog_x:.2f}")
    c.drawString(620, 185, f"{cog_y:.2f}")
    c.drawString(690, 185, f"{cog_z:.2f}")
    c.save()
    return overlay

def merge_pdfs(base_pdf, overlay_pdf, output_pdf=r"C:\Users\arul.mohan\OneDrive - MKS VISION PVT LTD\Documents\GitHub\cog\template\updated_template.pdf"):
    reader = PdfReader(base_pdf)
    overlay = PdfReader(overlay_pdf)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        if i == 0:
            page.merge_page(overlay.pages[0])
        writer.add_page(page)

    with open(output_pdf, "wb") as out_file:
        writer.write(out_file)

# Main GUI setup
app = tk.Tk()
app.title("COG Drg Gen_VT0/VT1")
app.geometry("320x350")
app.configure(bg="#f0f0f5")  # Light gray-blue background

# Apply ttk theme
style = ttk.Style()
style.theme_use("clam")
style.configure("CustomLabel.TLabel", font=("Helvetica", 10, "bold"), background="#f0f0f5")
style.configure("TButton", font=("Helvetica", 10, "bold"), background="#0066cc", foreground="white")
style.configure("CustomCombobox.TCombobox", font=("Helvetica", 10))

frame = ttk.Frame(app, padding=10)
frame.grid(row=0, column=0, padx=10, pady=10)

# Dropdown variables
vc_model_var = tk.StringVar(value="VC_MODEL")
vc_moc_var = tk.StringVar(value="MOC")
vc_fill_type_var = tk.StringVar(value="Fill Type")
vc_eliminators_var = tk.StringVar(value="Eliminators")
vc_sweeper_piping_var = tk.StringVar(value="Sweeper Piping")
vc_intake_var = tk.StringVar(value="Intake")
vc_discharge_var = tk.StringVar(value="Discharge")

# Define options for dropdowns (list shortened for example)
vc_models = ["VT0-012-E", "VT0-014-F", "VT0-019-G", "VT0-024-G", "VT0-028-H", "VT0-032-H", 
    "VT0-041-J", "VT0-052-J", "VT0-057-K", "VT0-065-J", "VT0-075-K", "VT0-078-K", 
    "VT0-088-L", "VT0-102-L", "VT0-107-L", "VT0-116-M", "VT0-132-L", "VT0-145-M", 
    "VT0-155-N", "VT0-166-N", "VT0-176-O", "VT1-1020-P", "VT1-1125-P", "VT1-1200-Q", 
    "VT1-1245-R", "VT1-1335-S", "VT1-275-P", "VT1-307-O", "VT1-340-P", "VT1-375-P", 
    "VT1-400-Q", "VT1-415-R", "VT1-416-O", "VT1-478-N", "VT1-507-O", "VT1-550-P", 
    "VT1-560-O", "VT1-600-P", "VT1-680-P", "VT1-750-P", "VT1-800-Q", "VT1-825-P", 
    "VT1-830-R", "VT1-921-O", "VT1-M1044-P", "VT1-M1050-O", "VT1-M1056-P", "VT1-M1113-P",
    "VT1-M1137-Q", "VT1-M1194-Q", "VT1-M1260-R", "VT1-M316-O", "VT1-M328-O", "VT1-M348-P", 
    "VT1-M350-O", "VT1-M352-P", "VT1-M371-P", "VT1-M379-Q", "VT1-M398-Q", "VT1-M420-R", 
    "VT1-M431-N", "VT1-M455-O", "VT1-M484-N", "VT1-M514-O", "VT1-M515-N", "VT1-M533-N", 
    "VT1-M544-O", "VT1-M557-O", "VT1-M560-P", "VT1-M595-P", "VT1-M610-P", "VT1-M632-O", 
    "VT1-M656-O", "VT1-M696-P", "VT1-M700-O", "VT1-M704-P", "VT1-M742-P", "VT1-M758-Q", 
    "VT1-M796-Q", "VT1-M840-R", "VT1-M948-O", "VT1-M984-O", "VT1-N209-P", "VT1-N220-O", 
    "VT1-N240-P", "VT1-N255-P", "VT1-N301-Q", "VT1-N325-P", "VT1-N346-Q", "VT1-N370-Q", 
    "VT1-N395-R", "VT1-N418-P", "VT1-N440-O", "VT1-N480-P", "VT1-N510-P"]  
vc_mocs = ["GLV", "BBD", "ALL_304_SST"]
vc_fill_types = ["PVC", "PVC_HIGH_TEMP"]
vc_eliminators = ["PVC","GLV", "BBD", "SST304"]
vc_sweeper_piping = ["NONE", "YES_SWEEP_PIPE", "IND_SWEEP_PIPE"]
vc_intakes = ["NONE","INLET_SND_GLV", "INLET_SND_BBD", "INLET_SND_SST","BOTPNLS_GLV","BOTPNLS_BBD","BOTPNLS_SST","BOTSCRN_GLV","BOTSCRN_BBD","BOTSCRN_SST"]
vc_discharges = ["NONE","GLV_DISCHR_SND", "BBD_DISCHR_SND", "SST_DISCHR_SND","GLV_TAP_HD","BBD_TAP_HD","SST_TAP_HD"]


# Create dropdowns
create_dropdown("VC_MODEL:", vc_models, vc_model_var)
create_dropdown("MOC:", vc_mocs, vc_moc_var)
create_dropdown("Fill Type:", vc_fill_types, vc_fill_type_var)
create_dropdown("Eliminators:", vc_eliminators, vc_eliminators_var)
create_dropdown("Sweeper Piping:", vc_sweeper_piping, vc_sweeper_piping_var)
create_dropdown("Intake:", vc_intakes, vc_intake_var)
create_dropdown("Discharge:", vc_discharges, vc_discharge_var)

# Buttons for actions
ttk.Button(frame, text="Calculate Combined COG", command=display_combined_cog_details).grid(row=len(frame.winfo_children()) // 2, column=0, columnspan=2, pady=15)

# Label for displaying results
result_label = ttk.Label(frame, text="Combined COG will appear here.", style="CustomLabel.TLabel")
result_label.grid(row=(len(frame.winfo_children()) // 2) + 1, column=0, columnspan=2, pady=5)




        # Step 4: Manipulate PDF
        # Replace 'NewContent.pdf' with the actual path of the new PDF content you want to add
        append_to_pdf(local_pdf_path, "Final_COG_VT_1.pdf", "NewContent.pdf")

   

# Run the Script
if __name__ == "__main__":
    main()
