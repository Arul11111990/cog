import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox

# Function to fetch COG and mass values for each parameter from respective tables
def get_cog_mass_values(vc_model, vc_moc, vc_fill_type, vc_eliminators, vc_sweeper_piping, vc_intake, vc_discharge):
    try:
        connection = pyodbc.connect(r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\\Users\\arul.mohan\\OneDrive - MKS VISION PVT LTD\\COG\\VT_COG.accdb;")
        cursor = connection.cursor()

        # Define the table names and respective ParameterValue fields
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

        # Retrieve COG and mass values for each parameter table
        for table, (parameter_column, parameter_value) in tables.items():
            # Query to get COG_X, COG_Y, COG_Z, and MASS for each selected parameter
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
        connection.close()

        # Calculate combined COG if total mass is greater than zero
        if total_mass > 0:
            combined_cog = {
                'x': weighted_cog['x'] / total_mass,
                'y': weighted_cog['y'] / total_mass,
                'z': weighted_cog['z'] / total_mass
            }
            return f"Combined COG X: {combined_cog['x']:.2f}, Y: {combined_cog['y']:.2f}, Z: {combined_cog['z']:.2f}"
        else:
            return "No COG and mass data found for the selected configuration."
    except Exception as e:
        return f"Error: {str(e)}"

# Function to display combined COG details
def display_combined_cog_details():
    vc_model = vc_model_var.get()
    vc_moc = vc_moc_var.get()
    vc_fill_type = vc_fill_type_var.get()
    vc_eliminators = vc_eliminators_var.get()
    vc_sweeper_piping = vc_sweeper_piping_var.get()
    vc_intake = vc_intake_var.get()
    vc_discharge = vc_discharge_var.get()

    if all([vc_model, vc_moc, vc_fill_type, vc_eliminators, vc_sweeper_piping, vc_intake, vc_discharge]):
        cog_details = get_cog_mass_values(vc_model, vc_moc, vc_fill_type, vc_eliminators, vc_sweeper_piping, vc_intake, vc_discharge)
        result_label.config(text=f"Combined COG Details: {cog_details}")
    else:
        messagebox.showwarning("Input Error", "Please select all parameters.")

# Create the main application window
app = tk.Tk()
app.title("Combined COG Calculator")

# Dropdown variables and options
vc_model_var = tk.StringVar(value="Select Model")
vc_moc_var = tk.StringVar(value="Select MOC")
vc_fill_type_var = tk.StringVar(value="Select Fill Type")
vc_eliminators_var = tk.StringVar(value="Select Eliminators")
vc_sweeper_piping_var = tk.StringVar(value="Select Sweeper Piping")
vc_intake_var = tk.StringVar(value="Select Intake")
vc_discharge_var = tk.StringVar(value="Select Discharge")

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

# Function to create dropdowns
def create_dropdown(label_text, options, variable):
    label = ttk.Label(app, text=label_text)
    label.pack(pady=5)
    dropdown = ttk.Combobox(app, textvariable=variable, values=options, state="readonly")
    dropdown.pack(pady=5)

# Creating dropdowns
create_dropdown("Select VC_MODEL:", vc_models, vc_model_var)
create_dropdown("Select VC_MOC:", vc_mocs, vc_moc_var)
create_dropdown("Select VC_FILL_TYPE:", vc_fill_types, vc_fill_type_var)
create_dropdown("Select VC_MOC_ELIMINATORS:", vc_eliminators, vc_eliminators_var)
create_dropdown("Select VC_SWEEPER_PIPING:", vc_sweeper_piping, vc_sweeper_piping_var)
create_dropdown("Select VC_INTAKE:", vc_intakes, vc_intake_var)
create_dropdown("Select VC_DISCHARGE:", vc_discharges, vc_discharge_var)

# Button to fetch and display combined COG details
fetch_button = ttk.Button(app, text="Calculate Combined COG", command=display_combined_cog_details)
fetch_button.pack(pady=20)

# Label to display the combined COG result
result_label = ttk.Label(app, text="Combined COG Details: ")
result_label.pack(pady=10)

# Run the application
app.mainloop()