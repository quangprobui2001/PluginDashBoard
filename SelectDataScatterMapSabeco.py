import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import json

with open('input 200310.json', encoding='utf-8') as f:
    input_data = json.load(f)

def add_offset(lat, lng, index, offset=0.001):
    offset = offset * index
    return lat + offset, lng + offset

def list_of_dicts_to_plain_dict(list_dict, keyword, valuename):
    return {
        element[keyword]: element[valuename] for element in list_dict
    }

def list_of_dicts_to_dict_of_dicts(list_dict, keyword):
    return{
        element[keyword]:{
            key: value for key, value in element.items() if key != keyword
        } for element in list_dict
    }

def list_of_dicts_to_dict_of_list(list_dict, keyword, valuename):
    return {
        component[keyword]: [
            element[valuename] for element in list_dict if component[keyword] == element[keyword]
        ] for component in list_dict
        
    }

def reverse_plain_dict_to_dict_of_list(input_dict):
    reverse_dict = {}
    for key, value in input_dict.items():
        reverse_dict.setdefault(value, []).append(key)
    return reverse_dict

def create_customer_data(input_data, lat_lng_dict):
    customer_data = {}
    location_offsets = {}

    for customer in input_data["customers"]:
        lat = lat_lng_dict[customer["customerCode"]]["lat"]
        lng = lat_lng_dict[customer["customerCode"]]["lng"]
        key = (lat, lng)

        location_offsets[key] = location_offsets.get(key, 0) + 1
        offset_index = location_offsets[key] - 1
        offset_lat, offset_lng = add_offset(lat, lng, offset_index) if offset_index > 0 else(lat, lng)

        customer_data[customer["customerCode"]] = {
            "customerCode": customer["customerCode"],
            "customerDetails": customer["customerDetails"],
            "limitNumberTCODelivered": customer["limitNumberTCODelivered"],
            "MOQweight": customer["MOQweight"],
            "original_coord": {
                "lat": lat_lng_dict[customer["customerCode"]]["lat"],
                "lng": lat_lng_dict[customer["customerCode"]]["lng"]
            },
            "offset_coord": {
                "lat": offset_lat,
                "lng": offset_lng
            },

            "products": [
                {
                    "product_code": product["productCode"],
                    "demand": product["meanDemand"],
                    "p-value" : product["p-value"],
                    "standardDeviationDemand": product["standardDeviationDemand"],
                }
                for product in customer["products"]
            ],
            "safety_stock": [
                {
                    "product_code": stock["productCode"],
                    "capacity": stock["Capacity"]
                }
                for stock in customer["safetyStock"]
            ]
        }

    return customer_data


def create_depot_data(input_data, lat_lng_dict):
    depot_data = {}
    location_offsets = {}

    for depot in input_data["depots"]:
        lat = lat_lng_dict[depot["depotCode"]]["lat"]
        lng = lat_lng_dict[depot["depotCode"]]["lng"]
        key = (lat, lng)

        location_offsets[key] = location_offsets.get(key, 0) + 1
        offset_index = location_offsets[key] - 1
        offset_lat, offset_lng = add_offset(lat, lng, offset_index) if offset_index > 0 else(lat, lng)

        depot_data[depot["depotCode"]] = {
            "depotCode": depot["depotCode"],
            "depotDetails": depot["depotDetails"],
            "original_coord": {
                "lat": lat_lng_dict[depot["depotCode"]]["lat"],
                "lng": lat_lng_dict[depot["depotCode"]]["lng"]
            },
            "offset_coord": {
                "lat": offset_lat,
                "lng": offset_lng
            },
            "handlingOutCost" : depot["handlingOutCost"],
            "handlingInCost" : depot["handlingInCost"],
            "KV" : depot["KV"]
        }
    return depot_data


def create_factories_data(input_data, lat_lng_dict):
    factories_data = {}
    location_offsets = {}

    for factory in input_data["factories"]:
        lat = lat_lng_dict[factory["factoryCode"]]["lat"]
        lng = lat_lng_dict[factory["factoryCode"]]["lng"]
        key = (lat, lng)

        location_offsets[key] = location_offsets.get(key, 0) + 1
        offset_index = location_offsets[key] - 1
        offset_lat, offset_lng = add_offset(lat, lng, offset_index) if offset_index > 0 else(lat, lng)

        factories_data[factory["factoryCode"]] = {
            "factoryCode": factory["factoryCode"],
            "factoryDetails": factory["factoryDetails"],
            "original_coord": {
                "lat": lat_lng_dict[factory["factoryCode"]]["lat"],
                "lng": lat_lng_dict[factory["factoryCode"]]["lng"]
            },
            "offset_coord": {
                "lat": offset_lat,
                "lng": offset_lng
            },
            "products" : factory["products"]

        }
    return factories_data

lat_lng_dict = list_of_dicts_to_dict_of_dicts(input_data["locations"], "locationCode")
customer_data = create_customer_data(input_data, lat_lng_dict)
depot_data = create_depot_data(input_data, lat_lng_dict)
factories_data = create_factories_data(input_data, lat_lng_dict)




app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.Graph(
        id='mapbox',
        figure={
            'data': [
                {
                    'type': 'scattermapbox',
                    'lat': [customer_data[customer]['offset_coord']['lat'] for customer in customer_data],
                    'lon': [customer_data[customer]['offset_coord']['lng'] for customer in customer_data],
                    'hovertext': [customer_data[customer]['customerDetails']['cType']['typeOfCustomerByOwner'] for customer in customer_data],
                    'mode': 'markers',
                    'marker': {'size': 10},
                    'marker_color': 'blue',
                    'name': 'customers',
                    'text': [customer_data[customer]['customerCode'] for customer in customer_data]
                },
                {
                    'type': 'scattermapbox',
                    'lat': [depot_data[depot]['offset_coord']['lat'] for depot in depot_data],
                    'lon': [depot_data[depot]['offset_coord']['lng'] for depot in depot_data],
                    'hovertext': [depot_data[depot]['depotCode'] for depot in depot_data],
                    'mode': 'markers',
                    'marker': {'size': 15},
                    'marker_color': 'red',
                    'name': 'depots',
                    'text': [depot_data[depot]['depotCode'] for depot in depot_data]
                }
            ],
            'layout': {
                'mapbox': {
                    'accesstoken': 'pk.eyJ1Ijoic29sa2FyYW1tYWFyIiwiYSI6ImNrc2JqdWM4eTA3aXYzMG9kOGd2NTZxdHEifQ.M8vfidWZ-3C7SEI2w4EjLg',
                    'style': 'mapbox://styles/mapbox/streets-v11',
                    'center': {
                        'lat': 10.8,
                        'lon': 106.6
                    },
                    'zoom': 8
                }
            }
        }
    ),
    html.Div(id='output-container')
])

# Define callback to update output based on lasso selection
@app.callback(
    Output('output-container', 'children'),
    [Input('mapbox', 'selectedData')],
)
def update_output(selectedData, input_data=input_data):
    if selectedData is not None:
        selected_points = selectedData['points']
        selected_location_codes = [point['text'] for point in selected_points]
    else:
        selected_location_codes = []
    print (selected_location_codes)

    factory_code = []
    for factory in input_data["factories"]:
        factory_code.append(factory["factoryCode"])
    print(factory_code)
    print("\n=====================================\n")

    factoryByOwner = []
    for factory in input_data["factories"]:
        owner_type = factory["factoryDetails"]["fType"]["typeOfFactoryByOwner"]
        factoryByOwner.append(owner_type)
    factoryByOwner = list(set(factoryByOwner))
    print(factoryByOwner)
    print("\n=====================================\n")

    select_depot_code = []
    select_customer_code = []
    for location_code in selected_location_codes:
        for depot in depot_data.values():
            if location_code == depot['depotCode']:
                select_depot_code.append(depot['depotCode'])
                break
        for customer in customer_data.values():
            if location_code == customer['customerCode']:
                select_customer_code.append(customer['customerCode'])
                break

    print(select_depot_code)
    print("\n=====================================\n")   
    print(select_customer_code)
    print("\n=====================================\n")

    physic_depot_codes = []
    for location_code in select_depot_code:
        for depot in depot_data.values():
            if location_code == depot['depotCode']:
                depot_code = depot['depotCode']
                if 'DC' in depot_code:
                    depot_code = depot_code.replace('DC', '')
                physic_depot_code = 'PD-' + depot_code
                physic_depot_codes.append(physic_depot_code)
                break
    print(physic_depot_codes)
    print("\n=====================================\n")

    depotByOwner = []
    for location_code in select_depot_code:
        for depot in depot_data.values():
            if location_code == depot["depotCode"]:
                depot_owner = depot["depotDetails"]["dType"]["typeOfDepotByOwner"]
                depotByOwner.append(depot_owner)
    depotByOwner = list(set(depotByOwner))
    print("depotByOwner", depotByOwner)
    print("\n=====================================\n")

    customerByOwner = []
    for location_code in select_customer_code:
        for customer in customer_data.values():
            if location_code == customer["customerCode"]:
                customer_owner = customer["customerDetails"]["cType"]["typeOfCustomerByOwner"]
                customerByOwner.append(customer_owner)
    customerByOwner = list(set(customerByOwner))
    print("customerByOwner", customerByOwner)
    print("\n=====================================\n")


    
    append_data = {
        'day_plan': 1,
        'factories': input_data['factories'],#done
        'customers': [],
        'physicDepots': [], #done
        'depots': [],     #done
        'products': input_data['products'],# done
        'priceByLevelService': {
            "IBtranspCost": [], #done
            "OBtranspCost": [] #done
        },
        'distances': {
            'FD': [],#done
            'DC' : []#done
        },
        'matrixConfig': {
            "mapPhysicDepotWithDepot": [], #done
            "mapPhysicDepotWithFactory": input_data['matrixConfig']['mapPhysicDepotWithFactory'], #done
            "matrixCamTai": {
                "factoryDepot":{
                    "factoryDepotByAdress": [], #done
                    "factoryDepotByOwner": [] #done
                },
                "depotCustomer":{
                    "depotCustomerByAdress": [], #done
                    "depotCustomerByOwner": [] #done
                }
            },
            "parameter":{ **input_data['matrixConfig']['parameter']}#done

        },
        'locations': [], #done
        'algoParam': { **input_data['algoParam']} #done
    }
    
    for location_code in select_customer_code:
        for customer in input_data['customers']:
            if location_code == customer['customerCode']:
                append_data['customers'].append(customer)
                break
        
    for location_code in select_depot_code:  
        for depot in input_data['depots']:   
            if location_code == depot['depotCode']:
                append_data['depots'].append(depot)
                break
    
    for physic_depot_code in physic_depot_codes:
        for physic_depot in input_data['physicDepots']:
            if physic_depot_code == physic_depot['depotPhysicCode']:
                append_data['physicDepots'].append(physic_depot)
                break
    
    for location in input_data['locations']:
        for factory in input_data['factories']:
            if location['locationCode'] == factory['factoryCode']:
                append_data['locations'].append(location)
                break

    mapPhysicDepotWithDepot = input_data['matrixConfig']["mapPhysicDepotWithDepot"]  
    for depot, physic_depot in zip(select_depot_code, physic_depot_codes):
        for entry in mapPhysicDepotWithDepot:
            if entry["typeOfDepotByAdress"] == depot and entry["typeOfPDByAdress"] == physic_depot:
                append_data['matrixConfig']['mapPhysicDepotWithDepot'].append(entry)
    print(append_data['matrixConfig']['mapPhysicDepotWithDepot'])
    print("\n=====================================\n")

    factoryDepotByAdress = input_data['matrixConfig']["matrixCamTai"]["factoryDepot"]["factoryDepotByAdress"]
    for depot in select_depot_code:
        for factory in factory_code:
            for entry_2 in factoryDepotByAdress:
                if entry_2["typeOfDepotByAdress"] == depot and entry_2["typeOfFactoryByAdress"] == factory:
                    append_data['matrixConfig']['matrixCamTai']["factoryDepot"]["factoryDepotByAdress"].append(entry_2)
    print(append_data['matrixConfig']['matrixCamTai']["factoryDepot"]["factoryDepotByAdress"])
    print("\n=====================================\n")

    factoryDepotByOwner = input_data['matrixConfig']["matrixCamTai"]["factoryDepot"]["factoryDepotByOwner"]
    for depot_owner in depotByOwner:
        for factory_owner in factoryByOwner:
            for entry_3 in factoryDepotByOwner:
                if entry_3["typeOfDepotByOwner"] == depot_owner and entry_3["typeOfFactoryByOwner"] == factory_owner:
                    append_data['matrixConfig']['matrixCamTai']["factoryDepot"]["factoryDepotByOwner"].append(entry_3)
    print(append_data['matrixConfig']['matrixCamTai']["factoryDepot"]["factoryDepotByOwner"])
    print("\n=====================================\n")

    depotCustomerByOwner = input_data['matrixConfig']["matrixCamTai"]["depotCustomer"]["depotCustomerByOwner"]
    for customer_owner in customerByOwner:
        for depot_owner in depotByOwner:
            for entry_4 in depotCustomerByOwner:
                if entry_4["typeOfCustomerByOwner"] == customer_owner and entry_4["typeOfDepotByOwner"] == depot_owner:
                    append_data['matrixConfig']['matrixCamTai']["depotCustomer"]["depotCustomerByOwner"].append(entry_4)
    print(append_data['matrixConfig']['matrixCamTai']["depotCustomer"]["depotCustomerByOwner"])
    print("\n=====================================\n")

    FD_distance = input_data["distances"]["FD"]
    for depot in select_depot_code:
        for factory in factory_code:
            for entry_5 in FD_distance:
                if entry_5["srcCode"] == factory  and entry_5["destCode"] == depot:
                    append_data['distances']['FD'].append(entry_5)
    print(append_data['distances']['FD'])
    print("\n=====================================\n")

    DC_distance = input_data["distances"]["DC"]
    for depot in select_depot_code:
        for customer in select_customer_code:
            for entry_6 in DC_distance:
                if entry_6["srcCode"] == depot  and entry_6["destCode"] == customer:
                    append_data['distances']['DC'].append(entry_6)
    print(append_data['distances']['DC'])
    print("\n=====================================\n")

    IB_cost = input_data["priceByLevelService"]["IBtranspCost"]
    for depot in select_depot_code:
        for factory in factory_code:
            for entry_7 in IB_cost:
                if entry_7["srcCode"] == factory  and entry_7["destCode"] == depot:
                    append_data['priceByLevelService']["IBtranspCost"].append(entry_7)
    print(append_data['priceByLevelService']["IBtranspCost"])
    print("\n=====================================\n")

    OB_cost = input_data['priceByLevelService']['OBtranspCost']
    for depot in select_depot_code:
        for customer in select_customer_code:
            for entry_8 in OB_cost:
                if entry_8["srcCode"] == depot  and entry_8["destCode"] == customer:
                    append_data['priceByLevelService']["OBtranspCost"].append(entry_8)
    print(append_data['priceByLevelService']["OBtranspCost"])
    print("\n=====================================\n")
    
    for obj_type in append_data:
        if obj_type in input_data and isinstance(input_data[obj_type], list):
            for obj in input_data[obj_type]:
                if 'locationCode' in obj and obj['locationCode'] in selected_location_codes:
                    append_data[obj_type].append(obj)
        elif obj_type in input_data and isinstance(input_data[obj_type], dict):
            if 'locationCode' in input_data[obj_type] and input_data[obj_type]['locationCode'] in selected_location_codes:
                append_data[obj_type].append(input_data[obj_type])

    # Convert append_data to JSON string
    append_data_json = json.dumps(append_data, ensure_ascii=False)

    with open('test_full_4.json', 'w', encoding='utf-8') as f:
        json.dump(append_data, f, ensure_ascii=False, indent=4)

    return append_data_json

if __name__ == '__main__':
    app.run_server(debug=True)
