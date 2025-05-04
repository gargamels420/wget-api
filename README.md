# 🗂️ Flask Download Manager API

A lightweight download manager with a web interface built using Flask. Supports downloading files from URLs with progress tracking, stopping, resuming, and cancelling.

---

## 🚀 Features

- Start downloads via URL + custom filename
- Track real-time progress
- Stop, resume, or cancel downloads
- Simple web interface for managing downloads
- REST API with clean endpoints
- Docker support

---

## 📦 Requirements

- Python 3.8+
- `pip` for installing dependencies

---

## 🛠️ Installation (without Docker)

```bash
git clone https://github.com/yourusername/flask-download-manager.git
cd flask-download-manager
pip install -r requirements.txt
python app.py
````

Server will start on `http://localhost:5000`

---

## 🐳 Running with Docker

### Build the image

```bash
docker build -t flask-downloader .
```

### Run the container

```bash
docker run -d -p 5000:5000 --name downloader flask-downloader
```

### (Optional) Mount a local download folder

```bash
docker run -d -p 5000:5000 \
  -v "$(pwd)/downloads:/app/downloads" \
  --name downloader \
  flask-downloader
```

---

## 🧩 Docker Compose (Optional)

Create a file named `docker-compose.yml`:

```yaml
version: "3.8"

services:
  downloader:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./downloads:/app/downloads
    container_name: flask_downloader
```

Then run:

```bash
docker-compose up -d
```

---

## 🌐 API Endpoints

| Method | Endpoint    | Description                                            |
| ------ | ----------- | ------------------------------------------------------ |
| `GET`  | `/`         | List all download tasks                                |
| `POST` | `/download` | Start a download (requires `url` and `local_filename`) |
| `GET`  | `/progress` | Get progress (`task_id` param)                         |
| `POST` | `/stop`     | Stop a download (`task_id` param)                      |
| `POST` | `/resume`   | Resume a stopped download (`task_id`)                  |
| `POST` | `/cancel`   | Cancel and delete a download (`task_id`)               |

---

## 🖥️ Web Interface

Open your browser at:

```
http://localhost:5000
```

Use the form to enter:

* `URL`: Direct link to the file
* `Filename`: What to save it as

Track progress and control downloads in real time.

---

## 📁 Example

```bash
curl -X POST \
  "http://localhost:5000/download?url=https://example.com/file.zip&local_filename=test.zip"
```

---

## 📄 License

MIT — use freely and modify as needed.

```

---

Let me know if you want me to generate the `docker-compose.yml` as a file too.
```
