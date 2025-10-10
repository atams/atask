# Atask - Task Management API

Atask adalah aplikasi manajemen task/tugas yang dibangun dengan FastAPI dan terintegrasi dengan ATAMS (Atlas Authentication & Management System). Sistem ini menyediakan REST API lengkap untuk mengelola project, task, komentar, attachment, history, label, dan watcher.

## Daftar Isi

- [Fitur Utama](#fitur-utama)
- [Teknologi](#teknologi)
- [Instalasi](#instalasi)
- [Konfigurasi](#konfigurasi)
- [Menjalankan Aplikasi](#menjalankan-aplikasi)
- [API Endpoints](#api-endpoints)
  - [Master Data](#master-data)
  - [Projects](#projects)
  - [Tasks](#tasks)
  - [Comments](#comments)
  - [Attachments](#attachments)
  - [History](#history)
  - [Labels](#labels)
  - [Watchers](#watchers)
  - [Users](#users)
- [Penjelasan Parameter Unik](#penjelasan-parameter-unik)
- [Response Format](#response-format)
- [Authentication](#authentication)

## Fitur Utama

- **Manajemen Project**: CRUD lengkap untuk project dengan statistik task
- **Manajemen Task**: CRUD task dengan support sub-task, prioritas, status, dan tipe
- **Komentar & Diskusi**: Sistem komentar dengan threading (reply to comment)
- **File Attachment**: Upload dan download file untuk setiap task ⚠️ *Under Development*
- **Audit Trail**: Otomatis tracking perubahan task di history
- **Labeling System**: Tag/label fleksibel untuk kategorisasi task
- **Task Watcher**: Subscribe untuk mendapat notifikasi perubahan task
- **Advanced Search**: Pencarian task dengan multiple filter
- **Bulk Operations**: Update status multiple task sekaligus
- **User Dashboard**: Dashboard personal dengan statistik dan aktivitas
- **Response Encryption**: Enkripsi otomatis untuk response data (opsional)
- **Atlas SSO Integration**: Autentikasi terintegrasi dengan ATAMS
- **Role-based Access**: Kontrol akses berdasarkan role level user

## Teknologi

- **Framework**: FastAPI (Python 3.8+)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Atlas SSO (ATAMS)
- **Validation**: Pydantic
- **Server**: Uvicorn

## Instalasi

1. **Clone repository**
```bash
git clone https://github.com/GratiaManullang03/atask.git
cd atask
```

2. **Buat virtual environment**
```bash
python -m venv venv
```

3. **Aktifkan virtual environment**
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Konfigurasi

Buat file `.env` di root folder project dengan konfigurasi berikut:

```env
# Application
APP_NAME=atask
APP_VERSION=1.0.0
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Atlas SSO (ATAMS)
ATLAS_SSO_URL=https://atlas.yourdomain.com/api
ATLAS_APP_CODE=atask
ATLAS_ENCRYPTION_KEY=your-32-char-encryption-key
ATLAS_ENCRYPTION_IV=your-16-char-iv

# Response Encryption (Optional)
ENCRYPTION_ENABLED=true
ENCRYPTION_KEY=your-32-char-response-key
ENCRYPTION_IV=your-16-char-response-iv

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Logging
LOGGING_ENABLED=true
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_FILE_PATH=logs/atask.log
```

## Menjalankan Aplikasi

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Aplikasi akan berjalan di `http://localhost:8000`

- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

Base URL: `/api/v1`

### Master Data

#### Master Status
Endpoint untuk mengelola master data status task (To Do, In Progress, Done, dll).

- `GET /api/v1/master-statuses` - Get all status
- `GET /api/v1/master-statuses/{ms_id}` - Get status by ID
- `POST /api/v1/master-statuses` - Create new status
- `PUT /api/v1/master-statuses/{ms_id}` - Update status
- `DELETE /api/v1/master-statuses/{ms_id}` - Delete status

#### Master Priority
Endpoint untuk mengelola master data prioritas task (Low, Medium, High, Critical).

- `GET /api/v1/master-priorities` - Get all priorities
- `GET /api/v1/master-priorities/{mp_id}` - Get priority by ID
- `POST /api/v1/master-priorities` - Create new priority
- `PUT /api/v1/master-priorities/{mp_id}` - Update priority
- `DELETE /api/v1/master-priorities/{mp_id}` - Delete priority

#### Master Task Type
Endpoint untuk mengelola master data tipe task (Task, Bug, Feature, dll).

- `GET /api/v1/master-task-types` - Get all task types
- `GET /api/v1/master-task-types/{mtt_id}` - Get task type by ID
- `POST /api/v1/master-task-types` - Create new task type
- `PUT /api/v1/master-task-types/{mtt_id}` - Update task type
- `DELETE /api/v1/master-task-types/{mtt_id}` - Delete task type

### Projects

#### Create Project
```http
POST /api/v1/projects
```

**Request Body:**
```json
{
  "prj_code": "PROJ-001",
  "prj_name": "Website Redesign",
  "prj_description": "Redesign company website with modern UI/UX",
  "prj_start_date": "2025-01-15",
  "prj_end_date": "2025-06-30",
  "prj_u_id": 123,
  "prj_is_active": true
}
```

**Response:** `201 Created`

#### Get All Projects
```http
GET /api/v1/projects?skip=0&limit=100
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100) - Maximum records to return

**Response:** `200 OK` dengan pagination

#### Get Project by ID
```http
GET /api/v1/projects/{prj_id}
```

**Response:** `200 OK`

#### Update Project
```http
PUT /api/v1/projects/{prj_id}
```

**Request Body:** (semua field opsional)
```json
{
  "prj_name": "Website Redesign v2",
  "prj_description": "Updated description",
  "prj_end_date": "2025-07-15",
  "prj_is_active": true
}
```

**Response:** `200 OK`

#### Delete Project
```http
DELETE /api/v1/projects/{prj_id}
```

**Response:** `204 No Content`

#### Get Project Statistics
```http
GET /api/v1/projects/{prj_id}/statistics
```

**Response:** `200 OK` - Statistik lengkap task di project (jumlah by status, priority, type, overdue, dll)

### Tasks

#### Create Task
```http
POST /api/v1/tasks
```

**Request Body:**
```json
{
  "tsk_code": "TSK-001",
  "tsk_title": "Design homepage mockup",
  "tsk_description": "Create high-fidelity mockup for homepage redesign",
  "tsk_prj_id": 1,
  "tsk_ms_id": 1,
  "tsk_mp_id": 3,
  "tsk_mtt_id": 1,
  "tsk_assignee_u_id": 456,
  "tsk_reporter_u_id": 123,
  "tsk_start_date": "2025-01-20T09:00:00Z",
  "tsk_due_date": "2025-01-25T17:00:00Z",
  "tsk_duration": 40.00,
  "tsk_parent_tsk_id": null
}
```

**Response:** `201 Created`

#### Get All Tasks
```http
GET /api/v1/tasks?skip=0&limit=100
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100) - Maximum records to return

**Response:** `200 OK` dengan pagination

#### Get Task by ID
```http
GET /api/v1/tasks/{tsk_id}
```

**Response:** `200 OK` - Detail lengkap task dengan relasi (labels, watchers, attachments, subtasks)

#### Update Task
```http
PUT /api/v1/tasks/{tsk_id}
```

**Request Body:** (semua field opsional)
```json
{
  "tsk_title": "Design homepage mockup v2",
  "tsk_description": "Updated description",
  "tsk_ms_id": 2,
  "tsk_mp_id": 4,
  "tsk_assignee_u_id": 789,
  "tsk_due_date": "2025-01-28T17:00:00Z"
}
```

**Response:** `200 OK`

#### Delete Task
```http
DELETE /api/v1/tasks/{tsk_id}
```

**Response:** `204 No Content`

#### Bulk Update Status
```http
PATCH /api/v1/tasks/bulk-update-status
```

**Request Body:**
```json
{
  "task_ids": [1, 2, 3, 5],
  "ms_id": 4
}
```

**Response:** `200 OK` - Info jumlah task yang berhasil diupdate

#### Advanced Search
```http
POST /api/v1/tasks/search
```

**Request Body:**
```json
{
  "keyword": "design",
  "project_ids": [1, 2],
  "status_ids": [1, 2],
  "priority_ids": [3, 4],
  "type_ids": [1],
  "assignee_ids": [456],
  "reporter_ids": [123],
  "date_from": "2025-01-01",
  "date_to": "2025-12-31",
  "skip": 0,
  "limit": 20
}
```

**Response:** `200 OK` dengan pagination

### Comments

#### Create Comment
```http
POST /api/v1/tasks/{tsk_id}/comments
```

**Request Body:**
```json
{
  "tc_comment": "This looks great! Please add the color scheme.",
  "tc_parent_tc_id": null
}
```

**Response:** `201 Created`

#### Get All Comments for Task
```http
GET /api/v1/tasks/{tsk_id}/comments?skip=0&limit=100
```

**Response:** `200 OK` dengan pagination

#### Get Comment by ID
```http
GET /api/v1/comments/{tc_id}
```

**Response:** `200 OK`

#### Update Comment
```http
PUT /api/v1/comments/{tc_id}
```

**Request Body:**
```json
{
  "tc_comment": "Updated comment text"
}
```

**Response:** `200 OK`

#### Delete Comment
```http
DELETE /api/v1/comments/{tc_id}
```

**Response:** `204 No Content`

### Attachments

> **⚠️ UNDER DEVELOPMENT**: Fitur attachment sedang dalam pengembangan. Semua endpoint attachment akan mengembalikan response `"Attachment feature is currently under development"` untuk sementara waktu.

#### Upload Attachment
```http
POST /api/v1/tasks/{tsk_id}/attachments
Content-Type: multipart/form-data
```

**Request Body:**
```
file: [binary file]
```

**Response:** `201 Created` (Under Development)
```json
{
  "success": false,
  "message": "Attachment feature is currently under development",
  "data": null
}
```

#### Get All Attachments for Task
```http
GET /api/v1/tasks/{tsk_id}/attachments
```

**Response:** `200 OK` (Under Development)

#### Get Attachment by ID
```http
GET /api/v1/attachments/{ta_id}
```

**Response:** `200 OK` (Under Development)

#### Download Attachment
```http
GET /api/v1/attachments/{ta_id}/download
```

**Response:** (Under Development)

#### Delete Attachment
```http
DELETE /api/v1/attachments/{ta_id}
```

**Response:** `204 No Content` (Under Development)

### History

#### Get Task History
```http
GET /api/v1/tasks/{tsk_id}/history?skip=0&limit=100&field_name=status
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100) - Maximum records to return
- `field_name` (optional) - Filter by specific field name (status, priority, assignee, dll)

**Response:** `200 OK` dengan pagination

#### Get History by ID
```http
GET /api/v1/history/{th_id}
```

**Response:** `200 OK`

### Labels

#### Create Label
```http
POST /api/v1/labels
```

**Request Body:**
```json
{
  "lbl_name": "frontend",
  "lbl_color": "#3498db",
  "lbl_description": "Frontend related tasks"
}
```

**Response:** `201 Created`

#### Get All Labels
```http
GET /api/v1/labels?skip=0&limit=100&search=frontend
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100) - Maximum records to return
- `search` (optional) - Search by label name

**Response:** `200 OK` dengan pagination

#### Get Label by ID
```http
GET /api/v1/labels/{lbl_id}
```

**Response:** `200 OK` - Detail label dengan list task yang menggunakan label ini

#### Update Label
```http
PUT /api/v1/labels/{lbl_id}
```

**Request Body:**
```json
{
  "lbl_name": "frontend-ui",
  "lbl_color": "#3498db",
  "lbl_description": "Frontend UI/UX related tasks"
}
```

**Response:** `200 OK`

#### Delete Label
```http
DELETE /api/v1/labels/{lbl_id}
```

**Response:** `204 No Content`

#### Assign Label to Task
```http
POST /api/v1/tasks/{tsk_id}/labels
```

**Request Body:**
```json
{
  "lbl_id": 1
}
```

**Response:** `201 Created`

#### Get All Labels for Task
```http
GET /api/v1/tasks/{tsk_id}/labels
```

**Response:** `200 OK` - List label untuk task tertentu

#### Remove Label from Task
```http
DELETE /api/v1/tasks/{tsk_id}/labels/{lbl_id}
```

**Response:** `204 No Content`

### Watchers

#### Add Watcher to Task
```http
POST /api/v1/tasks/{tsk_id}/watchers
```

**Request Body:**
```json
{
  "u_id": 789
}
```

**Response:** `201 Created`

#### Get All Watchers for Task
```http
GET /api/v1/tasks/{tsk_id}/watchers
```

**Response:** `200 OK` - List user yang watch task ini

#### Remove Watcher from Task
```http
DELETE /api/v1/tasks/{tsk_id}/watchers/{u_id}
```

**Response:** `204 No Content`

### Users

#### Get All Users
```http
GET /api/v1/users?skip=0&limit=100&search=john
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100) - Maximum records to return
- `search` (optional) - Search by username, email, or full name

**Response:** `200 OK` dengan pagination

#### Get User Dashboard
```http
GET /api/v1/users/{u_id}/dashboard
```

**Response:** `200 OK` - Dashboard user dengan statistik (assigned tasks, reported tasks, watched tasks, recent activities)

#### Get Watched Tasks by User
```http
GET /api/v1/users/{u_id}/watched-tasks?skip=0&limit=100&status_id=2
```

**Query Parameters:**
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 100) - Maximum records to return
- `status_id` (optional) - Filter by status ID

**Response:** `200 OK` dengan pagination

## Penjelasan Parameter Unik

### Project Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `prj_id` | Integer | ID unik project (Primary Key) |
| `prj_code` | String | Kode project yang unique, contoh: "PROJ-001", "WEBSITE-REDESIGN" |
| `prj_name` | String | Nama project |
| `prj_description` | Text | Deskripsi lengkap project |
| `prj_start_date` | Date | Tanggal mulai project (format: YYYY-MM-DD) |
| `prj_end_date` | Date | Target tanggal selesai project (format: YYYY-MM-DD) |
| `prj_u_id` | Integer | ID user yang menjadi owner/penanggung jawab project (Foreign Key ke tabel users) |
| `prj_is_active` | Boolean | Status apakah project masih aktif atau sudah selesai/ditutup |

### Task Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `tsk_id` | Integer | ID unik task (Primary Key) |
| `tsk_code` | String | Kode task yang unique, contoh: "TSK-001", "BUG-123" |
| `tsk_title` | String | Judul/ringkasan task |
| `tsk_description` | Text | Deskripsi lengkap task, bisa berisi requirement detail |
| `tsk_prj_id` | Integer | ID project yang memiliki task ini (Foreign Key, opsional - task bisa tidak terikat project) |
| `tsk_ms_id` | Integer | ID master status task (Foreign Key ke master_status) - status saat ini: To Do, In Progress, Done, dll |
| `tsk_mp_id` | Integer | ID master priority task (Foreign Key ke master_priority) - prioritas: Low, Medium, High, Critical |
| `tsk_mtt_id` | Integer | ID master task type (Foreign Key ke master_task_type) - tipe: Task, Bug, Feature, Improvement, dll |
| `tsk_assignee_u_id` | Integer | ID user yang ditugaskan mengerjakan task (Foreign Key ke users, opsional) |
| `tsk_reporter_u_id` | Integer | ID user yang membuat/melaporkan task (Foreign Key ke users) |
| `tsk_start_date` | Timestamp | Tanggal dan waktu mulai pengerjaan task (format: ISO 8601) |
| `tsk_due_date` | Timestamp | Deadline task (format: ISO 8601) |
| `tsk_duration` | Decimal | Estimasi waktu yang dibutuhkan untuk task (dalam jam, contoh: 40.00) |
| `tsk_parent_tsk_id` | Integer | ID task parent jika ini adalah sub-task (Foreign Key ke task lain, untuk hierarki task) |

### Comment Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `tc_id` | Integer | ID unik comment (Primary Key) |
| `tc_tsk_id` | Integer | ID task yang dikomentari (Foreign Key ke task) |
| `tc_u_id` | Integer | ID user yang menulis comment (Foreign Key ke users) |
| `tc_comment` | Text | Isi komentar/diskusi |
| `tc_parent_tc_id` | Integer | ID comment parent jika ini reply (Foreign Key ke comment lain, untuk threading/nested comments) |

### Attachment Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `ta_id` | Integer | ID unik attachment (Primary Key) |
| `ta_tsk_id` | Integer | ID task yang memiliki attachment (Foreign Key ke task) |
| `ta_file_name` | String | Nama file original yang diupload |
| `ta_file_path` | String | Path/lokasi penyimpanan file di server atau cloud storage |
| `ta_file_size` | Integer | Ukuran file dalam bytes |
| `ta_file_type` | String | Ekstensi file (pdf, jpg, png, docx, dll) |

### History Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `th_id` | Integer | ID unik history record (Primary Key) |
| `th_tsk_id` | Integer | ID task yang mengalami perubahan (Foreign Key ke task) |
| `th_field_name` | String | Nama field yang diubah (status, priority, assignee, due_date, dll) |
| `th_old_value` | String | Nilai lama sebelum perubahan |
| `th_new_value` | String | Nilai baru setelah perubahan |
| `th_u_id` | Integer | ID user yang melakukan perubahan (Foreign Key ke users) |

### Label Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `lbl_id` | Integer | ID unik label (Primary Key) |
| `lbl_name` | String | Nama label yang unique (frontend, backend, urgent, documentation, dll) |
| `lbl_color` | String | Kode warna hex untuk visualisasi (#3498db, #e74c3c, dll) |
| `lbl_description` | String | Deskripsi kegunaan label |

### Task Label Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `tl_id` | Integer | ID unik relasi task-label (Primary Key) |
| `tl_tsk_id` | Integer | ID task yang diberi label (Foreign Key ke task) |
| `tl_lbl_id` | Integer | ID label yang ditempelkan (Foreign Key ke label) |

> **Note:** Kombinasi `tl_tsk_id` dan `tl_lbl_id` adalah unique - satu task tidak bisa memiliki label yang sama lebih dari sekali.

### Watcher Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `tw_id` | Integer | ID unik relasi watcher (Primary Key) |
| `tw_tsk_id` | Integer | ID task yang di-watch (Foreign Key ke task) |
| `tw_u_id` | Integer | ID user yang menjadi watcher/pengamat (Foreign Key ke users) |

> **Note:** Kombinasi `tw_tsk_id` dan `tw_u_id` adalah unique - satu user tidak bisa watch task yang sama lebih dari sekali. User yang menjadi watcher akan mendapat notifikasi setiap ada perubahan pada task.

### Master Status Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `ms_id` | Integer | ID unik status (Primary Key) |
| `ms_code` | String | Kode status machine-readable (TODO, IN_PROGRESS, IN_REVIEW, DONE, CANCELLED) |
| `ms_name` | String | Nama status yang ditampilkan ("To Do", "In Progress", "In Review", "Done", "Cancelled") |
| `ms_description` | Text | Penjelasan detail tentang status |
| `ms_is_active` | Boolean | Penanda apakah status masih aktif digunakan |

### Master Priority Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `mp_id` | Integer | ID unik priority (Primary Key) |
| `mp_code` | String | Kode prioritas (LOW, MEDIUM, HIGH, CRITICAL) |
| `mp_name` | String | Nama prioritas ditampilkan ("Low", "Medium", "High", "Critical") |
| `mp_level` | Integer | Level prioritas dalam angka (1=terendah, 4=tertinggi) - berguna untuk sorting |
| `mp_color` | String | Kode warna hex (#2ecc71 untuk low, #FF0000 untuk critical) |
| `mp_is_active` | Boolean | Status aktif/nonaktif prioritas |

### Master Task Type Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `mtt_id` | Integer | ID unik task type (Primary Key) |
| `mtt_code` | String | Kode tipe task (TASK, BUG, FEATURE, IMPROVEMENT, RESEARCH) |
| `mtt_name` | String | Nama tipe task ("Task", "Bug", "Feature", "Improvement", "Research") |
| `mtt_description` | Text | Deskripsi dari tipe task |
| `mtt_is_active` | Boolean | Status aktif/nonaktif tipe task |

## Response Format

### Success Response dengan Data
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Success Response dengan Pagination
```json
{
  "success": true,
  "message": "Data retrieved successfully",
  "data": [ ... ],
  "total": 100,
  "page": 1,
  "size": 10,
  "pages": 10
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "details": { ... }
}
```

## Authentication

Semua endpoint memerlukan authentication header:

```
Authorization: Bearer {token}
```

Token didapat dari Atlas SSO. Setiap request akan divalidasi dengan Atlas dan mendapat informasi user (user_id, role_level, dll).

**Minimum Role Level**: Sebagian besar endpoint memerlukan role level minimal 10.

## Audit Fields

Setiap tabel memiliki audit fields untuk tracking:

- `created_by` - Username/ID yang membuat record
- `created_at` - Timestamp pembuatan
- `updated_by` - Username/ID yang terakhir update
- `updated_at` - Timestamp update terakhir

## Response Encryption

Response data bisa di-enkripsi otomatis jika `ENCRYPTION_ENABLED=true` di environment variable. Client perlu mendekripsi response dengan key dan IV yang sesuai.

## Catatan Penting

1. **Soft Delete**: Sistem menggunakan hard delete. Pertimbangkan implementasi soft delete untuk data penting.

2. **Cascade Delete**: Ketika task dihapus, semua data terkait (comments, attachments, history, labels, watchers) akan ikut terhapus.

3. **Validation Rules**:
   - Task code harus unique
   - Project code harus unique
   - Label name harus unique
   - Due date tidak boleh lebih awal dari start date
   - Satu user tidak bisa menjadi watcher task yang sama lebih dari sekali
   - Satu task tidak bisa memiliki label yang sama lebih dari sekali

4. **File Upload** (Under Development):
   - Fitur attachment sedang dalam pengembangan
   - Semua endpoint attachment akan return "under development" message
   - Future plan: File disimpan di folder `uploads/tasks/{tsk_id}/`
   - Future plan: Batasan ukuran file (misal: max 10MB)
   - Future plan: Support semua tipe file

5. **History Tracking**:
   - Setiap perubahan pada task otomatis tercatat di `task_history`
   - Field yang di-track: status, priority, assignee, due_date, dll

6. **Performance**:
   - Database sudah menggunakan indexing untuk kolom yang sering di-query
   - Response data ter-enkripsi jika enabled untuk keamanan ekstra

## License

[Specify your license here]

## =e Contributors

[List contributors or link to contributors page]

## Support

Untuk pertanyaan atau issue, silakan hubungi tim development atau buat issue di repository.
