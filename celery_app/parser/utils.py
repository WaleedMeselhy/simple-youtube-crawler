import requests
import shutil
import os


def download(url, file_path):
    if not os.path.isfile(file_path):
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(file_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
