from flask import Flask, request, jsonify, stream_with_context
import requests
import uuid
import threading
 
filenames = []
downloaded_files = []


api = Flask(__name__)
 
# Function to download with progress reporting
def download_file(url, task_id):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_length = r.headers.get('content-length')
        if total_length is None:  # No content length header
            total_length = None
 
        total_length = int(total_length)
        downloaded = 0
        # Open file for saving the downloaded content
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_length == None:
                        progress = "unknown"
                    else:
                        progress = (downloaded / total_length) * 100
                        # Update progress for this task (store progress in the list)
                        update_progress(task_id, progress)
    # Append the filename and URL to the list after download completes
    downloaded_files.append({"id": task_id, "url": url, "filename": local_filename})
    return f"Download complete: {local_filename}"
 
# Store progress of each download task
download_progress = {}
 
def update_progress(task_id, progress):
    download_progress[task_id] = progress
 
@api.route('/', methods=['GET'])
def get_companies():
    return jsonify(filenames)
 
@api.route('/download', methods=['POST'])
def post_download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is missing"}), 400
 
    # Create a task ID for the download
    task_id = str(uuid.uuid4())
 
    # Start the download in a separate thread
    download_thread = threading.Thread(target=download_file, args=(url, task_id))
    download_thread.start()
 
    # Return task ID to track progress
    return jsonify({"message": "Download started", "task_id": task_id})
 
@api.route('/progress', methods=['GET'])
def get_progress():
    task_id = request.args.get('task_id')
    if not task_id:
        return jsonify({"error": "task_id parameter is missing"}), 400
 
    progress = download_progress.get(task_id, None)
    if progress is None:
        return jsonify({"error": "Invalid task_id or download not found"}), 404
 
    return jsonify({"task_id": task_id, "progress": progress})
 
if __name__ == '__main__':
    api.run()