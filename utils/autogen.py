import os
import json
import yaml
import string

def type_to_kaitai(type: str) -> str:
    match type:
        case "bool":
            return "b1"
        case "int8":
            return "s1"
        case "uint8":
            return "u1"
        case "int16":
            return "s2"
        case "uint16":
            return "u2"
        case "int32" | "int":
            return "s4"
        case "uint32" | "uint":
            return "u4"
        case "lot":
            return "common::lot"
        case "int64":
            return "s8"
        case "uint64":
            return "u8"
        case "objectid":
            return "commom::object_id"
        case "float":
            return "f4"
        case "double":
            return "f8"
        case "string":
            return "strz"
        case "Vector3":
            return "common::vector3"
        case "Quaternion" | "Vector4":
            return "common::quaternion"
        case "wstr":
            return "common::u4_wstr"
        case "str":
            return "common::u4_str"
        case _:
            return type 

def clean_up_name(data: str) -> str:
    if len(data) > 1:
        if data[0] in string.ascii_lowercase and data[1] in string.ascii_uppercase:
            data = data[1:]

    for i in range(len(data)):
        character = data[i]
        if character in string.ascii_uppercase:
            for j in range(i + 1, len(data)):
                if data[j] in string.ascii_uppercase:
                    data = data[:j] + data[j].lower() + data[j + 1:]
                else:
                    break
    
    # split the words by where the upper case starts
    words = []
    for i in range(len(data)):
        character = data[i]

        if character in string.ascii_uppercase:
            words.append(character.lower())
        else:
            if len(words) == 0:
                words.append(character)
            else:
                words[-1] += character

    return "_".join(words)

def generate_meta_data() -> dict:
    return {
        "id": "game_message",
        "endian": "le",
        "bit-endian": "le",
        "imports": ["../common"]
    }

def generate_sequence_data(params: dict) -> list:
    return_list = []
    
    for item in params:
        return_list.append({
            "id": clean_up_name(item["name"]),
            "type": type_to_kaitai(item["type"]),
        })

        if "default" in item:
            return_list[-1]["contents"] = item["default"]

    return return_list

def generate_yaml(data) -> dict:
    classes = {}
    cases = {}

    for key in data["messages"].keys():
        message = data["messages"][key]
        if "custom" in message:
            continue

        classes[clean_up_name(message["name"])] = {"seq": generate_sequence_data(message["params"])}
        cases[int(key)] = clean_up_name(message["name"])

    return {
        "meta": generate_meta_data(),
        "seq": [
            {"type": {
                "switch-on": "id",
                "cases": cases
            }}
        ],
        "types": classes
    }

def main():
    if not os.path.exists("../packets/"):
        os.mkdir("../packets/")

    data_store = json.loads(open("input.json", "r").read())

    with open("test.yaml", "w") as f:
        yaml.dump(generate_yaml(data_store), f, indent=2)

if __name__ == "__main__":
    main()