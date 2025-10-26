# OpenCodeHub API Documentation

## Version Upload and Management API

This document describes the API endpoints for managing project versions in OpenCodeHub.

## Authentication

All API endpoints require authentication. The API uses Django's session authentication by default.

## Base URL

```
http://localhost:8000/api/
```

## Endpoints

### 1. Upload Version (2.2, 2.3, 2.5)

**Endpoint:** `POST /api/projects/{project_id}/versions/upload/`

**Description:** Upload a new version file for a project. This endpoint handles file storage and updates the database.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Authentication: Required

**Parameters:**
- `project_id` (path parameter): ID of the project
- `version_number` (required): Version number (e.g., "1.0.0")
- `description` (optional): Description of the version
- `version_file` (required): The file to upload
- `is_latest` (optional): Boolean to mark as latest version

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/projects/1/versions/upload/ \
  -H "X-CSRFToken: your-csrf-token" \
  -F "version_number=1.0.0" \
  -F "description=Initial release" \
  -F "version_file=@/path/to/file.zip" \
  -F "is_latest=true"
```

**Response:**
```json
{
  "id": 1,
  "project": 1,
  "version_number": "1.0.0",
  "description": "Initial release",
  "created_at": "2024-10-26T12:00:00Z",
  "created_by": {
    "id": 1,
    "username": "john_doe"
  },
  "version_file": "/media/project_versions/file.zip",
  "version_file_url": "http://localhost:8000/media/project_versions/file.zip",
  "file_size": 1024000,
  "file_type": "zip",
  "is_latest": true
}
```

### 2. List All Versions (3.1, 3.4)

**Endpoint:** `GET /api/projects/{project_id}/versions/`

**Description:** Fetch all versions linked to a specific project with pagination support.

**Request:**
- Method: `GET`
- Authentication: Required

**Query Parameters:**
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page (max: 100)
- `sort` (optional): Sort field (`created_at`, `-created_at`, `version_number`, `-version_number`)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/projects/1/versions/?page=1&page_size=10&sort=-created_at"
```

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/projects/1/versions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 5,
      "project": 1,
      "version_number": "2.0.0",
      "description": "Major update",
      "created_at": "2024-10-26T14:00:00Z",
      "created_by": {...},
      "version_file": "/media/project_versions/v2.zip",
      "file_size": 2048000,
      "file_type": "zip",
      "is_latest": true
    },
    // ... more versions
  ]
}
```

### 3. Get Latest Version

**Endpoint:** `GET /api/projects/{project_id}/versions/latest/`

**Description:** Get the latest version of a project.

**Response:**
```json
{
  "id": 5,
  "project": 1,
  "version_number": "2.0.0",
  "is_latest": true,
  // ... other fields
}
```

### 4. Set Latest Version (4.2)

**Endpoint:** `POST /api/projects/{project_id}/versions/{version_id}/set-latest/`

**Description:** Mark a specific version as the latest. Only project owners can perform this action.

**Response:**
```json
{
  "id": 3,
  "version_number": "1.5.0",
  "is_latest": true,
  // ... other fields
}
```

### 5. Download Version (5.1, 5.2, 5.4)

**Endpoint:** `GET /api/projects/{project_id}/versions/{version_id}/download/`

**Description:** Download a specific version file. Access permissions are verified before download.

**Security:** 
- Only project owner, shared users, or users accessing public projects can download
- File is served directly from Django media storage

**Response:** Binary file download with appropriate headers

### 6. Get Version Details

**Endpoint:** `GET /api/projects/{project_id}/versions/{version_id}/`

**Description:** Get detailed information about a specific version.

### 7. Update Version

**Endpoint:** `PATCH /api/projects/{project_id}/versions/{version_id}/`

**Description:** Update version metadata (description, is_latest flag).

**Request Body:**
```json
{
  "description": "Updated description",
  "is_latest": true
}
```

### 8. Delete Version

**Endpoint:** `DELETE /api/projects/{project_id}/versions/{version_id}/`

**Description:** Delete a specific version. Only project owners can delete versions.

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation error message",
  "field_errors": {
    "version_number": ["Version 1.0.0 already exists for this project"]
  }
}
```

### 403 Forbidden
```json
{
  "error": "You don't have permission to upload versions to this project"
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

## File Upload Restrictions

- **Maximum file size:** 50MB (configurable in settings)
- **Blocked extensions:** `.exe`, `.bat`, `.sh`, `.cmd`, `.com`, `.app`, `.dmg`, `.deb`, `.rpm`, `.msi`, `.scr`, `.vbs`, `.js.exe`

## Version Number Format

Version numbers should follow semantic versioning (e.g., "1.0.0", "2.1.3", "1.0.0-beta").

## Automatic Latest Version Marking

When uploading a new version:
1. If `is_latest=true` is specified, all other versions are unmarked as latest
2. If it's the first version for a project, it's automatically marked as latest
3. The newest upload is automatically marked as latest if no other version is marked

## Storage

- Version files are stored in `MEDIA_ROOT/project_versions/`
- Files are accessible via `MEDIA_URL/project_versions/`
- For production, consider using cloud storage (AWS S3, Supabase Storage, etc.)

## Testing

Use the provided `test_api.py` script to test all endpoints:

```bash
cd opencodehub
python test_api.py
```

## Integration with Frontend

The API returns JSON responses that can be easily consumed by frontend frameworks:

```javascript
// Example: Upload version using JavaScript
const formData = new FormData();
formData.append('version_number', '1.0.0');
formData.append('description', 'Initial release');
formData.append('version_file', fileInput.files[0]);
formData.append('is_latest', true);

fetch(`/api/projects/${projectId}/versions/upload/`, {
  method: 'POST',
  headers: {
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log('Version uploaded:', data));
```
