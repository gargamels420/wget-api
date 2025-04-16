import json
import os

METADATA_FILE = "download_metadata.json"
#<-----------------metadata helpers------------------------>
def load_metadata():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_metadata(metadata):
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=4)

def get_task_metadata(task_id):
    metadata = load_metadata()
    return metadata.get(task_id)

def update_task_metadata(task_id, data):
    metadata = load_metadata()
    metadata[task_id] = data
    save_metadata(metadata)

def delete_task_metadata(task_id):
    metadata = load_metadata()
    metadata.pop(task_id, None)
    save_metadata(metadata)

#<--------------------file helpers------------------------->
def rename_file(path, newpath):
    os.rename(path,newpath)

def delete_file(path):
    os.remove(path)