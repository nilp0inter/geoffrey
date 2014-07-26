"""
JSON Schemas
"""
from geoffrey.data import DataKey

subscription = {
    "$schema": "http://json-schema.org/draft-03/schema",
    "properties": {
        "criteria": {
            "items": {
                "properties": {k: {
                    "type": "string",
                    "id": "http://jsonschema.net/criteria/0/{}".format(k),
                    "required": False}
                for k in DataKey._fields},
                "anyOf": [{"required": [k]} for k in DataKey._fields],
                "additionalProperties": False,
                "type": "object",
                "id": "http://jsonschema.net/criteria/0",
                "required": False
            },
            "type": "array",
            "id": "http://jsonschema.net/criteria",
            "required": True
        }
    },
    "type": "object",
    "id": "http://jsonschema.net",
    "required": True
}
