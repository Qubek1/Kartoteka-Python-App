from json_generics.serializable import try_to_serialize, try_to_deserialize

import json

def json_save(object_to_save, file_name:str) -> bool:
    with open(file_name, "w") as file:
        json.dump(try_to_serialize(object_to_save), file)
    
def json_load(file_name:str, cls:type = None):
    try:
        with open(file_name, "r") as file:
            loaded_object = try_to_deserialize(json.load(file), cls)
        return loaded_object
    except:
        return None
