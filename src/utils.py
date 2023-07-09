import json


def load_json(path: str):
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def save_csv(data: list, file_path:str, sep:str="|"):
    with open(file_path, "w") as f:
        _ = f.writelines([f"{sep.join(line)}\n" for line in data])
    return file_path


def save_xml(data: list, file_path: str):
    header = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    with open(file_path, "w") as f:
        _ = f.write(f"{header}\n<SESSION>\n")
        for line in data:
            _ = f.write(
                """
                <DISCOURSE speaker="{speaker}" speech="{speech}"><TEXT>{content}</TEXT></DISCOURSE>\n
                """.format(**line))
        _ = f.write("</SESSION>")
