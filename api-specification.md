
📦 File Download API Specification
Base URL

http://<your-server-address>/

Endpoints
GET /
Description

Returns a list of successfully downloaded files.
Response

[
  {
    "id": "uuid",
    "url": "https://example.com/file.zip",
    "filename": "file.zip"
  },
  ...
]

Status Codes

    200 OK – List of downloaded files.

POST /download?url=<file_url>
Description

Starts downloading a file from the specified url. The download is handled in a separate thread and tracked by a task_id.
Query Parameters
Name	Type	Required	Description
url	string	✅	The direct link to the file you want to download.
Response

{
  "message": "Download started",
  "task_id": "string"
}

Status Codes

    200 OK – Download started.

    400 Bad Request – URL not provided.

GET /progress?task_id=<task_id>
Description

Returns the download progress of a file identified by task_id.
Query Parameters
Name	Type	Required	Description
task_id	string	✅	Task ID from the /download response.
Response (Example)

{
  "task_id": "string",
  "progress": 64.32  // in percent
}

Status Codes

    200 OK – Returns progress.

    400 Bad Request – Missing task_id.

    404 Not Found – Invalid or unknown task_id.

Notes

    Progress is tracked in-memory and lost if the server restarts.

    The server only supports downloads with a known Content-Length header.

    Downloaded files are saved in the current working directory.