from dataclasses import dataclass

class JsonSerializable:
    def to_json_object(self):
        pass
    
    @classmethod
    def from_json_object(cls, json_object):
        pass

def try_to_serialize(object_to_serialize:JsonSerializable):
    if isinstance(object_to_serialize, JsonSerializable):
        return object_to_serialize.to_json_object()
    return object_to_serialize

def try_to_deserialize(json_object, cls:JsonSerializable = None):
    if cls is not None and issubclass(cls, JsonSerializable):
        return cls.from_json_object(json_object)
    return json_object