def extract_input_obj_codes(input_data):
    input_obj_codes = dict()
    input_obj_codes["input_factory_codes"] = [fac["factoryCode"] for fac in input_data["factories"]]
    input_obj_codes["input_customer_codes"] = [cus["customerCode"] for cus in input_data["customers"]]
    # input_obj_codes["input_physic_depot_codes"] = [dep["depotPhysicCode"] for dep in input_data["physicDepots"]]
    # input_obj_codes["input_tco_depot_codes"] = [dep["depotCode"] for dep in input_data["depots"]]
    input_obj_codes["input_depot_codes"] = [dep["depotCode"] for dep in input_data["depots"]]
    input_obj_codes["input_product_codes"] = [loc["productCode"] for loc in input_data["products"]]

    return input_obj_codes

def extract_output_obj_codes(output_data):
    output_factory_codes = []
    output_customer_codes = []
    output_depot_codes = []
    output_product_codes = []    

    for depot in output_data["depots"]:
        output_depot_codes.append(depot["depotCode"])

        for fac in depot["factories"]:
            output_factory_codes.append(fac["factoryCode"])  

            for pro in fac["products"]:
                output_product_codes.append(pro["productCode"]) 
            

        for cus in depot["customers"]:
            output_customer_codes.append(cus["customerCode"])

            for pro in cus["products"]:
                output_product_codes.append(pro["productCode"]) 


    output_obj_codes = dict()
    output_obj_codes["output_factory_codes"] = output_factory_codes
    output_obj_codes["output_customer_codes"] = output_customer_codes
    output_obj_codes["output_depot_codes"] = output_depot_codes
    output_obj_codes["output_product_codes"] = output_product_codes    

    return output_obj_codes

def check_input_output_match(input_data, output_data):
    input_obj_codes = extract_input_obj_codes(input_data)
    output_obj_codes = extract_output_obj_codes(output_data)

    fac_match = set(output_obj_codes["output_factory_codes"]).issubset(set(input_obj_codes["input_factory_codes"]))
    cus_match = set(output_obj_codes["output_customer_codes"]).issubset(set(input_obj_codes["input_customer_codes"]))
    dep_match = set(output_obj_codes["output_depot_codes"]).issubset(set(input_obj_codes["input_depot_codes"]))
    pro_match = set(output_obj_codes["output_product_codes"]).issubset(set(input_obj_codes["input_product_codes"]))

    io_match = cus_match and fac_match and dep_match and pro_match

    return io_match