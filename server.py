from flask import Flask, request, jsonify
import requests
import uuid
import threading
import os
import metadata_services

#<-----------------------after start------------------------->

DOWNLOAD_FOLDER = "downloads"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

api = Flask(__name__)

# File-based metadata path
METADATA_FILE = "download_metadata.json"
cancel_flags = {}
download_progress = {}





#<---------------------- Download Helpers ---------------------->

def update_progress(task_id, progress):
    download_progress[task_id] = progress

def has_invalid_chars(filename):
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        if char in filename:
            return True
    return False

def download_file(url, task_id, local_filename):
    full_path = os.path.join(DOWNLOAD_FOLDER, local_filename)
    part_file = full_path + ".part"
    start_byte = 0

    try:
        start_byte = os.path.getsize(part_file)
    except FileNotFoundError:
        pass

    headers = {'Range': f'bytes={start_byte}-'} if start_byte > 0 else {}

    with requests.get(url, headers=headers, stream=True) as r:
        if r.status_code not in [200, 206]:
            r.raise_for_status()

        total_length = r.headers.get('content-length')
        total_length = int(total_length) + start_byte if total_length else None

        downloaded = start_byte
        with open(part_file, 'ab') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if cancel_flags.get(task_id):
                    print(f"Download {task_id} stoped.")
                    return

                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress = (downloaded / total_length) * 100 if total_length else "unknown"
                    update_progress(task_id, progress)

    metadata_services.rename_file(part_file, local_filename)
    metadata_services.update_task_metadata(task_id, {
        "url": url,
        "filename": local_filename,
        "status": "completed"
    })
    print(f"Download {task_id} complete.")

#<---------------------- API Routes ---------------------->
@api.route('/download', methods=['POST'])
def post_download():
    url = request.args.get('url')
    local_filename = request.args.get('local_filename')

    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400
    if not local_filename:
        return jsonify({"error": "Missing 'local_filename' parameter"}), 400
    if has_invalid_chars(local_filename):
        return jsonify({"error": "Filename contains invalid characters"}), 400

    task_id = str(uuid.uuid4())

    metadata_services.update_task_metadata(task_id, {
        "url": url,
        "filename": local_filename,
        "status": "in_progress"
    })

    thread = threading.Thread(target=download_file, args=(url, task_id, local_filename))
    thread.start()

    return jsonify({"message": "Download started", "task_id": task_id}), 200

@api.route('/progress', methods=['GET'])
def get_progress():
    task_id = request.args.get('task_id')
    if not task_id:
        return jsonify({"error": "Missing 'task_id' parameter"}), 400

    progress = download_progress.get(task_id)
    if progress is None:
        return jsonify({"error": "Download not found or no progress yet"}), 404

    return jsonify({"task_id": task_id, "progress": progress})

@api.route('/stop', methods=['POST'])
def stop_download():
    task_id = request.args.get('task_id')
    if not task_id:
        return jsonify({"error": "Missing 'task_id' parameter"}), 400

    meta = metadata_services.get_task_metadata(task_id)
    if not meta:
        return jsonify({"error": "Invalid task_id"}), 404

    cancel_flags[task_id] = True
    meta["status"] = "stoped"
    metadata_services.update_task_metadata(task_id, meta)

    return jsonify({"message": f"Download {task_id} stop requested."}), 200

@api.route('/cancel', methods=['POST'])
def cancel_download():
    task_id = request.args.get('task_id')
    if not task_id:
        return jsonify({"error": "Missing 'task_id' parameter"}), 400

    meta = metadata_services.get_task_metadata(task_id)
    if not meta:
        return jsonify({"error": "Invalid task_id"}), 404

    cancel_flags[task_id] = True
    meta["status"] = "cancelled"
    metadata_services.update_task_metadata(task_id, meta)
    metadata_services.delete_file(meta["filename"]+".part")
    return jsonify({"message": f"Download {task_id} cancellation requested."}), 200

@api.route('/resume', methods=['POST'])
def resume_download():
    task_id = request.args.get('task_id')
    if not task_id:
        return jsonify({"error": "Missing 'task_id' parameter"}), 400

    meta = metadata_services.get_task_metadata(task_id)
    if not meta:
        return jsonify({"error": "Invalid task_id"}), 404

    if meta["status"] == "completed":
        return jsonify({"message": "Download already completed"}), 200
    
    meta["status"] = "in_progress"

    cancel_flags[task_id] = False  # reset cancel flag
    metadata_services.update_task_metadata(task_id,meta)

    thread = threading.Thread(target=download_file, args=(meta["url"], task_id, meta["filename"]))
    thread.start()

    return jsonify({"message": f"Resuming download for task {task_id}"}), 200

@api.route('/', methods=['GET'])
def get_status():
    return jsonify(metadata_services.load_metadata())

@api.route('/webui', methods=['GET'])
def get_webui():
    with open("index.html","r") as f:
        webpage = f.read()
    return webpage


#<---------------------- Run Server ---------------------->

def auto_resume_download():
    meta_bunch = metadata_services.load_metadata()
    for meta in meta_bunch:
        meta_data = meta_bunch[meta]
        if meta_data["status"] == "in_progress":
            thread = threading.Thread(target=download_file, args=(meta_data["url"], meta, meta_data["filename"]))
            thread.start()

auto_resume_download()

if __name__ == '__main__':
    api.run(debug=True)
