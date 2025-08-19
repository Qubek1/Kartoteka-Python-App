from json_generics.serializable import *

def serialize_dict(dictionary:dict):
    if any(isinstance(key, JsonSerializable) for key in dictionary.keys()):
        return [(try_to_serialize(key), try_to_serialize(value)) for key, value in dictionary.items()]
    else:
        return {key:try_to_serialize(value) for key, value in dictionary.items()}

def deserialize_to_dict(collection:dict|list, key_cls:type = None, value_cls:type = None) -> dict:
    if isinstance(collection, dict):
        return {try_to_deserialize(key, key_cls):try_to_deserialize(value, value_cls) for key, value in collection.items()}
    else:
        return {try_to_deserialize(key, key_cls):try_to_deserialize(value, value_cls) for key, value in collection}
    
def serialize_list(l:list) -> list:
    return [try_to_serialize(item) for item in l]

def deserialize_to_list(l:list, cls:type = None) -> list:
    return [try_to_deserialize(item, cls) for item in l]


class JsonSerializableList(list, JsonSerializable):
    def to_json_object(self):
        return serialize_list(self)
    
    @classmethod
    def from_json_object(cls, json_object):
        return deserialize_to_list(json_object)
    

class JsonSerializableDict(dict, JsonSerializable):
    def to_json_object(self):
        return serialize_dict(self)
    
    @classmethod
    def from_json_object(cls, json_object):
        return deserialize_to_dict(json_object)