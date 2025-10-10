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
  - [Nested Resources](#nested-resources)
  - [Labels](#labels)
  - [Users](#users)
- [Penjelasan Parameter Unik](#penjelasan-parameter-unik)
- [Response Format](#response-format)
- [Authentication & Authorization](#authentication--authorization)
- [Validation Rules](#validation-rules)

## Fitur Utama

- **Manajemen Project**: CRUD lengkap untuk project dengan statistik task dan auto-join owner information
- **Manajemen Task**: CRUD task dengan support sub-task, prioritas, status, dan tipe
- **Auto-Generated Task Code**: Task code otomatis dihasilkan berdasarkan project dan tipe task
- **Task Duration Auto-Calculate**: Durasi otomatis dihitung dalam jam dari start_date sampai due_date
- **Komentar & Diskusi**: Sistem komentar dengan threading (reply to comment)
- **File Attachment**: Upload dan download file untuk setiap task ⚠️ *Under Development*
- **Immutable Audit Trail**: Otomatis tracking perubahan task di history (log-only, tidak bisa diubah/dihapus)
- **Labeling System**: Tag/label fleksibel untuk kategorisasi task dengan bulk operations
- **Task Watcher**: Subscribe untuk mendapat notifikasi perubahan task dengan bulk operations
- **Advanced Search**: Pencarian task dengan multiple filter
- **Bulk Operations**: Update status multiple task sekaligus
- **User Dashboard**: Dashboard personal dengan statistik dan aktivitas
- **Response Encryption**: Enkripsi otomatis untuk response data (opsional)
- **Atlas SSO Integration**: Autentikasi terintegrasi dengan ATAMS
- **Role-based Access**: Kontrol akses berdasarkan role level user
- **Creator-only Modification**: Hanya pembuat (creator) yang bisa update/delete resource

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
- `PUT /api/v1/master-statuses/{ms_id}` - Update status (creator only)
- `DELETE /api/v1/master-statuses/{ms_id}` - Delete status (creator only)

#### Master Priority
Endpoint untuk mengelola master data prioritas task (Low, Medium, High, Critical).

- `GET /api/v1/master-priorities` - Get all priorities
- `GET /api/v1/master-priorities/{mp_id}` - Get priority by ID
- `POST /api/v1/master-priorities` - Create new priority
- `PUT /api/v1/master-priorities/{mp_id}` - Update priority (creator only)
- `DELETE /api/v1/master-priorities/{mp_id}` - Delete priority (creator only)

#### Master Task Type
Endpoint untuk mengelola master data tipe task (Task, Bug, Feature, dll).

- `GET /api/v1/master-task-types` - Get all task types
- `GET /api/v1/master-task-types/{mtt_id}` - Get task type by ID
- `POST /api/v1/master-task-types` - Create new task type
- `PUT /api/v1/master-task-types/{mtt_id}` - Update task type (creator only)
- `DELETE /api/v1/master-task-types/{mtt_id}` - Delete task type (creator only)

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

**Response:** `201 Created` dengan field tambahan `prj_owner_name` (auto-joined)

#### Get All Projects
```http
GET /api/v1/projects?skip=0&limit=100
```

**Response:** `200 OK` - Semua project dengan `prj_owner_name` (auto-joined)

#### Get Project by ID
```http
GET /api/v1/projects/{prj_id}
```

**Response:** `200 OK` - Detail project dengan `prj_owner_name` (auto-joined)

#### Update Project
```http
PUT /api/v1/projects/{prj_id}
```

**Authorization:** ⚠️ **Only creator (created_by) can update**

**Request Body:** (semua field opsional)
```json
{
  "prj_name": "Website Redesign v2",
  "prj_description": "Updated description",
  "prj_end_date": "2025-07-15",
  "prj_is_active": true
}
```

**Response:** `200 OK` atau `403 Forbidden` jika bukan creator

#### Delete Project
```http
DELETE /api/v1/projects/{prj_id}
```

**Authorization:** ⚠️ **Only creator (created_by) can delete**

**Response:** `204 No Content` atau `403 Forbidden`

#### Get Project Statistics
```http
GET /api/v1/projects/{prj_id}/statistics
```

**Response:** `200 OK` - Statistik lengkap dengan struktur nested:
```json
{
  "prj_id": 1,
  "prj_name": "Website Redesign",
  "total_tasks": 50,
  "by_status": {
    "TODO": 10,
    "IN_PROGRESS": 15,
    "IN_REVIEW": 5,
    "DONE": 18,
    "CANCELLED": 2
  },
  "by_priority": {
    "LOW": 8,
    "MEDIUM": 20,
    "HIGH": 15,
    "CRITICAL": 7
  },
  "by_type": {
    "TASK": 25,
    "BUG": 12,
    "FEATURE": 8,
    "IMPROVEMENT": 3,
    "RESEARCH": 2
  },
  "overdue_tasks": 3,
  "completion_rate": 0.36,
  "average_completion_time": 72.5
}
```

### Tasks

#### Create Task
```http
POST /api/v1/tasks
```

**Request Body:**
```json
{
  "tsk_title": "Design homepage mockup",
  "tsk_description": "Create high-fidelity mockup for homepage redesign",
  "tsk_prj_id": 1,
  "tsk_ms_id": 1,
  "tsk_mp_id": 3,
  "tsk_mtt_id": 1,
  "tsk_assignee_u_id": 456,
  "tsk_reporter_u_id": 123,
  "tsk_start_date": "2025-01-20T09:00:00Z",
  "tsk_parent_tsk_id": null
}
```

**Important Notes:**
- ✅ `tsk_code` is **auto-generated** (format: `{prj_id}/{task_type_code}/{number}`)
- ❌ `tsk_due_date` **cannot be set at creation** (only assignee can set it later)
- ❌ `tsk_duration` **is auto-calculated** (read-only, in hours)

**Response:** `201 Created` dengan joins:
```json
{
  "tsk_code": "001/TASK/001",
  "tsk_title": "Design homepage mockup",
  "tsk_duration": null,
  "tsk_project_name": "Website Redesign",
  "tsk_status_name": "To Do",
  "tsk_priority_name": "High",
  "tsk_priority_color": "#FF9800",
  "tsk_type_name": "Task",
  "tsk_assignee_name": "John Doe",
  "tsk_reporter_name": "Jane Smith"
}
```

#### Get All Tasks
```http
GET /api/v1/tasks?skip=0&limit=100
```

**Response:** `200 OK` - All tasks dengan auto-joins (project_name, status_name, dll)

#### Get Task by ID
```http
GET /api/v1/tasks/{tsk_id}
```

**Response:** `200 OK` - Detail lengkap dengan auto-joins

#### Update Task
```http
PUT /api/v1/tasks/{tsk_id}
```

**Authorization:** ⚠️ **Only creator (created_by) can update**

**Request Body:** (semua field opsional)
```json
{
  "tsk_title": "Design homepage mockup v2",
  "tsk_description": "Updated description",
  "tsk_ms_id": 2,
  "tsk_mp_id": 4,
  "tsk_assignee_u_id": 789,
  "tsk_start_date": "2025-01-20T09:00:00Z",
  "tsk_due_date": "2025-01-25T17:00:00Z"
}
```

**Special Rules:**
- ✅ `tsk_due_date` **can only be set by assignee** (or null to clear)
- ✅ `due_date >= start_date` (validation error jika due_date lebih awal)
- ✅ `tsk_duration` **auto-calculated in hours** dari (due_date - start_date)
- ❌ `tsk_duration` **cannot be manually set** (read-only)
- ❌ Non-creator **cannot update task** (403 Forbidden)

**Response:** `200 OK` atau `400 Bad Request` atau `403 Forbidden`

#### Delete Task
```http
DELETE /api/v1/tasks/{tsk_id}
```

**Authorization:** ⚠️ **Only creator (created_by) can delete**

**Response:** `204 No Content` atau `403 Forbidden`

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

**Response:** `200 OK` dengan pagination dan auto-joins

### Nested Resources

> **Important:** Comments, History, Labels, dan Watchers adalah nested resources di bawah task.
> Standalone endpoints (`/api/v1/comments`, `/api/v1/history`, dll) **sudah dihapus**.

#### Task Comments

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

```http
GET /api/v1/tasks/{tsk_id}/comments?skip=0&limit=100
```
**Response:** List comments dengan auto-joins: `tc_task_title`, `tc_user_name`, `tc_user_email`

#### Task History (Audit Log)

```http
GET /api/v1/tasks/{tsk_id}/history?skip=0&limit=100&field_name=status
```

**Important:**
- 📝 History adalah **immutable audit log**
- ✅ **Auto-created** saat task diupdate
- ✅ **Only GET** endpoint available
- ❌ **NO POST/PUT/DELETE** endpoints (tidak bisa manual create/update/delete)
- ❌ **NO updated_by/updated_at** fields (log is immutable)

**Response:** List history dengan auto-joins: `th_task_title`, `th_user_name`

**Tracked Fields:**
- `title`, `description`, `status`, `priority`, `assignee`, `due_date`, `start_date`

#### Task Labels

```http
POST /api/v1/tasks/{tsk_id}/labels
```
**Request Body:**
```json
{
  "tl_lbl_id": 1
}
```

```http
GET /api/v1/tasks/{tsk_id}/labels
```
**Response:** List labels dengan auto-joins: `tl_task_title`, `tl_label_name`, `tl_label_color`

```http
DELETE /api/v1/tasks/{tsk_id}/labels/{lbl_ids}
```
**Bulk Delete:** `lbl_ids` bisa comma-separated (e.g., `1,2,3`)

#### Task Watchers

```http
POST /api/v1/tasks/{tsk_id}/watchers
```
**Request Body:**
```json
{
  "tw_u_id": 789
}
```

```http
GET /api/v1/tasks/{tsk_id}/watchers
```
**Response:** List watchers dengan auto-joins: `tw_task_title`, `tw_user_name`, `tw_user_email`

```http
DELETE /api/v1/tasks/{tsk_id}/watchers/{u_ids}
```
**Bulk Delete:** `u_ids` bisa comma-separated (e.g., `2,3,4`)

#### Task Attachments

> **⚠️ UNDER DEVELOPMENT**: Semua endpoint akan return `"Attachment feature is currently under development"`

```http
POST /api/v1/tasks/{tsk_id}/attachments
```
```http
GET /api/v1/tasks/{tsk_id}/attachments
```

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

#### Get All Labels
```http
GET /api/v1/labels?skip=0&limit=100&search=frontend
```

#### Get Label by ID
```http
GET /api/v1/labels/{lbl_id}
```

#### Update Label
```http
PUT /api/v1/labels/{lbl_id}
```

#### Delete Label
```http
DELETE /api/v1/labels/{lbl_id}
```

### Users

#### Get All Users
```http
GET /api/v1/users?skip=0&limit=100&search=john
```

**Response:** List users dari Atlas SSO

#### Get User Dashboard
```http
GET /api/v1/users/{u_id}/dashboard
```

**Response:** Dashboard user dengan statistik (assigned tasks, reported tasks, watched tasks, recent activities)

#### Get Watched Tasks by User
```http
GET /api/v1/users/{u_id}/watched-tasks?skip=0&limit=100&status_id=2
```

## Penjelasan Parameter Unik

### Project Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `prj_id` | Integer | ID unik project (Primary Key) |
| `prj_code` | String | Kode project yang unique |
| `prj_name` | String | Nama project |
| `prj_description` | Text | Deskripsi lengkap project |
| `prj_start_date` | Date | Tanggal mulai project |
| `prj_end_date` | Date | Target tanggal selesai project |
| `prj_u_id` | Integer | ID user owner project |
| `prj_owner_name` | String | **Auto-joined** nama owner dari Atlas users |
| `prj_is_active` | Boolean | Status project aktif/nonaktif |

### Task Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `tsk_id` | Integer | ID unik task (Primary Key) |
| `tsk_code` | String | **Auto-generated** format: `{prj_id}/{type_code}/{number}` |
| `tsk_title` | String | Judul/ringkasan task |
| `tsk_description` | Text | Deskripsi lengkap task |
| `tsk_prj_id` | Integer | ID project (required) |
| `tsk_ms_id` | Integer | ID master status (required) |
| `tsk_mp_id` | Integer | ID master priority (required) |
| `tsk_mtt_id` | Integer | ID master task type (required) |
| `tsk_assignee_u_id` | Integer | ID user assigned (optional) |
| `tsk_reporter_u_id` | Integer | ID user reporter (required) |
| `tsk_start_date` | Timestamp | Tanggal mulai |
| `tsk_due_date` | Timestamp | Deadline (**only assignee can set**) |
| `tsk_duration` | Decimal | **Auto-calculated in hours** (read-only) |
| `tsk_parent_tsk_id` | Integer | ID parent task untuk sub-task |
| `tsk_project_name` | String | **Auto-joined** nama project |
| `tsk_status_name` | String | **Auto-joined** nama status |
| `tsk_priority_name` | String | **Auto-joined** nama priority |
| `tsk_priority_color` | String | **Auto-joined** warna priority |
| `tsk_type_name` | String | **Auto-joined** nama type |
| `tsk_assignee_name` | String | **Auto-joined** nama assignee |
| `tsk_reporter_name` | String | **Auto-joined** nama reporter |

### History Parameters

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `th_id` | Integer | ID unik history (Primary Key) |
| `th_tsk_id` | Integer | ID task yang berubah |
| `th_field_name` | String | Field yang diubah |
| `th_old_value` | String | Nilai lama |
| `th_new_value` | String | Nilai baru |
| `th_u_id` | Integer | ID user yang mengubah |
| `th_task_title` | String | **Auto-joined** judul task |
| `th_user_name` | String | **Auto-joined** nama user |
| `created_by` | String | User yang membuat record |
| `created_at` | Timestamp | Waktu pembuatan |

**Note:** History **tidak memiliki** `updated_by` dan `updated_at` (immutable log)

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

## Authentication & Authorization

### Authentication

Semua endpoint memerlukan authentication header:

```
Authorization: Bearer {token}
```

Token didapat dari Atlas SSO. Setiap request akan divalidasi dan mendapat informasi user (user_id, username, role_level, dll).

### Authorization Rules

**Minimum Role Level:** Role level minimal **10** untuk akses API.

**Creator-Only Operations:**
- ⚠️ **UPDATE**: Hanya creator (`created_by == current_user_id`) yang bisa update
- ⚠️ **DELETE**: Hanya creator (`created_by == current_user_id`) yang bisa delete
- Berlaku untuk: Projects, Tasks, Master Data

**Special Task Rules:**
- ⚠️ **tsk_due_date**: Hanya assignee (`tsk_assignee_u_id == current_user_id`) yang bisa set/update
- ⚠️ **tsk_duration**: Read-only, auto-calculated (tidak bisa manual set)

## Validation Rules

### Task Validation

1. **Task Code**: Auto-generated, format `{prj_id}/{type_code}/{number}` (e.g., `005/BUG/001`)
2. **Due Date**: Must be >= start_date (error jika due_date lebih awal)
3. **Duration**: Auto-calculated in **hours** from (due_date - start_date), read-only
4. **Assignee-Only Due Date**: Only assignee can set/update `tsk_due_date`
5. **Creator-Only Modification**: Only creator can update/delete task

### Project Validation

1. **Project Code**: Must be unique
2. **Creator-Only Modification**: Only creator can update/delete project

### History (Audit Log)

1. **Immutable Log**: Cannot be updated or deleted via API
2. **Auto-Created**: Automatically created on task updates
3. **No Manual Creation**: No POST endpoint available
4. **Tracked Fields**: title, description, status, priority, assignee, due_date, start_date

### Label & Watcher

1. **Unique Assignment**: Satu task tidak bisa memiliki label/watcher yang sama lebih dari sekali
2. **Bulk Delete**: Support comma-separated IDs (e.g., `DELETE /tasks/1/labels/1,2,3`)

## Audit Fields

Setiap tabel memiliki audit fields:

- `created_by` - ID user yang membuat
- `created_at` - Timestamp pembuatan
- `updated_by` - ID user yang terakhir update
- `updated_at` - Timestamp update terakhir

**Exception:** Table `task_history` hanya punya `created_by` dan `created_at` (immutable log).

## Response Encryption

Response data bisa di-enkripsi otomatis jika `ENCRYPTION_ENABLED=true`. Client perlu mendekripsi dengan key dan IV yang sesuai.

## Catatan Penting

1. **Clean Architecture**: Menggunakan 3-layer architecture (Presentation → Service → Repository)

2. **Immutable Audit Trail**: History adalah log yang tidak bisa diubah/dihapus

3. **Auto-Generated Fields**:
   - Task code auto-generated
   - Task duration auto-calculated
   - History auto-created on updates

4. **Auto-Joins**: Semua foreign key auto-joined dengan data terkait (nama user, nama project, dll)

5. **Cascade Delete**: Ketika task dihapus, semua data terkait (comments, history, labels, watchers) ikut terhapus

6. **Nested Resources**: Comments, history, labels, watchers hanya accessible via `/tasks/{tsk_id}/*`

7. **Duration in Hours**: Task duration dihitung dalam satuan **jam (hours)**

8. **File Upload** (Under Development): Fitur attachment sedang dalam pengembangan

## Kontribusi

Untuk kontribusi, silakan buat pull request atau hubungi maintainer.

## License

[Specify your license here]
