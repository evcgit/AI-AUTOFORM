import PyPDF2
import requests

def extract_pdf_data(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        fields = reader.get_fields()

        # Initial variables
        module_qty = ''
        for key, field in fields.items():
            if 'QTY' in key and field.get('/V', '').strip().isdigit():
                module_qty = field.get('/V', '').strip()
                break

        # Spacing extraction with Other check
        spacing = {
            "12": 'Checked' if fields.get("12", {}).get('/V', '/Off') == '/On' else 'Unchecked',
            "16": 'Checked' if fields.get("16", {}).get('/V', '/Off') == '/On' else 'Unchecked',
            "24": 'Checked' if fields.get("24", {}).get('/V', '/Off') == '/On' else 'Unchecked',
            "other_spacing": fields.get("Other_Spacing", {}).get('/V', ''),
            "other_spacing_checked": 'Checked' if fields.get("Other_Spacing_Checkbox", {}).get('/V', '/Off') == '/On' else 'Unchecked'
        }
        
        # Check if 'Service Upgrade / Derate' is checked
        service_upgrade_checked = 'Checked' if fields.get("If Service Upgrade  Derate", {}).get('/V', '/Off') == '/On' else 'Unchecked'

        # Initial Busbar and Main Breaker values
        busbar = fields.get("Busbar", {}).get('/V', '')
        main_breaker = fields.get("Main Breaker", {}).get('/V', '')

        # Check states for "New" checkboxes
        new_busbar_checked = 'Checked' if fields.get("New", {}).get('/V', '/Off') == '/On' else 'Unchecked'
        new_main_breaker_checked = 'Checked' if fields.get("New_2", {}).get('/V', '/Off') == '/On' else 'Unchecked'

        # Initialize mpu and derate
        mpu = False
        derate = False

        # Update Busbar and Main Breaker values based on 'Service Upgrade / Derate'
        if service_upgrade_checked == 'Checked':
            new_busbar_value = fields.get("Busbar_2", {}).get('/V', '')
            
            if new_busbar_checked == 'Checked' and new_busbar_value:
                busbar = fields.get("Busbar_2", {}).get('/V', '')
            if new_main_breaker_checked == 'Checked':
                main_breaker = fields.get("Main Breaker_2", {}).get('/V', '')

            # Determine conditions for mpu and derate
            if new_busbar_checked == 'Checked' and new_main_breaker_checked == 'Checked':
                mpu = True
            elif new_busbar_checked == 'Checked' or new_main_breaker_checked == 'Checked':
                derate = True

        # Electrical information dictionary
        electrical_info = {
            "service_upgrade": service_upgrade_checked,
            "busbar": busbar,
            "main_breaker": main_breaker,
            "mpu": mpu,
            "derate": derate,
            "interconnection": fields.get("Point of Interconnection Location", {}).get('/V', '').strip(),
        }

        # Combine all necessary data
        data = {
            "module_1_qty": module_qty,
            "utility_company": fields.get("Utility Company", {}).get('/V', '').strip(),
            "spacing": spacing,
            "electrical_info": electrical_info,
        }

        return data

def send_data_to_django(data):
    url = 'http://127.0.0.1:8000/api/submit-data/'
    try:
        response = requests.post(url, json=data)
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error sending data: {e}")

if __name__ == '__main__':
    pdf_path = '../../file.pdf'  # Update with the correct path
    data = extract_pdf_data(pdf_path)
    if data:
        send_data_to_django(data)
    else:
        print("No data extracted.")
