import os
import requests

def download(url: str, output: str) -> str:
    response = requests.get(url)
    out_folder = os.path.dirname(output)
    os.makedirs(out_folder, exist_ok=True)
    with open(output, 'wb') as f:
        _ = f.write(response.content)
    return output
