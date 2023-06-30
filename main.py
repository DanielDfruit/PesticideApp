import requests
import PySimpleGUI as sg

def search_pesticide(chemical_name):
    try:
        # Construct the URL to search by product name
        url = f"https://ofmpub.epa.gov/apex/pesticides/pplstxt/{chemical_name}"

        # Send a request to the API
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Check if any items were found
            if 'items' in data and len(data['items']) > 0:
                item = data['items'][0]  # Assuming we only need the first item

                # Extract the desired information from the item
                product_name = item.get('productname')
                manufacturer = item.get('companyinfo', [{}])[0].get('name')
                chemical_type = item.get('types', [{}])[0].get('type', 'Unknown')  # Handle empty types list
                approved_crops = [site.get('site') for site in item.get('sites', [])]
                cas_number = item.get('active_ingredients', [{}])[0].get('cas_number')
                product_status = item.get('product_status')
                formulation = item.get('formulations', [{}])[0].get('formulation')

                # Retrieve active ingredient and molecular weight from PubChem
                active_ingredient, molecular_weight = get_active_ingredient_and_mw(cas_number)

                # Return the information as a dictionary
                return {
                    'Chemical Name': product_name,
                    'Manufacturer': manufacturer,
                    'Chemical Type': chemical_type,
                    'Approved Crops': approved_crops,
                    'Active Ingredient': active_ingredient,
                    'Product Status': product_status,
                    'Formulation': formulation,
                    'CAS Number': cas_number,
                    'Molecular Weight': molecular_weight
                }
    except Exception as e:
        print(f"Error occurred: {e}")

    return None

def get_active_ingredient_and_mw(cas_number):
    try:
        base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        substance_url = f"{base_url}/substance/name/{cas_number}/cids/JSON"

        # Retrieve the Substance ID (SID) from PubChem using the CAS number
        response = requests.get(substance_url)
        substance_data = response.json()

        if 'IdentifierList' in substance_data and 'CID' in substance_data['IdentifierList']:
            cids = substance_data['IdentifierList']['CID']

            if len(cids) > 0:
                cid = cids[0]

                # Retrieve the active ingredient and molecular weight using the CID
                compound_url = f"{base_url}/compound/cid/{cid}/JSON"

                response = requests.get(compound_url)
                compound_data = response.json()

                if 'PC_Compounds' in compound_data and len(compound_data['PC_Compounds']) > 0:
                    compound = compound_data['PC_Compounds'][0]

                    # Extract the active ingredient and molecular weight
                    active_ingredient = compound.get('synonyms', [cas_number])[0]
                    molecular_weight = compound.get('props', [{}])[0].get('MW')

                    return active_ingredient, molecular_weight
    except Exception as e:
        print(f"Error occurred while retrieving active ingredient and molecular weight: {e}")

    return None, None

# Set the theme
sg.theme('BluePurple')

# Create the PySimpleGUI layout
layout = [
    [sg.Text("Enter the chemical you are looking for:")],
    [sg.Input(key='-CHEMICAL-')],
    [sg.Button("Search"), sg.Button("Clear"), sg.Button("Close")],
    [sg.Output(size=(80, 20), key='-OUTPUT-')]
]

# Create the window
window = sg.Window("Pesticide Information", layout)

# Event loop
while True:
    event, values = window.read()

    # Exit the program if the window is closed
    if event == sg.WINDOW_CLOSED or event == "Close":
        break

    if event == "Search":
        chemical_name = values['-CHEMICAL-']

        # Call the search function
        result = search_pesticide(chemical_name)

        # Clear the previous output
        window['-OUTPUT-'].update('')

        if result is not None:
            # Print the information
            for key, value in result.items():
                print(f"{key}: {value}")
        else:
            print("No results found for the given chemical.")

    if event == "Clear":
        # Clear the output
        window['-OUTPUT-'].update('')

# Close the window
window.close()
