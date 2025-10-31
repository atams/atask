# ATASK - Technical API Documentation

## Deskripsi Sistem

ATASK (Atlas Task Management System) adalah aplikasi manajemen proyek dan tugas yang terintegrasi dengan ATAMS (Atlas Authentication & Management System). Sistem ini menyediakan REST API lengkap untuk mengelola proyek, task, komentar, attachment, riwayat perubahan, label, dan watcher.

**Target User:**

-   Project Manager: Mengelola proyek dan task
-   Developer/Team Member: Mengerjakan task, menambah komentar, upload file
-   Stakeholder: Melihat progress proyek

**Masalah yang diselesaikan:**

-   Tracking task dan progress proyek secara real-time
-   Kolaborasi tim dengan sistem komentar dan watcher
-   Audit trail lengkap untuk setiap perubahan task
-   Notifikasi otomatis untuk task yang akan dimulai

---

## Autentikasi & Otorisasi

### Sistem Autentikasi

-   **Metode**: JWT Bearer Token (dari Atlas SSO/ATAMS)
-   **Header Required**:
    ```
    Authorization: Bearer <token>
    ```
-   **Token Location**: HTTP Header
-   **Validasi**: Setiap request akan divalidasi oleh Atlas SSO untuk mendapatkan informasi user (user_id, username, role_level, dll)

**Cara Mendapatkan Token:**

1. User login melalui Atlas SSO
2. Atlas SSO mengembalikan JWT token
3. Token disimpan di client (localStorage/cookie)
4. Token dikirim di header setiap request ke ATASK API

### Role & Permission

Sistem menggunakan **role_level** untuk mengontrol akses:

-   **role_level >= 10 (User)**: Akses penuh ke semua endpoint

    -   Bisa membaca semua data
    -   Bisa membuat project, task, label, dll
    -   Bisa mengupdate/delete resource yang **mereka buat sendiri** (creator-only)

-   **role_level < 10**: Akses ditolak (403 Forbidden)

**Creator-Only Rule:**

-   Hanya user yang membuat resource (created_by == current_user_id) yang bisa mengupdate atau menghapus resource tersebut
-   Berlaku untuk: Project, Task, Label, Master Data (jika ada CUD)
-   Exception: Task Watcher dan Task Label bisa dihapus oleh siapa saja dengan role_level >= 10

---

## Fitur & Endpoint

### 1. Master Data (READ-ONLY)

Master data adalah data referensi yang digunakan untuk task status, priority, dan type. **Endpoint ini READ-ONLY** - tidak ada operasi Create, Update, atau Delete.

#### GET /api/v1/master-statuses

**Fungsi**: Mengambil semua master status yang tersedia (To Do, In Progress, In Review, Done, Cancelled, dll)

**Auth Required**: Ya (role_level >= 10)

**Query Parameters**:

-   `skip`: integer (default: 0) - Jumlah record yang diskip untuk pagination
-   `limit`: integer (default: 100, max: 1000) - Jumlah maksimal record yang dikembalikan

**Validasi Auth**:

-   Token harus valid
-   role_level minimal 10

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Master statuses retrieved successfully",
    "data": [
        {
            "ms_id": 1,
            "ms_name": "TODO",
            "ms_description": "Task belum dikerjakan",
            "ms_color": "#6B7280",
            "created_by": "1",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_by": null,
            "updated_at": null
        }
    ],
    "total": 5,
    "page": 1,
    "size": 100,
    "pages": 1
}
```

**Response Error**:

-   401: Token invalid atau tidak ada
-   403: role_level < 10

---

#### GET /api/v1/master-priorities

**Fungsi**: Mengambil semua master priority (Low, Medium, High, Critical)

**Auth Required**: Ya (role_level >= 10)

**Query Parameters**:

-   `skip`: integer (default: 0)
-   `limit`: integer (default: 100, max: 1000)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Master priorities retrieved successfully",
    "data": [
        {
            "mp_id": 1,
            "mp_name": "LOW",
            "mp_description": "Prioritas rendah",
            "mp_color": "#10B981",
            "created_by": "1",
            "created_at": "2024-01-15T10:00:00Z"
        }
    ],
    "total": 4,
    "page": 1,
    "size": 100,
    "pages": 1
}
```

---

#### GET /api/v1/master-task-types

**Fungsi**: Mengambil semua master task type (Task, Bug, Feature, Improvement, Research)

**Auth Required**: Ya (role_level >= 10)

**Query Parameters**:

-   `skip`: integer (default: 0)
-   `limit`: integer (default: 100, max: 1000)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Master task types retrieved successfully",
    "data": [
        {
            "mtt_id": 1,
            "mtt_name": "TASK",
            "mtt_code": "TASK",
            "mtt_description": "Tugas umum",
            "created_by": "1",
            "created_at": "2024-01-15T10:00:00Z"
        }
    ],
    "total": 5,
    "page": 1,
    "size": 100,
    "pages": 1
}
```

**Panduan Frontend:**

-   Fetch master data saat aplikasi pertama kali load
-   Simpan di global state (Redux/Zustand/Context)
-   Gunakan untuk dropdown, filter, dan display
-   Refresh hanya jika ada indikasi data berubah

---

### 2. Projects

#### POST /api/v1/projects

**Fungsi**: Membuat project baru

**Auth Required**: Ya (role_level >= 10)

**Request Body**:

```json
{
    "prj_code": "string (required) - Kode unik project",
    "prj_name": "string (required) - Nama project",
    "prj_description": "string (optional) - Deskripsi project",
    "prj_start_date": "date (optional) - Tanggal mulai (format: YYYY-MM-DD)",
    "prj_end_date": "date (optional) - Tanggal selesai (format: YYYY-MM-DD)",
    "prj_u_id": "integer (required) - User ID owner project",
    "prj_is_active": "boolean (optional, default: true) - Status aktif project"
}
```

**Validasi Auth**:

-   Token harus valid
-   role_level minimal 10

**Validasi Data**:

-   `prj_code` harus unik (belum ada di database)
-   `prj_name` tidak boleh kosong
-   `prj_u_id` harus valid user ID
-   `prj_end_date` harus >= `prj_start_date` (jika keduanya diisi)

**Response Success (201)**:

```json
{
    "success": true,
    "message": "Project created successfully",
    "data": {
        "prj_id": 1,
        "prj_code": "PROJ-001",
        "prj_name": "Website Redesign",
        "prj_description": "Redesign website perusahaan",
        "prj_start_date": "2025-01-15",
        "prj_end_date": "2025-06-30",
        "prj_u_id": 123,
        "prj_owner_name": "John Doe",
        "prj_is_active": true,
        "created_by": "123",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_by": null,
        "updated_at": null
    }
}
```

**Response Error**:

-   400: Validasi gagal (prj_code sudah ada, field required kosong)
-   401: Token invalid
-   403: role_level < 10
-   409: Conflict - prj_code sudah digunakan project lain

**Logika Khusus**:

-   `prj_owner_name` di-auto-join dari tabel users (pt_atams_indonesia.users)
-   `created_by` otomatis diisi dengan user_id yang login
-   `prj_id` di-generate otomatis oleh database

---

#### GET /api/v1/projects

**Fungsi**: Mengambil daftar semua project dengan pagination

**Auth Required**: Ya (role_level >= 10)

**Query Parameters**:

-   `skip`: integer (default: 0) - Pagination offset
-   `limit`: integer (default: 100, max: 1000) - Jumlah record per page

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Projects retrieved successfully",
    "data": [
        {
            "prj_id": 1,
            "prj_code": "PROJ-001",
            "prj_name": "Website Redesign",
            "prj_owner_name": "John Doe",
            "prj_is_active": true,
            "created_at": "2025-01-15T10:00:00Z"
        }
    ],
    "total": 50,
    "page": 1,
    "size": 100,
    "pages": 1
}
```

**Panduan Frontend**:

-   Implementasi infinite scroll atau pagination
-   Show loading state saat fetch data
-   Cache data untuk menghindari fetch berulang

---

#### GET /api/v1/projects/{prj_id}

**Fungsi**: Mengambil detail project berdasarkan ID

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `prj_id`: integer (required) - ID project

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Project retrieved successfully",
    "data": {
        "prj_id": 1,
        "prj_code": "PROJ-001",
        "prj_name": "Website Redesign",
        "prj_description": "Redesign website perusahaan dengan UI/UX modern",
        "prj_start_date": "2025-01-15",
        "prj_end_date": "2025-06-30",
        "prj_u_id": 123,
        "prj_owner_name": "John Doe",
        "prj_is_active": true,
        "created_by": "123",
        "created_at": "2025-01-15T10:00:00Z",
        "updated_by": null,
        "updated_at": null
    }
}
```

**Response Error**:

-   404: Project dengan ID tersebut tidak ditemukan

---

#### PUT /api/v1/projects/{prj_id}

**Fungsi**: Mengupdate project yang sudah ada

**Auth Required**: Ya (role_level >= 10, dan **hanya creator yang bisa update**)

**Path Parameters**:

-   `prj_id`: integer (required) - ID project

**Request Body** (semua field optional):

```json
{
    "prj_code": "string (optional)",
    "prj_name": "string (optional)",
    "prj_description": "string (optional)",
    "prj_start_date": "date (optional)",
    "prj_end_date": "date (optional)",
    "prj_u_id": "integer (optional)",
    "prj_is_active": "boolean (optional)"
}
```

**Validasi Auth**:

-   Token valid
-   role_level >= 10
-   **created_by project harus == current_user_id** (creator-only)

**Validasi Data**:

-   Jika `prj_code` diubah, harus tetap unik
-   `prj_end_date` >= `prj_start_date`

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Project updated successfully",
    "data": {
        // Project object lengkap setelah update
    }
}
```

**Response Error**:

-   403: Bukan creator project (created_by != current_user_id)
-   404: Project tidak ditemukan
-   409: prj_code baru sudah digunakan project lain

**Logika Khusus**:

-   Hanya field yang dikirim di request body yang akan diupdate
-   `updated_by` dan `updated_at` otomatis diupdate
-   Creator check dilakukan di service layer

**Panduan Frontend**:

-   Tampilkan tombol Edit hanya jika user adalah creator
-   Handle 403 error dengan message "Anda tidak memiliki izin"
-   Konfirmasi sebelum update

---

#### DELETE /api/v1/projects/{prj_id}

**Fungsi**: Menghapus project

**Auth Required**: Ya (role_level >= 10, dan **hanya creator**)

**Path Parameters**:

-   `prj_id`: integer (required)

**Validasi Auth**:

-   Token valid
-   role_level >= 10
-   created_by == current_user_id

**Response Success (204)**:
No content (empty response)

**Response Error**:

-   403: Bukan creator
-   404: Project tidak ditemukan

**Logika Khusus**:

-   Soft delete atau hard delete (tergantung implementasi repository)
-   Cascade delete: Task yang terkait dengan project juga ikut terhapus

**Panduan Frontend**:

-   Konfirmasi delete dengan modal
-   Tampilkan peringatan bahwa task di project juga akan terhapus
-   Redirect ke list projects setelah delete berhasil

---

#### GET /api/v1/projects/{prj_id}/statistics

**Fungsi**: Mengambil statistik project (jumlah task berdasarkan status, priority, type, dll)

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `prj_id`: integer (required)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Project statistics retrieved successfully",
    "data": {
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
}
```

**Panduan Frontend**:

-   Tampilkan dalam bentuk chart (pie chart, bar chart)
-   Gunakan untuk project dashboard
-   Refresh saat ada perubahan task

---

### 3. Tasks

#### POST /api/v1/tasks

**Fungsi**: Membuat task baru di dalam project

**Auth Required**: Ya (role_level >= 10)

**Request Body**:

```json
{
    "tsk_title": "string (required) - Judul task",
    "tsk_description": "string (optional) - Deskripsi lengkap task",
    "tsk_prj_id": "integer (required) - ID project tempat task dibuat",
    "tsk_ms_id": "integer (required) - ID master status",
    "tsk_mp_id": "integer (required) - ID master priority",
    "tsk_mtt_id": "integer (required) - ID master task type",
    "tsk_assignee_u_id": "integer (optional) - ID user yang ditugaskan",
    "tsk_reporter_u_id": "integer (required) - ID user yang membuat task",
    "tsk_start_date": "datetime (optional) - Tanggal mulai task (ISO 8601)",
    "tsk_parent_tsk_id": "integer (optional) - ID parent task (untuk sub-task)"
}
```

**PENTING - Field yang TIDAK boleh dikirim**:

-   `tsk_code`: **Auto-generated** oleh sistem (format: `{prj_id}/{type_code}/{number}`)
-   `tsk_due_date`: **Hanya assignee yang bisa set** (di endpoint update)
-   `tsk_duration`: **Auto-calculated** dari selisih due_date dan start_date (read-only)

**Validasi Data**:

-   `tsk_title` tidak boleh kosong
-   `tsk_prj_id` harus valid (project harus exist)
-   `tsk_ms_id`, `tsk_mp_id`, `tsk_mtt_id` harus valid
-   `tsk_assignee_u_id` harus valid user (jika diisi)
-   `tsk_reporter_u_id` harus valid user

**Response Success (201)**:

```json
{
    "success": true,
    "message": "Task created successfully",
    "data": {
        "tsk_id": 1,
        "tsk_code": "001/TASK/001",
        "tsk_title": "Design homepage mockup",
        "tsk_description": "Create high-fidelity mockup",
        "tsk_prj_id": 1,
        "tsk_project_name": "Website Redesign",
        "tsk_ms_id": 1,
        "tsk_status_name": "TODO",
        "tsk_mp_id": 3,
        "tsk_priority_name": "HIGH",
        "tsk_priority_color": "#FF9800",
        "tsk_mtt_id": 1,
        "tsk_type_name": "TASK",
        "tsk_assignee_u_id": 456,
        "tsk_assignee_name": "Jane Smith",
        "tsk_reporter_u_id": 123,
        "tsk_reporter_name": "John Doe",
        "tsk_start_date": "2025-01-20T09:00:00Z",
        "tsk_due_date": null,
        "tsk_duration": null,
        "tsk_parent_tsk_id": null,
        "tsk_thumbnail": null,
        "tsk_thumbnail_url": null,
        "created_by": "123",
        "created_at": "2025-01-20T08:00:00Z"
    }
}
```

**Logika Khusus**:

-   **Auto-generated tsk_code**: Format `{prj_id}/{mtt_code}/{nomor_urut}`
    -   Contoh: `001/TASK/001`, `001/BUG/002`, `002/FEATURE/001`
    -   Nomor urut increment per project dan per type
-   **Auto-join**: System otomatis join dengan tabel terkait untuk mendapatkan nama-nama
-   `tsk_due_date` dan `tsk_duration` default null saat create
-   `created_by` otomatis diisi dengan current_user_id

**Panduan Frontend**:

-   Form create task jangan include field `tsk_code`, `tsk_due_date`, `tsk_duration`
-   Dropdown assignee dari endpoint `/api/v1/users`
-   Dropdown status, priority, type dari master data
-   Validate required fields sebelum submit

---

#### GET /api/v1/tasks

**Fungsi**: Mengambil daftar semua task dengan pagination

**Auth Required**: Ya (role_level >= 10)

**Query Parameters**:

-   `skip`: integer (default: 0)
-   `limit`: integer (default: 100, max: 1000)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Tasks retrieved successfully",
    "data": [
        {
            "tsk_id": 1,
            "tsk_code": "001/TASK/001",
            "tsk_title": "Design homepage mockup",
            "tsk_project_name": "Website Redesign",
            "tsk_status_name": "TODO",
            "tsk_priority_name": "HIGH",
            "tsk_priority_color": "#FF9800",
            "tsk_assignee_name": "Jane Smith",
            "tsk_due_date": null,
            "created_at": "2025-01-20T08:00:00Z"
        }
    ],
    "total": 150,
    "page": 1,
    "size": 100,
    "pages": 2
}
```

**Panduan Frontend**:

-   Tampilkan dalam table atau card list
-   Implement sorting dan filtering di frontend (atau gunakan advanced search)
-   Color code berdasarkan priority_color
-   Badge untuk status

---

#### GET /api/v1/tasks/{tsk_id}

**Fungsi**: Mengambil detail task berdasarkan ID

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `tsk_id`: integer (required)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Task retrieved successfully",
    "data": {
        // Full task object dengan semua field dan joins
    }
}
```

**Response Error**:

-   404: Task tidak ditemukan

---

#### PUT /api/v1/tasks/{tsk_id}

**Fungsi**: Mengupdate task yang sudah ada

**Auth Required**: Ya (role_level >= 10, **creator-only**)

**Path Parameters**:

-   `tsk_id`: integer (required)

**Request Body** (semua field optional):

```json
{
    "tsk_title": "string (optional)",
    "tsk_description": "string (optional)",
    "tsk_prj_id": "integer (optional)",
    "tsk_ms_id": "integer (optional)",
    "tsk_mp_id": "integer (optional)",
    "tsk_mtt_id": "integer (optional)",
    "tsk_assignee_u_id": "integer (optional)",
    "tsk_reporter_u_id": "integer (optional)",
    "tsk_start_date": "datetime (optional)",
    "tsk_due_date": "datetime (optional)",
    "tsk_parent_tsk_id": "integer (optional)"
}
```

**Validasi Auth**:

-   Token valid
-   role_level >= 10
-   **created_by == current_user_id** ATAU **current_user adalah assignee untuk field tsk_due_date**

**Validasi Data**:

-   **tsk_due_date HANYA bisa diset/update oleh assignee** (tsk_assignee_u_id == current_user_id)
-   `tsk_due_date` harus >= `tsk_start_date`
-   `tsk_code` TIDAK bisa diupdate (auto-generated, immutable)
-   `tsk_duration` TIDAK bisa diupdate (auto-calculated)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Task updated successfully",
    "data": {
        // Updated task object
    }
}
```

**Response Error**:

-   400: Validasi gagal (due_date < start_date)
-   403: Bukan creator atau bukan assignee (untuk due_date)
-   404: Task tidak ditemukan

**Logika Khusus**:

-   **Auto-calculate duration**: Jika `tsk_start_date` dan `tsk_due_date` keduanya terisi, sistem otomatis calculate `tsk_duration` dalam **hours**
    -   Rumus: `(tsk_due_date - tsk_start_date) / 3600` detik
-   **Auto-track changes**: Setiap perubahan field tertentu akan otomatis dicatat di `task_history`:
    -   Field yang di-track: title, description, status, priority, assignee, due_date, start_date
    -   History immutable (tidak bisa diubah/dihapus)
-   **updated_by** dan **updated_at** otomatis diupdate

**Panduan Frontend**:

-   Tampilkan field `tsk_due_date` hanya untuk assignee
-   Disable field `tsk_due_date` untuk non-assignee
-   Show validation error jika due_date < start_date
-   Tampilkan `tsk_duration` sebagai read-only (dalam format jam atau hari)
-   Real-time update duration saat user ubah start_date atau due_date

---

#### DELETE /api/v1/tasks/{tsk_id}

**Fungsi**: Menghapus task

**Auth Required**: Ya (role_level >= 10, **creator-only**)

**Path Parameters**:

-   `tsk_id`: integer (required)

**Validasi Auth**:

-   created_by == current_user_id

**Response Success (204)**:
No content

**Response Error**:

-   403: Bukan creator
-   404: Task tidak ditemukan

**Logika Khusus**:

-   **Cascade delete**: Comments, attachments, history, labels, watchers yang terkait juga ikut terhapus

---

#### PATCH /api/v1/tasks/bulk-update-status

**Fungsi**: Update status untuk multiple tasks sekaligus

**Auth Required**: Ya (role_level >= 10)

**Request Body**:

```json
{
    "task_ids": [1, 2, 3, 5, 8],
    "ms_id": 4
}
```

**Validasi Data**:

-   `task_ids` tidak boleh kosong
-   `ms_id` harus valid master status ID
-   **Validasi**: User harus creator dari masing-masing task, atau update akan di-skip untuk task yang bukan miliknya

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Task statuses updated successfully",
    "data": {
        "updated_count": 3,
        "skipped_count": 2,
        "skipped_task_ids": [3, 8]
    }
}
```

**Logika Khusus**:

-   Batch update untuk efisiensi
-   Task yang gagal/tidak boleh diupdate akan di-skip (bukan error)
-   History tetap dicatat untuk setiap task yang berhasil diupdate

**Panduan Frontend**:

-   Tampilkan checkbox untuk multi-select tasks
-   Button "Update Status" muncul saat ada task yang dipilih
-   Show result: berapa yang berhasil, berapa yang di-skip
-   Refresh task list setelah update

---

#### POST /api/v1/tasks/search

**Fungsi**: Advanced search tasks dengan multiple filters

**Auth Required**: Ya (role_level >= 10)

**Request Body**:

```json
{
    "keyword": "string (optional) - Search di title dan description",
    "project_ids": [1, 2, 3],
    "status_ids": [1, 2],
    "priority_ids": [3, 4],
    "assignee_ids": [456, 789],
    "reporter_ids": [123],
    "type_ids": [1, 2],
    "date_from": "2025-01-01",
    "date_to": "2025-12-31",
    "skip": 0,
    "limit": 20
}
```

**Semua field optional** - kirim hanya filter yang ingin digunakan

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Tasks retrieved successfully",
    "data": [
        // Array of task objects
    ],
    "total": 15,
    "page": 1,
    "size": 20,
    "pages": 1
}
```

**Logika Khusus**:

-   Semua filter bersifat AND (semua kondisi harus terpenuhi)
-   `keyword` search menggunakan ILIKE (case-insensitive)
-   `date_from` dan `date_to` filter berdasarkan `tsk_start_date`
-   Empty filter = ambil semua tasks (seperti GET /tasks)

**Panduan Frontend**:

-   Implementasi advanced filter panel/modal
-   Multi-select untuk project, status, priority, assignee, type
-   Date range picker untuk date filter
-   Search input dengan debounce (300-500ms)
-   Show active filters sebagai chips/tags
-   Clear filters button

---

### 4. Task Comments

#### POST /api/v1/tasks/{tsk_id}/comments

**Fungsi**: Menambahkan komentar pada task (support threading/reply)

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `tsk_id`: integer (required) - ID task

**Request Body**:

```json
{
    "tc_comment": "string (required) - Isi komentar",
    "tc_parent_tc_id": "integer (optional) - ID parent comment untuk reply"
}
```

**Validasi Data**:

-   `tc_comment` tidak boleh kosong
-   `tc_parent_tc_id` harus valid comment ID (jika diisi)
-   Parent comment harus milik task yang sama

**Response Success (201)**:

```json
{
    "success": true,
    "message": "Comment created successfully",
    "data": {
        "tc_id": 1,
        "tc_tsk_id": 1,
        "tc_task_title": "Design homepage mockup",
        "tc_u_id": 123,
        "tc_user_name": "John Doe",
        "tc_user_email": "john@example.com",
        "tc_comment": "Looks great! Please add color scheme.",
        "tc_parent_tc_id": null,
        "created_by": "123",
        "created_at": "2025-01-20T10:00:00Z"
    }
}
```

**Logika Khusus**:

-   `tc_u_id` otomatis diisi dengan current_user_id
-   Auto-join dengan users table untuk nama dan email
-   Support nested comments (reply to reply)

**Panduan Frontend**:

-   Textarea untuk input comment
-   Button "Reply" untuk setiap comment
-   Tampilkan thread/indentation untuk replies
-   Show user avatar dan nama
-   Format timestamp dengan relative time (e.g., "2 hours ago")

---

#### GET /api/v1/tasks/{tsk_id}/comments

**Fungsi**: Mengambil semua komentar untuk task tertentu

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `tsk_id`: integer (required)

**Query Parameters**:

-   `skip`: integer (default: 0)
-   `limit`: integer (default: 100, max: 1000)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Comments retrieved successfully",
    "data": [
        {
            "tc_id": 1,
            "tc_comment": "Looks great!",
            "tc_user_name": "John Doe",
            "tc_parent_tc_id": null,
            "created_at": "2025-01-20T10:00:00Z"
        },
        {
            "tc_id": 2,
            "tc_comment": "Thanks!",
            "tc_user_name": "Jane Smith",
            "tc_parent_tc_id": 1,
            "created_at": "2025-01-20T10:30:00Z"
        }
    ],
    "total": 2,
    "page": 1,
    "size": 100,
    "pages": 1
}
```

**Panduan Frontend**:

-   Build comment tree structure di frontend
-   Group replies dengan parent comment
-   Implementasi "Load more replies"
-   Real-time update dengan polling atau websocket (optional)

---

### 5. Task Attachments

#### POST /api/v1/tasks/{tsk_id}/attachments

**Fungsi**: Upload multiple files ke task (bulk upload)

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `tsk_id`: integer (required)

**Request**:

-   Content-Type: `multipart/form-data`
-   Form field: `files` (array of files)

**Validasi Data**:

-   **Allowed file types**: PDF (.pdf), Images (.png, .jpg, .jpeg)
-   **Max file size**:
    -   Images: 5MB
    -   PDF: 10MB
-   Content-Type validation dijalankan

**Response Success (201)**:

```json
{
    "success": true,
    "message": "2 attachment(s) uploaded successfully",
    "data": [
        {
            "ta_id": 1,
            "ta_tsk_id": 1,
            "ta_file_name": "mockup.png",
            "ta_file_url": "https://res.cloudinary.com/xxx/image/upload/v123/atask/mockup.png",
            "ta_file_type": "image/png",
            "ta_file_size": 1048576,
            "ta_cloudinary_public_id": "atask/mockup_abc123",
            "created_by": "123",
            "created_at": "2025-01-20T11:00:00Z"
        },
        {
            "ta_id": 2,
            "ta_file_name": "requirements.pdf",
            "ta_file_url": "https://res.cloudinary.com/xxx/raw/upload/v123/atask/requirements.pdf",
            "ta_file_type": "application/pdf",
            "ta_file_size": 2097152
        }
    ]
}
```

**Response Error**:

-   400: File type tidak diizinkan atau file terlalu besar
-   404: Task tidak ditemukan

**Logika Khusus**:

-   Files diupload ke **Cloudinary**
-   `ta_cloudinary_public_id` disimpan untuk management file
-   `ta_file_url` adalah public URL dari Cloudinary
-   Support bulk upload (multiple files sekaligus)
-   File size dalam bytes

**Panduan Frontend**:

-   Implementasi drag-and-drop upload
-   Show file preview sebelum upload
-   Progress bar untuk upload
-   Validate file type dan size di frontend sebelum upload
-   Tampilkan uploaded files dengan download link
-   File size formatter (KB, MB)

---

#### GET /api/v1/tasks/{tsk_id}/attachments

**Fungsi**: Mengambil semua attachments untuk task

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `tsk_id`: integer (required)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Task attachments retrieved successfully",
    "data": {
        "attachments": [
            {
                "ta_id": 1,
                "ta_file_name": "mockup.png",
                "ta_file_url": "https://...",
                "ta_file_type": "image/png",
                "ta_file_size": 1048576,
                "created_at": "2025-01-20T11:00:00Z"
            }
        ],
        "total_size": 1048576
    }
}
```

**Panduan Frontend**:

-   Tampilkan sebagai file list dengan icon sesuai type
-   Show total size
-   Clickable file name untuk preview/download
-   Thumbnail untuk images

---

#### DELETE /api/v1/tasks/{tsk_id}/attachments/{ta_id}

**Fungsi**: Menghapus attachment dari task

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `tsk_id`: integer (required)
-   `ta_id`: integer (required)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Task attachment deleted successfully",
    "data": null
}
```

**Logika Khusus**:

-   File dihapus dari **database DAN Cloudinary**
-   Cascade delete (jika task dihapus, semua attachments juga ikut terhapus)

**Panduan Frontend**:

-   Konfirmasi sebelum delete
-   Show loading state
-   Remove dari list setelah delete berhasil

---

### 6. Task Thumbnail

#### POST /api/v1/tasks/{tsk_id}/thumbnail

**Fungsi**: Upload thumbnail image untuk task

**Auth Required**: Ya (role_level >= 10, **creator-only**)

**Path Parameters**:

-   `tsk_id`: integer (required)

**Request**:

-   Content-Type: `multipart/form-data`
-   Form field: `file` (single image file)

**Validasi Data**:

-   **Allowed file types**: Images only (.png, .jpg, .jpeg)
-   **Max file size**: 5MB

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Task thumbnail uploaded successfully",
    "data": {
        // Full task object dengan tsk_thumbnail dan tsk_thumbnail_url terisi
        "tsk_id": 1,
        "tsk_thumbnail": "atask/thumbnails/abc123",
        "tsk_thumbnail_url": "https://res.cloudinary.com/xxx/image/upload/v123/atask/thumbnails/abc123.jpg"
    }
}
```

**Logika Khusus**:

-   Jika task sudah punya thumbnail, thumbnail lama akan dihapus dari Cloudinary
-   `tsk_thumbnail` menyimpan Cloudinary public_id
-   `tsk_thumbnail_url` di-generate otomatis saat fetch task

**Panduan Frontend**:

-   Image upload dengan preview
-   Crop/resize image sebelum upload (optional)
-   Show existing thumbnail jika ada
-   Replace button untuk ganti thumbnail

---

#### DELETE /api/v1/tasks/{tsk_id}/thumbnail

**Fungsi**: Menghapus thumbnail dari task

**Auth Required**: Ya (role_level >= 10, **creator-only**)

**Path Parameters**:

-   `tsk_id`: integer (required)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Task thumbnail deleted successfully",
    "data": {
        // Task object dengan tsk_thumbnail dan tsk_thumbnail_url = null
    }
}
```

**Logika Khusus**:

-   File thumbnail dihapus dari Cloudinary
-   `tsk_thumbnail` dan `tsk_thumbnail_url` di-set null

---

### 7. Task History (Audit Log)

#### GET /api/v1/tasks/{tsk_id}/history

**Fungsi**: Melihat riwayat perubahan task (audit trail)

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `tsk_id`: integer (required)

**Query Parameters**:

-   `skip`: integer (default: 0)
-   `limit`: integer (default: 100, max: 1000)
-   `field_name`: string (optional) - Filter by field name (title, status, priority, assignee, due_date, start_date)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Task history retrieved successfully",
    "data": [
        {
            "th_id": 1,
            "th_tsk_id": 1,
            "th_task_title": "Design homepage mockup",
            "th_field_name": "status",
            "th_old_value": "TODO",
            "th_new_value": "IN_PROGRESS",
            "th_u_id": 123,
            "th_user_name": "John Doe",
            "created_by": "123",
            "created_at": "2025-01-20T14:00:00Z"
        }
    ],
    "total": 5,
    "page": 1,
    "size": 100,
    "pages": 1
}
```

**Logika Khusus**:

-   **History is immutable**: Tidak ada endpoint POST, PUT, DELETE untuk history
-   History **auto-created** saat task diupdate
-   **Tracked fields**: title, description, status, priority, assignee, due_date, start_date
-   History **tidak punya** `updated_by` dan `updated_at` (log tidak bisa diubah)

**Panduan Frontend**:

-   Tampilkan sebagai timeline/activity feed
-   Format: "John Doe changed status from TODO to IN_PROGRESS"
-   Filter by field name dengan dropdown
-   Group by date
-   Highlight changes (old value vs new value)

---

### 8. Task Labels

#### POST /api/v1/tasks/{tsk_id}/labels

**Fungsi**: Menambahkan label ke task

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `tsk_id`: integer (required)

**Request Body**:

```json
{
    "lbl_id": 1
}
```

**Validasi Data**:

-   `lbl_id` harus valid label ID
-   Label belum pernah di-assign ke task ini (unique constraint)

**Response Success (201)**:

```json
{
    "success": true,
    "message": "Label assigned to task successfully",
    "data": {
        "tl_id": 1,
        "tl_tsk_id": 1,
        "tl_task_title": "Design homepage mockup",
        "tl_lbl_id": 1,
        "tl_label_name": "frontend",
        "tl_label_color": "#3498db",
        "created_by": "123",
        "created_at": "2025-01-20T15:00:00Z"
    }
}
```

**Response Error**:

-   409: Label sudah di-assign ke task ini

**Panduan Frontend**:

-   Dropdown atau multi-select untuk pilih label
-   Show existing labels sebagai chips/tags dengan color
-   Prevent double-assign (hide label yang sudah di-assign)

---

#### GET /api/v1/tasks/{tsk_id}/labels

**Fungsi**: Mengambil semua labels yang di-assign ke task

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `tsk_id`: integer (required)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Task labels retrieved successfully",
    "data": {
        "labels": [
            {
                "tl_id": 1,
                "tl_lbl_id": 1,
                "tl_label_name": "frontend",
                "tl_label_color": "#3498db",
                "created_at": "2025-01-20T15:00:00Z"
            }
        ]
    }
}
```

**Panduan Frontend**:

-   Tampilkan sebagai colored badges/chips
-   Clickable untuk filter tasks by label

---

#### DELETE /api/v1/tasks/{tsk_id}/labels/{lbl_ids}

**Fungsi**: Menghapus satu atau multiple labels dari task (bulk delete)

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `tsk_id`: integer (required)
-   `lbl_ids`: string (required) - **Bisa comma-separated** (contoh: "1" atau "1,2,3")

**Response Success (204)**:
No content

**Logika Khusus**:

-   Support bulk delete dengan comma-separated IDs
-   Label yang tidak ditemukan akan di-skip (tidak error)

**Panduan Frontend**:

-   X button pada setiap label chip untuk remove
-   Multi-select untuk bulk remove
-   No confirmation needed (easy to re-add)

---

### 9. Task Watchers

#### POST /api/v1/tasks/{tsk_id}/watchers

**Fungsi**: Menambahkan watcher ke task (subscribe untuk notifikasi)

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `tsk_id`: integer (required)

**Request Body**:

```json
{
    "u_id": 789
}
```

**Validasi Data**:

-   `u_id` harus valid user ID
-   User belum pernah di-add sebagai watcher (unique constraint)

**Response Success (201)**:

```json
{
    "success": true,
    "message": "Watcher added to task successfully",
    "data": {
        "tw_id": 1,
        "tw_tsk_id": 1,
        "tw_task_title": "Design homepage mockup",
        "tw_u_id": 789,
        "tw_user_name": "Bob Wilson",
        "tw_user_email": "bob@example.com",
        "created_by": "123",
        "created_at": "2025-01-20T16:00:00Z"
    }
}
```

**Response Error**:

-   409: User sudah menjadi watcher task ini

**Panduan Frontend**:

-   User search/dropdown untuk add watcher
-   Show existing watchers dengan avatar
-   Button "Watch this task" untuk add diri sendiri

---

#### GET /api/v1/tasks/{tsk_id}/watchers

**Fungsi**: Mengambil semua watchers untuk task

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `tsk_id`: integer (required)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Watchers retrieved successfully",
    "data": {
        "watchers": [
            {
                "tw_id": 1,
                "tw_u_id": 789,
                "tw_user_name": "Bob Wilson",
                "tw_user_email": "bob@example.com",
                "created_at": "2025-01-20T16:00:00Z"
            }
        ]
    }
}
```

**Panduan Frontend**:

-   Tampilkan sebagai avatar list
-   Hover untuk show nama
-   Show count (e.g., "3 watchers")

---

#### DELETE /api/v1/tasks/{tsk_id}/watchers/{u_ids}

**Fungsi**: Menghapus satu atau multiple watchers dari task (bulk delete)

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `tsk_id`: integer (required)
-   `u_ids`: string (required) - **Bisa comma-separated** (contoh: "2" atau "2,3,4")

**Response Success (204)**:
No content

**Logika Khusus**:

-   Support bulk delete
-   User yang tidak ditemukan di-skip

**Panduan Frontend**:

-   X button untuk remove watcher
-   Button "Unwatch" untuk remove diri sendiri

---

### 10. Labels

#### POST /api/v1/labels

**Fungsi**: Membuat label baru

**Auth Required**: Ya (role_level >= 10)

**Request Body**:

```json
{
    "lbl_name": "string (required) - Nama label",
    "lbl_color": "string (required) - Hex color code (e.g., #3498db)",
    "lbl_description": "string (optional) - Deskripsi label"
}
```

**Validasi Data**:

-   `lbl_name` tidak boleh kosong dan harus unique
-   `lbl_color` harus format hex color valid

**Response Success (201)**:

```json
{
    "success": true,
    "message": "Label created successfully",
    "data": {
        "lbl_id": 1,
        "lbl_name": "frontend",
        "lbl_color": "#3498db",
        "lbl_description": "Frontend related tasks",
        "created_by": "123",
        "created_at": "2025-01-20T17:00:00Z"
    }
}
```

**Panduan Frontend**:

-   Color picker untuk select color
-   Preview label dengan color
-   Suggest popular colors

---

#### GET /api/v1/labels

**Fungsi**: Mengambil semua labels

**Auth Required**: Ya (role_level >= 10)

**Query Parameters**:

-   `skip`: integer (default: 0)
-   `limit`: integer (default: 100, max: 1000)
-   `search`: string (optional) - Search by label name

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Labels retrieved successfully",
    "data": [
        {
            "lbl_id": 1,
            "lbl_name": "frontend",
            "lbl_color": "#3498db",
            "created_at": "2025-01-20T17:00:00Z"
        }
    ],
    "total": 10,
    "page": 1,
    "size": 100,
    "pages": 1
}
```

---

#### GET /api/v1/labels/{lbl_id}

**Fungsi**: Mengambil detail label berdasarkan ID

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `lbl_id`: integer (required)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Label retrieved successfully",
    "data": {
        // Full label object
    }
}
```

---

#### PUT /api/v1/labels/{lbl_id}

**Fungsi**: Update label

**Auth Required**: Ya (role_level >= 10, **creator-only**)

**Path Parameters**:

-   `lbl_id`: integer (required)

**Request Body** (semua optional):

```json
{
    "lbl_name": "string (optional)",
    "lbl_color": "string (optional)",
    "lbl_description": "string (optional)"
}
```

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Label updated successfully",
    "data": {
        // Updated label object
    }
}
```

---

#### DELETE /api/v1/labels/{lbl_id}

**Fungsi**: Menghapus label

**Auth Required**: Ya (role_level >= 10, **creator-only**)

**Path Parameters**:

-   `lbl_id`: integer (required)

**Response Success (204)**:
No content

**Logika Khusus**:

-   Cascade delete: Task labels yang menggunakan label ini juga ikut terhapus

---

### 11. Users

#### GET /api/v1/users

**Fungsi**: Mengambil daftar users dari Atlas SSO

**Auth Required**: Ya (role_level >= 10)

**Query Parameters**:

-   `skip`: integer (default: 0)
-   `limit`: integer (default: 100, max: 1000)
-   `search`: string (optional) - Search by username, email, or full name

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Users retrieved successfully",
    "data": [
        {
            "u_id": 123,
            "u_username": "johndoe",
            "u_email": "john@example.com",
            "u_full_name": "John Doe",
            "u_is_active": true
        }
    ],
    "total": 50,
    "page": 1,
    "size": 100,
    "pages": 1
}
```

**Logika Khusus**:

-   Data diambil dari tabel `pt_atams_indonesia.users` (ATAMS database)
-   Cross-schema query

**Panduan Frontend**:

-   Gunakan untuk dropdown assignee, reporter, watcher
-   Implementasi search dengan debounce
-   Cache user data untuk performa

---

#### GET /api/v1/users/{u_id}/dashboard

**Fungsi**: Mengambil dashboard user dengan statistik task

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `u_id`: integer (required)

**Response Success (200)**:

```json
{
    "success": true,
    "message": "User dashboard retrieved successfully",
    "data": {
        "u_id": 123,
        "u_full_name": "John Doe",
        "statistics": {
            "assigned_tasks": {
                "total": 15,
                "by_status": {
                    "TODO": 5,
                    "IN_PROGRESS": 7,
                    "DONE": 3
                }
            },
            "reported_tasks": {
                "total": 25,
                "by_status": {
                    "TODO": 8,
                    "IN_PROGRESS": 10,
                    "DONE": 7
                }
            },
            "watched_tasks": {
                "total": 10
            }
        },
        "recent_activities": [
            {
                "activity_type": "task_updated",
                "task_id": 1,
                "task_title": "Design homepage",
                "field_changed": "status",
                "timestamp": "2025-01-20T18:00:00Z"
            }
        ]
    }
}
```

**Panduan Frontend**:

-   Tampilkan di user profile page
-   Chart untuk visualisasi statistik
-   Activity feed untuk recent activities

---

#### GET /api/v1/users/{u_id}/watched-tasks

**Fungsi**: Mengambil semua tasks yang di-watch oleh user

**Auth Required**: Ya (role_level >= 10)

**Path Parameters**:

-   `u_id`: integer (required)

**Query Parameters**:

-   `skip`: integer (default: 0)
-   `limit`: integer (default: 100, max: 1000)
-   `status_id`: integer (optional) - Filter by status

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Watched tasks retrieved successfully",
    "data": [
        {
            // Task objects yang di-watch user
        }
    ],
    "total": 10,
    "page": 1,
    "size": 100,
    "pages": 1
}
```

**Panduan Frontend**:

-   Tampilkan di "My Watched Tasks" page
-   Filter by status
-   Button "Unwatch" untuk setiap task

---

### 12. Notifications

#### POST /api/v1/notifications/send-daily-reminders

**Fungsi**: Mengirim email reminder harian untuk tasks yang akan dimulai hari ini (endpoint untuk scheduled job)

**Auth Required**: Tidak (menggunakan CRON_API_KEY di header)

**Headers**:

```
X-Api-Key: <CRON_API_KEY>
```

**Validasi Auth**:

-   `X-Api-Key` header harus match dengan `CRON_API_KEY` di environment variable
-   Jika tidak match atau kosong: 403 Forbidden

**Response Success (200)**:

```json
{
    "success": true,
    "message": "Daily reminders processed: 10 sent, 0 failed",
    "data": {
        "total_tasks": 10,
        "emails_sent": 10,
        "emails_failed": 0,
        "success_rate": 100.0,
        "failed_tasks": []
    }
}
```

**Logika Khusus**:

-   Dijadwalkan via GitHub Actions setiap hari jam 9 pagi
-   Mencari tasks dengan `tsk_start_date = today`
-   Task harus punya assignee (`tsk_assignee_u_id NOT NULL`)
-   Kirim HTML email ke assignee dengan detail task
-   Email template berisi:
    -   Task code & title
    -   Project name
    -   Status, Priority, Type
    -   Reporter name
    -   Start date
    -   Task description

**Panduan Frontend**:

-   Endpoint ini untuk backend automation, tidak digunakan di frontend
-   User menerima email reminder secara otomatis

---

#### GET /api/v1/notifications/health

**Fungsi**: Health check untuk notification service

**Auth Required**: Tidak (public endpoint untuk monitoring)

**Response Success (200)**:

```json
{
    "status": "ok",
    "email_configured": true,
    "cron_api_key_configured": true
}
```

**Panduan Frontend**:

-   Bisa digunakan untuk status page/monitoring dashboard
-   Show alert jika service not configured

---

## Flow Aplikasi

### 1. Flow Login & Authentication

```
[User buka aplikasi]
  ↓
[Check localStorage untuk token]
  ↓
If token exists dan valid:
  → Decode token untuk user info
  → Set user state (user_id, username, role_level)
  → Redirect ke dashboard

If token tidak ada atau expired:
  → Redirect ke Atlas SSO login page
  → User login di Atlas SSO
  → Atlas SSO redirect kembali dengan token
  → Simpan token di localStorage
  → Set user state
  → Redirect ke dashboard
```

**Implementasi Tips**:

-   Gunakan axios interceptor untuk auto-attach token ke setiap request
-   Handle 401 error secara global (redirect ke login)
-   Refresh token jika mendekati expiry

---

### 2. Flow Create Task

```
[User klik "Create Task" button]
  ↓
[Tampilkan form modal/page]
  ↓
[User isi form]
  - Pilih Project (dropdown dari GET /projects)
  - Isi Title (required)
  - Isi Description (optional)
  - Pilih Status (dropdown dari master-statuses)
  - Pilih Priority (dropdown dari master-priorities)
  - Pilih Type (dropdown dari master-task-types)
  - Pilih Assignee (dropdown dari GET /users)
  - Set Reporter (default: current user)
  - Set Start Date (date picker)
  ↓
[User klik Submit]
  ↓
[Frontend validation]
  - Check required fields
  - Validate date format
  ↓
If validation fails:
  → Show error messages
  → User fix errors

If validation success:
  → POST /api/v1/tasks
  → Show loading state
  ↓
If API success (201):
  → Close modal
  → Refresh task list
  → Show success toast
  → Optional: Navigate to task detail

If API error:
  → Show error message
  → Keep form data
  → User bisa retry
```

---

### 3. Flow Update Task Status (dengan bulk update)

```
[User di task list page]
  ↓
[User pilih multiple tasks dengan checkbox]
  ↓
[Button "Update Status" muncul]
  ↓
[User klik button]
  ↓
[Tampilkan status picker modal]
  ↓
[User pilih status baru]
  ↓
[User klik Confirm]
  ↓
[PATCH /api/v1/tasks/bulk-update-status]
  Request: {
    task_ids: [1, 2, 3],
    ms_id: 2
  }
  ↓
If success (200):
  → Response berisi updated_count dan skipped_count
  → Refresh task list
  → Show toast: "3 tasks updated, 1 skipped (not creator)"
  → Clear checkbox selection

If error:
  → Show error message
  → Keep selection
```

---

### 4. Flow Upload Attachment

```
[User di task detail page]
  ↓
[User klik "Upload" button atau drag files]
  ↓
[File picker terbuka / Drop files]
  ↓
[User pilih multiple files]
  ↓
[Frontend validation]
  - Check file type (PDF, PNG, JPG, JPEG)
  - Check file size (max 5MB untuk image, 10MB untuk PDF)
  ↓
If validation fails:
  → Show error: "Invalid file type" atau "File too large"
  → User hapus file invalid

If validation success:
  → Show file preview dengan progress bar
  → POST /api/v1/tasks/{tsk_id}/attachments
  → Upload files (form-data dengan multiple files)
  ↓
During upload:
  → Show progress bar per file
  → Disable upload button

If upload success (201):
  → Hide progress
  → Add files ke attachment list
  → Show success toast
  → Files sekarang clickable untuk download

If upload error:
  → Show error per file
  → Allow retry untuk failed files
```

---

### 5. Flow Comment & Reply

```
[User di task detail page]
  ↓
[User scroll ke comments section]
  ↓
Scenario A: Post new comment
  [User ketik di comment box]
  ↓
  [User klik "Post Comment"]
  ↓
  [POST /api/v1/tasks/{tsk_id}/comments]
    Body: {
      tc_comment: "user input",
      tc_parent_tc_id: null
    }
  ↓
  If success (201):
    → Add comment ke list (top atau bottom)
    → Clear input box
    → Show success feedback

Scenario B: Reply to comment
  [User klik "Reply" button pada comment]
  ↓
  [Reply box muncul di bawah comment]
  ↓
  [User ketik reply]
  ↓
  [User klik "Post Reply"]
  ↓
  [POST /api/v1/tasks/{tsk_id}/comments]
    Body: {
      tc_comment: "user reply",
      tc_parent_tc_id: <parent_comment_id>
    }
  ↓
  If success (201):
    → Add reply di bawah parent comment (indented)
    → Close reply box
    → Show success feedback
```

---

### 6. Flow Advanced Search

```
[User di tasks page]
  ↓
[User klik "Advanced Search" button]
  ↓
[Modal/Panel filter terbuka]
  ↓
[User set filters]
  - Ketik keyword (debounced 500ms)
  - Pilih projects (multi-select)
  - Pilih statuses (multi-select)
  - Pilih priorities (multi-select)
  - Pilih assignees (multi-select)
  - Set date range (date picker)
  ↓
[User klik "Apply Filters"]
  ↓
[POST /api/v1/tasks/search]
  Body: {
    keyword: "design",
    project_ids: [1, 2],
    status_ids: [1, 2],
    priority_ids: [3, 4],
    assignee_ids: [456],
    date_from: "2025-01-01",
    date_to: "2025-12-31",
    skip: 0,
    limit: 20
  }
  ↓
If success (200):
  → Replace task list dengan search results
  → Show active filters sebagai chips/tags
  → Show result count
  → Enable "Clear Filters" button

If no results:
  → Show empty state: "No tasks found"
  → Suggest to adjust filters

[User klik chip X untuk remove filter]
  ↓
  → Remove filter dari request
  → Re-run search

[User klik "Clear Filters"]
  ↓
  → Clear semua filters
  → Fetch GET /api/v1/tasks (default list)
```

---

### 7. Flow Project Statistics Dashboard

```
[User navigate ke project detail]
  ↓
[GET /api/v1/projects/{prj_id}]
  → Fetch project info
  ↓
[GET /api/v1/projects/{prj_id}/statistics]
  → Fetch statistics
  ↓
If success:
  → Render project header (name, code, dates, owner)
  → Render statistics section:
    * Total tasks card
    * Pie chart: tasks by status
    * Bar chart: tasks by priority
    * Donut chart: tasks by type
    * Overdue tasks warning badge
    * Completion rate progress bar
    * Average completion time metric
  ↓
[User klik status pada chart]
  ↓
  → Filter tasks by selected status
  → Navigate ke tasks page dengan pre-filter

[User klik "View Tasks"]
  ↓
  → Navigate ke tasks page dengan project_id filter
```

---

## Data Models / Schema

### Project

```json
{
    "prj_id": "integer - Primary key, auto-increment",
    "prj_code": "string - Unique project code (e.g., PROJ-001)",
    "prj_name": "string - Project name",
    "prj_description": "string - Project description",
    "prj_start_date": "date - Project start date (YYYY-MM-DD)",
    "prj_end_date": "date - Project end date (YYYY-MM-DD)",
    "prj_u_id": "integer - Owner user ID (FK to users)",
    "prj_owner_name": "string - Owner full name (auto-joined from users)",
    "prj_is_active": "boolean - Active status",
    "created_by": "string - User ID who created",
    "created_at": "datetime - Creation timestamp",
    "updated_by": "string - User ID who last updated",
    "updated_at": "datetime - Last update timestamp"
}
```

**Relationships**:

-   `prj_u_id` → `pt_atams_indonesia.users.u_id` (one-to-one)
-   `prj_id` → `tasks.tsk_prj_id` (one-to-many)

**Validations**:

-   `prj_code` must be unique
-   `prj_name` cannot be empty
-   `prj_end_date` >= `prj_start_date` (if both filled)

---

### Task

```json
{
    "tsk_id": "integer - Primary key, auto-increment",
    "tsk_code": "string - Auto-generated task code (e.g., 001/TASK/001)",
    "tsk_title": "string - Task title",
    "tsk_description": "string - Task description",
    "tsk_prj_id": "integer - Project ID (FK to projects)",
    "tsk_ms_id": "integer - Status ID (FK to master_status)",
    "tsk_mp_id": "integer - Priority ID (FK to master_priority)",
    "tsk_mtt_id": "integer - Task type ID (FK to master_task_type)",
    "tsk_assignee_u_id": "integer - Assignee user ID (FK to users)",
    "tsk_reporter_u_id": "integer - Reporter user ID (FK to users)",
    "tsk_start_date": "datetime - Start date and time",
    "tsk_due_date": "datetime - Due date and time (only assignee can set)",
    "tsk_duration": "decimal - Duration in hours (auto-calculated, read-only)",
    "tsk_parent_tsk_id": "integer - Parent task ID for sub-tasks",
    "tsk_thumbnail": "string - Cloudinary public_id for thumbnail",
    "tsk_thumbnail_url": "string - Public URL for thumbnail (auto-generated)",
    "tsk_project_name": "string - Project name (auto-joined)",
    "tsk_status_name": "string - Status name (auto-joined)",
    "tsk_priority_name": "string - Priority name (auto-joined)",
    "tsk_priority_color": "string - Priority color (auto-joined)",
    "tsk_type_name": "string - Task type name (auto-joined)",
    "tsk_assignee_name": "string - Assignee full name (auto-joined)",
    "tsk_reporter_name": "string - Reporter full name (auto-joined)",
    "created_by": "string - User ID who created",
    "created_at": "datetime - Creation timestamp",
    "updated_by": "string - User ID who last updated",
    "updated_at": "datetime - Last update timestamp"
}
```

**Relationships**:

-   `tsk_prj_id` → `projects.prj_id`
-   `tsk_ms_id` → `master_status.ms_id`
-   `tsk_mp_id` → `master_priority.mp_id`
-   `tsk_mtt_id` → `master_task_type.mtt_id`
-   `tsk_assignee_u_id` → `users.u_id`
-   `tsk_reporter_u_id` → `users.u_id`
-   `tsk_parent_tsk_id` → `tasks.tsk_id` (self-referencing)
-   `tsk_id` → `task_comments.tc_tsk_id` (one-to-many)
-   `tsk_id` → `task_attachments.ta_tsk_id` (one-to-many)
-   `tsk_id` → `task_history.th_tsk_id` (one-to-many)
-   `tsk_id` → `task_labels.tl_tsk_id` (one-to-many)
-   `tsk_id` → `task_watchers.tw_tsk_id` (one-to-many)

**Validations**:

-   `tsk_code` is auto-generated and immutable
-   `tsk_title` cannot be empty
-   `tsk_due_date` >= `tsk_start_date` (if both filled)
-   `tsk_due_date` can only be set by assignee
-   `tsk_duration` is auto-calculated: `(tsk_due_date - tsk_start_date) in hours`

---

### TaskComment

```json
{
    "tc_id": "integer - Primary key",
    "tc_tsk_id": "integer - Task ID (FK to tasks)",
    "tc_u_id": "integer - User ID who commented (FK to users)",
    "tc_comment": "string - Comment text",
    "tc_parent_tc_id": "integer - Parent comment ID for replies (FK to task_comments)",
    "tc_task_title": "string - Task title (auto-joined)",
    "tc_user_name": "string - User full name (auto-joined)",
    "tc_user_email": "string - User email (auto-joined)",
    "created_by": "string",
    "created_at": "datetime",
    "updated_by": "string",
    "updated_at": "datetime"
}
```

**Relationships**:

-   `tc_tsk_id` → `tasks.tsk_id`
-   `tc_u_id` → `users.u_id`
-   `tc_parent_tc_id` → `task_comments.tc_id` (self-referencing)

---

### TaskAttachment

```json
{
    "ta_id": "integer - Primary key",
    "ta_tsk_id": "integer - Task ID (FK to tasks)",
    "ta_file_name": "string - Original file name",
    "ta_file_url": "string - Cloudinary public URL",
    "ta_file_type": "string - MIME type (e.g., image/png, application/pdf)",
    "ta_file_size": "integer - File size in bytes",
    "ta_cloudinary_public_id": "string - Cloudinary public_id for management",
    "created_by": "string",
    "created_at": "datetime"
}
```

**Validations**:

-   Allowed types: `image/png`, `image/jpeg`, `image/jpg`, `application/pdf`
-   Max size: 5MB for images, 10MB for PDF

---

### TaskHistory (Audit Log)

```json
{
    "th_id": "integer - Primary key",
    "th_tsk_id": "integer - Task ID (FK to tasks)",
    "th_field_name": "string - Field name that changed (title, description, status, priority, assignee, due_date, start_date)",
    "th_old_value": "string - Old value",
    "th_new_value": "string - New value",
    "th_u_id": "integer - User ID who made the change",
    "th_task_title": "string - Task title (auto-joined)",
    "th_user_name": "string - User full name (auto-joined)",
    "created_by": "string",
    "created_at": "datetime"
}
```

**Important**:

-   History **does NOT have** `updated_by` and `updated_at` (immutable log)
-   History is **auto-created** on task update
-   NO POST/PUT/DELETE endpoints (read-only via GET)

---

### TaskLabel

```json
{
    "tl_id": "integer - Primary key",
    "tl_tsk_id": "integer - Task ID (FK to tasks)",
    "tl_lbl_id": "integer - Label ID (FK to labels)",
    "tl_task_title": "string - Task title (auto-joined)",
    "tl_label_name": "string - Label name (auto-joined)",
    "tl_label_color": "string - Label color (auto-joined)",
    "created_by": "string",
    "created_at": "datetime"
}
```

**Validations**:

-   Unique constraint: `(tl_tsk_id, tl_lbl_id)` - Satu task tidak bisa punya label yang sama dua kali

---

### TaskWatcher

```json
{
    "tw_id": "integer - Primary key",
    "tw_tsk_id": "integer - Task ID (FK to tasks)",
    "tw_u_id": "integer - User ID (FK to users)",
    "tw_task_title": "string - Task title (auto-joined)",
    "tw_user_name": "string - User full name (auto-joined)",
    "tw_user_email": "string - User email (auto-joined)",
    "created_by": "string",
    "created_at": "datetime"
}
```

**Validations**:

-   Unique constraint: `(tw_tsk_id, tw_u_id)` - Satu user tidak bisa watch task yang sama dua kali

---

### Label

```json
{
    "lbl_id": "integer - Primary key",
    "lbl_name": "string - Label name (unique)",
    "lbl_color": "string - Hex color code (e.g., #3498db)",
    "lbl_description": "string - Label description",
    "created_by": "string",
    "created_at": "datetime",
    "updated_by": "string",
    "updated_at": "datetime"
}
```

**Validations**:

-   `lbl_name` must be unique
-   `lbl_color` must be valid hex color

---

### Master Status

```json
{
    "ms_id": "integer - Primary key",
    "ms_name": "string - Status name (e.g., TODO, IN_PROGRESS, DONE)",
    "ms_description": "string - Status description",
    "ms_color": "string - Hex color code",
    "created_by": "string",
    "created_at": "datetime"
}
```

---

### Master Priority

```json
{
    "mp_id": "integer - Primary key",
    "mp_name": "string - Priority name (e.g., LOW, MEDIUM, HIGH, CRITICAL)",
    "mp_description": "string - Priority description",
    "mp_color": "string - Hex color code",
    "created_by": "string",
    "created_at": "datetime"
}
```

---

### Master Task Type

```json
{
    "mtt_id": "integer - Primary key",
    "mtt_name": "string - Task type name (e.g., TASK, BUG, FEATURE)",
    "mtt_code": "string - Task type code (used in tsk_code generation)",
    "mtt_description": "string - Task type description",
    "created_by": "string",
    "created_at": "datetime"
}
```

---

## Response Format Standar

### Success Response (dengan data tunggal)

```json
{
    "success": true,
    "message": "Operation successful",
    "data": {
        // Single object
    }
}
```

### Success Response (dengan array data - pagination)

```json
{
    "success": true,
    "message": "Data retrieved successfully",
    "data": [
        // Array of objects
    ],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
}
```

### Error Response

```json
{
    "success": false,
    "message": "Error message yang jelas dan deskriptif",
    "details": {
        // Optional: Detail error tambahan
    }
}
```

### Validation Error Response

```json
{
    "success": false,
    "message": "Validation failed",
    "details": {
        "field": "prj_code",
        "value": "PROJ-001",
        "error": "Project with code 'PROJ-001' already exists"
    }
}
```

---

## HTTP Status Codes

-   **200 OK**: Request berhasil, data dikembalikan
-   **201 Created**: Resource berhasil dibuat (POST)
-   **204 No Content**: Request berhasil, tidak ada data yang dikembalikan (DELETE)
-   **400 Bad Request**: Validasi gagal, data tidak valid, atau business rule violated
-   **401 Unauthorized**: Token tidak valid, expired, atau tidak ada
-   **403 Forbidden**: User tidak punya permission (role_level < 10 atau bukan creator)
-   **404 Not Found**: Resource dengan ID tersebut tidak ditemukan
-   **409 Conflict**: Conflict seperti unique constraint violation (e.g., prj_code sudah ada)
-   **422 Unprocessable Entity**: Request format valid tapi tidak bisa diproses
-   **500 Internal Server Error**: Server error (tidak seharusnya terjadi, report ke backend team)

---

## Panduan untuk AI Frontend Developer

### 1. Autentikasi

**Setup:**

```javascript
// axios-instance.js
import axios from 'axios';

const api = axios.create({
    baseURL: 'https://your-api-url.com/api/v1',
    timeout: 10000,
});

// Interceptor untuk attach token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Interceptor untuk handle error
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Token invalid/expired
            localStorage.removeItem('auth_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default api;
```

**Login Flow:**

```javascript
// Setelah user login di Atlas SSO dan redirect kembali
const handleAuthCallback = (token) => {
    localStorage.setItem('auth_token', token);

    // Decode token untuk get user info (optional, tergantung token format)
    // const user = jwt_decode(token);
    // setUser(user);

    navigate('/dashboard');
};

// Logout
const handleLogout = () => {
    localStorage.removeItem('auth_token');
    navigate('/login');
};
```

---

### 2. Form Handling

**Best Practices:**

```javascript
// Example: Create Task Form
import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';

function CreateTaskForm() {
    const [formData, setFormData] = useState({
        tsk_title: '',
        tsk_description: '',
        tsk_prj_id: null,
        tsk_ms_id: null,
        tsk_mp_id: null,
        tsk_mtt_id: null,
        tsk_assignee_u_id: null,
        tsk_reporter_u_id: currentUser.u_id,
        tsk_start_date: null,
    });

    const [errors, setErrors] = useState({});

    // Fetch master data untuk dropdowns
    const { data: projects } = useQuery(['projects'], () =>
        api.get('/projects')
    );
    const { data: statuses } = useQuery(['statuses'], () =>
        api.get('/master-statuses')
    );
    const { data: priorities } = useQuery(['priorities'], () =>
        api.get('/master-priorities')
    );
    const { data: types } = useQuery(['types'], () =>
        api.get('/master-task-types')
    );
    const { data: users } = useQuery(['users'], () => api.get('/users'));

    // Mutation untuk create task
    const createTaskMutation = useMutation((data) => api.post('/tasks', data), {
        onSuccess: (response) => {
            toast.success('Task created successfully');
            queryClient.invalidateQueries(['tasks']);
            onClose();
        },
        onError: (error) => {
            const message =
                error.response?.data?.message || 'Failed to create task';
            toast.error(message);

            // Handle validation errors
            if (error.response?.data?.details) {
                setErrors({
                    [error.response.data.details.field]:
                        error.response.data.details.error,
                });
            }
        },
    });

    const handleSubmit = (e) => {
        e.preventDefault();

        // Frontend validation
        const newErrors = {};
        if (!formData.tsk_title) newErrors.tsk_title = 'Title is required';
        if (!formData.tsk_prj_id) newErrors.tsk_prj_id = 'Project is required';
        // ... other validations

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }

        // Submit
        createTaskMutation.mutate(formData);
    };

    return <form onSubmit={handleSubmit}>{/* Form fields */}</form>;
}
```

---

### 3. State Management

**Recommended: Zustand (simple & lightweight)**

```javascript
// stores/authStore.js
import create from 'zustand';

export const useAuthStore = create((set) => ({
    user: null,
    token: localStorage.getItem('auth_token'),
    setUser: (user) => set({ user }),
    setToken: (token) => {
        localStorage.setItem('auth_token', token);
        set({ token });
    },
    logout: () => {
        localStorage.removeItem('auth_token');
        set({ user: null, token: null });
    },
}));

// stores/masterDataStore.js
import create from 'zustand';

export const useMasterDataStore = create((set) => ({
    statuses: [],
    priorities: [],
    types: [],
    setStatuses: (statuses) => set({ statuses }),
    setPriorities: (priorities) => set({ priorities }),
    setTypes: (types) => set({ types }),
}));

// Usage in component
const { statuses, priorities } = useMasterDataStore();
```

**Alternative: React Query untuk data fetching + Context untuk auth**

```javascript
// contexts/AuthContext.js
import { createContext, useContext, useState } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('auth_token'));

    // ... auth methods

    return (
        <AuthContext.Provider value={{ user, token, setUser, setToken }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
```

---

### 4. UI/UX Guidelines

**Loading States:**

```javascript
// Button with loading
<button disabled={isLoading}>
    {isLoading ? (
        <>
            <Spinner size="sm" />
            <span>Loading...</span>
        </>
    ) : (
        'Submit'
    )}
</button>;

// Page loading
{
    isLoading && <LoadingSpinner />;
}
{
    isError && <ErrorMessage error={error} />;
}
{
    data && <TaskList tasks={data} />;
}
```

**Error States:**

```javascript
// Toast notifications (recommended: react-hot-toast)
import toast from 'react-hot-toast';

// Success
toast.success('Task created successfully');

// Error
toast.error(error.response?.data?.message || 'Something went wrong');

// Custom error component
function ErrorBoundary({ error, resetErrorBoundary }) {
    return (
        <div className="error-container">
            <h2>Oops! Something went wrong</h2>
            <p>{error.message}</p>
            <button onClick={resetErrorBoundary}>Try again</button>
        </div>
    );
}
```

**Empty States:**

```javascript
function TaskList({ tasks }) {
    if (tasks.length === 0) {
        return (
            <div className="empty-state">
                <EmptyIcon />
                <h3>No tasks found</h3>
                <p>Create your first task to get started</p>
                <button onClick={onCreateTask}>Create Task</button>
            </div>
        );
    }

    return <div>{/* Task list */}</div>;
}
```

**Success Feedback:**

```javascript
// Toast untuk quick actions
toast.success('Task status updated');

// Modal untuk important actions
<SuccessModal
    isOpen={isSuccessModalOpen}
    onClose={handleCloseSuccessModal}
    message="Project created successfully!"
    action={{
        label: 'View Project',
        onClick: () => navigate(`/projects/${projectId}`),
    }}
/>;
```

---

### 5. Role-Based Rendering

```javascript
// hooks/usePermission.js
import { useAuth } from '../contexts/AuthContext';

export const usePermission = () => {
    const { user } = useAuth();

    const canEdit = (resource) => {
        return user?.u_id === resource.created_by;
    };

    const canDelete = (resource) => {
        return user?.u_id === resource.created_by;
    };

    const canSetDueDate = (task) => {
        return user?.u_id === task.tsk_assignee_u_id;
    };

    return { canEdit, canDelete, canSetDueDate };
};

// Usage in component
function TaskDetailPage({ task }) {
    const { canEdit, canDelete, canSetDueDate } = usePermission();

    return (
        <div>
            {/* Show edit button only if user is creator */}
            {canEdit(task) && <button onClick={handleEdit}>Edit Task</button>}

            {/* Show delete button only if user is creator */}
            {canDelete(task) && (
                <button onClick={handleDelete}>Delete Task</button>
            )}

            {/* Show due date input only if user is assignee */}
            {canSetDueDate(task) ? (
                <DatePicker
                    value={task.tsk_due_date}
                    onChange={handleDueDateChange}
                />
            ) : (
                <span>{task.tsk_due_date || 'Not set'}</span>
            )}
        </div>
    );
}
```

---

### 6. Performance Tips

**Caching dengan React Query:**

```javascript
// Query configuration
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes
            cacheTime: 10 * 60 * 1000, // 10 minutes
            refetchOnWindowFocus: false,
        },
    },
});

// Cache master data aggressively (jarang berubah)
const { data: statuses } = useQuery(
    ['master-statuses'],
    () => api.get('/master-statuses'),
    {
        staleTime: Infinity, // Cache forever
        cacheTime: Infinity,
    }
);

// Invalidate cache after mutation
const createTaskMutation = useMutation((data) => api.post('/tasks', data), {
    onSuccess: () => {
        queryClient.invalidateQueries(['tasks']);
        queryClient.invalidateQueries(['project-statistics']);
    },
});
```

**Debouncing search input:**

```javascript
import { useDebounce } from 'use-debounce';

function TaskSearchInput() {
    const [searchTerm, setSearchTerm] = useState('');
    const [debouncedSearchTerm] = useDebounce(searchTerm, 500);

    const { data: tasks } = useQuery(
        ['tasks', 'search', debouncedSearchTerm],
        () => api.post('/tasks/search', { keyword: debouncedSearchTerm }),
        {
            enabled: debouncedSearchTerm.length > 2, // Only search if > 2 chars
        }
    );

    return (
        <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search tasks..."
        />
    );
}
```

**Lazy loading:**

```javascript
// Route-based code splitting
import { lazy, Suspense } from 'react';

const TaskListPage = lazy(() => import('./pages/TaskListPage'));
const TaskDetailPage = lazy(() => import('./pages/TaskDetailPage'));

function App() {
    return (
        <Suspense fallback={<LoadingSpinner />}>
            <Routes>
                <Route path="/tasks" element={<TaskListPage />} />
                <Route path="/tasks/:id" element={<TaskDetailPage />} />
            </Routes>
        </Suspense>
    );
}
```

**Virtual scrolling untuk long lists:**

```javascript
import { useVirtualizer } from '@tanstack/react-virtual';

function TaskList({ tasks }) {
    const parentRef = useRef();

    const virtualizer = useVirtualizer({
        count: tasks.length,
        getScrollElement: () => parentRef.current,
        estimateSize: () => 100, // estimated item height
    });

    return (
        <div ref={parentRef} style={{ height: '500px', overflow: 'auto' }}>
            <div
                style={{
                    height: `${virtualizer.getTotalSize()}px`,
                    position: 'relative',
                }}>
                {virtualizer.getVirtualItems().map((virtualItem) => (
                    <div
                        key={virtualItem.key}
                        style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            width: '100%',
                            height: `${virtualItem.size}px`,
                            transform: `translateY(${virtualItem.start}px)`,
                        }}>
                        <TaskCard task={tasks[virtualItem.index]} />
                    </div>
                ))}
            </div>
        </div>
    );
}
```

---

### 7. File Upload Best Practices

```javascript
import { useDropzone } from 'react-dropzone';

function FileUploadDropzone({ taskId }) {
    const [uploadProgress, setUploadProgress] = useState({});

    const onDrop = useCallback(
        async (acceptedFiles) => {
            // Validate files
            const validFiles = acceptedFiles.filter((file) => {
                const isValidType = [
                    'image/png',
                    'image/jpeg',
                    'image/jpg',
                    'application/pdf',
                ].includes(file.type);
                const isValidSize = file.type.startsWith('image/')
                    ? file.size <= 5_000_000
                    : file.size <= 10_000_000;

                if (!isValidType) {
                    toast.error(`${file.name}: Invalid file type`);
                    return false;
                }
                if (!isValidSize) {
                    toast.error(`${file.name}: File too large`);
                    return false;
                }
                return true;
            });

            // Upload files
            const formData = new FormData();
            validFiles.forEach((file) => {
                formData.append('files', file);
            });

            try {
                const response = await api.post(
                    `/tasks/${taskId}/attachments`,
                    formData,
                    {
                        headers: { 'Content-Type': 'multipart/form-data' },
                        onUploadProgress: (progressEvent) => {
                            const progress = Math.round(
                                (progressEvent.loaded * 100) /
                                    progressEvent.total
                            );
                            setUploadProgress((prev) => ({
                                ...prev,
                                [file.name]: progress,
                            }));
                        },
                    }
                );

                toast.success(
                    `${validFiles.length} file(s) uploaded successfully`
                );
                queryClient.invalidateQueries(['task-attachments', taskId]);
            } catch (error) {
                toast.error('Upload failed');
            }
        },
        [taskId]
    );

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'image/*': ['.png', '.jpg', '.jpeg'],
            'application/pdf': ['.pdf'],
        },
    });

    return (
        <div
            {...getRootProps()}
            className={`dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            {isDragActive ? (
                <p>Drop files here...</p>
            ) : (
                <p>Drag & drop files here, or click to select</p>
            )}

            {/* Show upload progress */}
            {Object.entries(uploadProgress).map(([filename, progress]) => (
                <div key={filename}>
                    <span>{filename}</span>
                    <progress value={progress} max="100" />
                </div>
            ))}
        </div>
    );
}
```

---

## Business Rules & Constraints

### Task Management

-   **Task Code Generation**: Format `{prj_id}/{mtt_code}/{sequential_number}`

    -   Contoh: `001/TASK/001`, `001/BUG/002`
    -   Sequential number per project dan per task type
    -   Immutable setelah dibuat

-   **Due Date Constraint**: Hanya assignee yang bisa set/update `tsk_due_date`

    -   User lain (termasuk creator) tidak bisa mengubah due date
    -   Validation: `tsk_due_date >= tsk_start_date`

-   **Duration Calculation**: Auto-calculated in hours

    -   Rumus: `(tsk_due_date - tsk_start_date) / 3600 seconds`
    -   Read-only field, tidak bisa di-set manual
    -   Null jika salah satu date kosong

-   **Creator-Only Modification**: Hanya creator yang bisa update/delete
    -   Berlaku untuk: Project, Task, Label
    -   Exception: Assignee bisa update `tsk_due_date` di task mereka

### History (Audit Trail)

-   **Immutable Log**: History tidak bisa diubah atau dihapus

    -   No `updated_by` dan `updated_at` fields
    -   No POST/PUT/DELETE endpoints
    -   Hanya GET endpoint available

-   **Auto-Tracking**: Perubahan otomatis dicatat saat task diupdate
    -   Tracked fields: title, description, status, priority, assignee, due_date, start_date
    -   Tidak track field lain (misalnya thumbnail)

### Labels & Watchers

-   **Unique Assignment**: Satu task tidak bisa punya label/watcher yang sama dua kali

    -   Database constraint: UNIQUE (tl_tsk_id, tl_lbl_id)
    -   Database constraint: UNIQUE (tw_tsk_id, tw_u_id)
    -   API akan return 409 Conflict jika duplicate

-   **Bulk Delete**: Support comma-separated IDs
    -   Contoh: DELETE `/tasks/1/labels/1,2,3`
    -   Invalid IDs akan di-skip (tidak error)

### Attachments & Thumbnails

-   **File Type Restrictions**:

    -   Attachments: PDF, PNG, JPG, JPEG
    -   Thumbnail: PNG, JPG, JPEG only (no PDF)

-   **File Size Limits**:

    -   Images: Max 5MB
    -   PDF: Max 10MB
    -   Enforced di backend, validate juga di frontend

-   **Cloudinary Integration**:
    -   Files stored di Cloudinary cloud storage
    -   `ta_cloudinary_public_id` / `tsk_thumbnail` untuk management
    -   Delete dari database akan delete juga dari Cloudinary

### Master Data

-   **Read-Only**: Master data endpoints tidak ada CUD operations
    -   Hanya GET available
    -   Data management via database seed/migration

### Cascade Delete

-   **Project Delete**: Semua tasks di project juga ikut terhapus

    -   Comments, attachments, history, labels, watchers di tasks juga ikut

-   **Task Delete**: Semua nested resources ikut terhapus

    -   Comments, attachments, history, labels, watchers

-   **Label Delete**: Task labels yang menggunakan label ini ikut terhapus

---

## Error Handling Best Practice

### Common Errors & Solutions

#### 1. 401 Unauthorized

-   **Cause**: Token invalid, expired, atau tidak ada
-   **Solution**:
    -   Redirect ke login page
    -   Clear local storage
    -   Show message: "Your session has expired. Please login again."
-   **User Message**: "Session expired. Redirecting to login..."

#### 2. 403 Forbidden (Role Level)

-   **Cause**: User role_level < 10
-   **Solution**:
    -   Shouldn't happen if authentication is correct
    -   Contact backend team jika terjadi
-   **User Message**: "You don't have permission to access this resource."

#### 3. 403 Forbidden (Creator-Only)

-   **Cause**: User bukan creator resource
-   **Solution**:
    -   Hide Edit/Delete buttons untuk non-creator
    -   Jika tetap terjadi (e.g., manual API call), show error
-   **User Message**: "You don't have permission to modify this resource."

#### 4. 403 Forbidden (Due Date - Assignee Only)

-   **Cause**: Non-assignee mencoba set/update due_date
-   **Solution**:
    -   Disable due_date input untuk non-assignee
    -   Show read-only due_date value
-   **User Message**: "Only the assignee can set the due date."

#### 5. 404 Not Found

-   **Cause**: Resource dengan ID tersebut tidak ditemukan
-   **Solution**:
    -   Show 404 page dengan option to go back
    -   Refresh data jika mungkin resource baru dihapus
-   **User Message**: "Resource not found. It may have been deleted."

#### 6. 409 Conflict (Duplicate)

-   **Cause**: Unique constraint violation (e.g., prj_code sudah ada, label sudah di-assign)
-   **Solution**:
    -   Show validation error di form
    -   Suggest alternative (e.g., "Try PRJ-002 instead")
-   **User Message**: "Project with code 'PROJ-001' already exists."

#### 7. 400 Bad Request (Validation)

-   **Cause**: Data tidak valid (e.g., due_date < start_date, required field kosong)
-   **Solution**:
    -   Show field-level validation errors
    -   Highlight invalid fields
    -   Prevent submit jika ada error
-   **User Message**: "Due date must be after start date."

#### 8. 500 Internal Server Error

-   **Cause**: Server error (bug di backend)
-   **Solution**:
    -   Show generic error message
    -   Log error untuk debugging
    -   Provide "Report Issue" button
-   **User Message**: "Something went wrong. Please try again later or contact support."

### Error Handling Strategy

```javascript
// Global error handler
function handleApiError(error) {
    const status = error.response?.status;
    const message = error.response?.data?.message;
    const details = error.response?.data?.details;

    switch (status) {
        case 400:
            // Validation error
            toast.error(message || 'Invalid data');
            return { type: 'validation', message, details };

        case 401:
            // Unauthorized
            toast.error('Session expired. Please login again.');
            localStorage.removeItem('auth_token');
            window.location.href = '/login';
            return { type: 'auth', message: 'Session expired' };

        case 403:
            // Forbidden
            toast.error(message || "You don't have permission");
            return { type: 'permission', message };

        case 404:
            // Not found
            toast.error(message || 'Resource not found');
            return { type: 'not_found', message };

        case 409:
            // Conflict
            toast.error(message || 'Resource already exists');
            return { type: 'conflict', message, details };

        case 500:
            // Server error
            toast.error('Something went wrong. Please try again later.');
            // Log to error tracking service (Sentry, etc.)
            logError(error);
            return { type: 'server_error', message: 'Internal server error' };

        default:
            toast.error('An unexpected error occurred');
            return { type: 'unknown', message: 'Unknown error' };
    }
}

// Usage
try {
    const response = await api.post('/tasks', taskData);
} catch (error) {
    const errorInfo = handleApiError(error);

    // Handle specific error types
    if (errorInfo.type === 'validation' && errorInfo.details) {
        setFieldError(errorInfo.details.field, errorInfo.details.error);
    }
}
```

---

## Integration Notes

### External Services

#### 1. Atlas SSO (ATAMS)

-   **Purpose**: Authentication & user management
-   **Integration**:
    -   User login/logout via Atlas SSO
    -   Token validation di setiap request
    -   User data dari `pt_atams_indonesia.users` table (cross-schema query)

#### 2. Cloudinary

-   **Purpose**: File storage untuk attachments dan thumbnails
-   **Integration**:
    -   Files uploaded via multipart/form-data
    -   Cloudinary returns public_id dan public URL
    -   public_id disimpan untuk file management
    -   Delete file dari DB akan trigger delete di Cloudinary

#### 3. Email Service (SMTP)

-   **Purpose**: Send daily task reminder emails
-   **Integration**:
    -   Configured via environment variables (MAIL_SERVER, MAIL_USERNAME, etc.)
    -   Support Gmail, SendGrid, Mailgun, dan SMTP providers lain
    -   HTML email template dengan Jinja2

### Background Jobs

#### Daily Task Reminder

-   **Job**: Send email reminder untuk tasks starting today
-   **Schedule**: Setiap hari jam 9 pagi (via GitHub Actions)
-   **Trigger**: POST `/api/v1/notifications/send-daily-reminders`
-   **Auth**: Menggunakan CRON_API_KEY di header (bukan JWT token)
-   **Logic**:
    1. Cari tasks dengan `tsk_start_date = today`
    2. Filter tasks yang punya assignee (`tsk_assignee_u_id NOT NULL`)
    3. Untuk setiap task, send email ke assignee
    4. Email berisi: task code, title, project, status, priority, type, reporter, start date, description
    5. Return summary: total tasks, emails sent, emails failed

---

## Testing Guidelines

### Test Scenarios

#### 1. Authentication Flow

-   [ ] User dapat login via Atlas SSO
-   [ ] Token disimpan di localStorage
-   [ ] Token di-attach ke setiap request (Authorization header)
-   [ ] 401 error redirect ke login page
-   [ ] Logout clear token dan redirect

#### 2. Create Task

-   [ ] Form validation bekerja (required fields)
-   [ ] Task code auto-generated (tidak bisa di-input manual)
-   [ ] Dropdown load data dari master data endpoints
-   [ ] User dropdown load dari `/api/v1/users`
-   [ ] Success: Task muncul di task list dengan auto-joined fields
-   [ ] Error handling: Show toast error jika gagal

#### 3. Update Task (Creator-Only)

-   [ ] Edit button hanya muncul untuk creator
-   [ ] Non-creator tidak bisa edit (403 error)
-   [ ] Update berhasil untuk creator
-   [ ] Changes tercatat di history

#### 4. Update Due Date (Assignee-Only)

-   [ ] Due date input hanya enabled untuk assignee
-   [ ] Non-assignee lihat read-only due date
-   [ ] Assignee bisa set/update due date
-   [ ] Validation: due_date >= start_date
-   [ ] Duration auto-calculated setelah set due date

#### 5. Bulk Update Status

-   [ ] Multi-select tasks dengan checkbox
-   [ ] Bulk update button muncul saat ada selection
-   [ ] Status picker modal terbuka
-   [ ] Request berisi task_ids dan ms_id
-   [ ] Response show updated count dan skipped count
-   [ ] Task list refresh setelah update

#### 6. Upload Attachments

-   [ ] Drag & drop files bekerja
-   [ ] File type validation (PDF, PNG, JPG, JPEG only)
-   [ ] File size validation (5MB image, 10MB PDF)
-   [ ] Bulk upload multiple files
-   [ ] Progress bar muncul saat upload
-   [ ] Files muncul di attachment list dengan download link
-   [ ] Delete attachment bekerja (hilang dari list dan Cloudinary)

#### 7. Upload Thumbnail

-   [ ] Single image upload
-   [ ] Image type validation (PNG, JPG, JPEG only)
-   [ ] Max size 5MB
-   [ ] Preview thumbnail setelah upload
-   [ ] Replace thumbnail: old thumbnail terhapus dari Cloudinary
-   [ ] Delete thumbnail: field jadi null

#### 8. Comments & Reply

-   [ ] Post comment berhasil
-   [ ] Reply to comment bekerja (nested/threaded)
-   [ ] Comment muncul dengan user name dan timestamp
-   [ ] Relative time format (e.g., "2 hours ago")

#### 9. Advanced Search

-   [ ] Keyword search bekerja (debounced)
-   [ ] Multi-select filters bekerja (projects, statuses, priorities, assignees, types)
-   [ ] Date range filter bekerja
-   [ ] Active filters tampil sebagai chips/tags
-   [ ] Clear individual filter bekerja
-   [ ] Clear all filters bekerja
-   [ ] Search results accurate

#### 10. Edge Cases

-   [ ] Empty states: No tasks, no projects, no comments
-   [ ] Loading states: Spinner/skeleton saat fetch data
-   [ ] Error states: 404, 403, 500
-   [ ] Long content: Truncate long titles/descriptions
-   [ ] Large lists: Pagination atau virtual scrolling
-   [ ] Offline mode: Show offline indicator

### Mock Data

```javascript
// Mock project
const mockProject = {
    prj_id: 1,
    prj_code: 'PROJ-001',
    prj_name: 'Website Redesign',
    prj_description: 'Redesign company website',
    prj_start_date: '2025-01-15',
    prj_end_date: '2025-06-30',
    prj_u_id: 123,
    prj_owner_name: 'John Doe',
    prj_is_active: true,
    created_by: '123',
    created_at: '2025-01-15T10:00:00Z',
};

// Mock task
const mockTask = {
    tsk_id: 1,
    tsk_code: '001/TASK/001',
    tsk_title: 'Design homepage mockup',
    tsk_description: 'Create high-fidelity mockup for homepage',
    tsk_prj_id: 1,
    tsk_project_name: 'Website Redesign',
    tsk_ms_id: 1,
    tsk_status_name: 'TODO',
    tsk_mp_id: 3,
    tsk_priority_name: 'HIGH',
    tsk_priority_color: '#FF9800',
    tsk_mtt_id: 1,
    tsk_type_name: 'TASK',
    tsk_assignee_u_id: 456,
    tsk_assignee_name: 'Jane Smith',
    tsk_reporter_u_id: 123,
    tsk_reporter_name: 'John Doe',
    tsk_start_date: '2025-01-20T09:00:00Z',
    tsk_due_date: '2025-01-25T17:00:00Z',
    tsk_duration: 128.0,
    tsk_parent_tsk_id: null,
    tsk_thumbnail: null,
    tsk_thumbnail_url: null,
    created_by: '123',
    created_at: '2025-01-20T08:00:00Z',
};

// Mock user
const mockUser = {
    u_id: 123,
    u_username: 'johndoe',
    u_email: 'john@example.com',
    u_full_name: 'John Doe',
    u_is_active: true,
};

// Mock master status
const mockStatuses = [
    { ms_id: 1, ms_name: 'TODO', ms_color: '#6B7280' },
    { ms_id: 2, ms_name: 'IN_PROGRESS', ms_color: '#3B82F6' },
    { ms_id: 3, ms_name: 'IN_REVIEW', ms_color: '#F59E0B' },
    { ms_id: 4, ms_name: 'DONE', ms_color: '#10B981' },
    { ms_id: 5, ms_name: 'CANCELLED', ms_color: '#EF4444' },
];

// Mock master priority
const mockPriorities = [
    { mp_id: 1, mp_name: 'LOW', mp_color: '#10B981' },
    { mp_id: 2, mp_name: 'MEDIUM', mp_color: '#F59E0B' },
    { mp_id: 3, mp_name: 'HIGH', mp_color: '#FF9800' },
    { mp_id: 4, mp_name: 'CRITICAL', mp_color: '#EF4444' },
];
```

---

## Catatan Tambahan

### Keamanan

-   **Token Security**: Simpan token di localStorage atau httpOnly cookie
-   **XSS Prevention**: Sanitize user input sebelum render (terutama di comments)
-   **CSRF Protection**: Gunakan CORS configuration yang benar
-   **File Upload**: Validate file type dan size di frontend DAN backend
-   **SQL Injection**: Backend menggunakan ORM (SQLAlchemy), aman dari SQL injection
-   **Input Validation**: Lakukan validation di frontend dan backend (double check)

### Performance

-   **Lazy Loading**: Split routes dengan React.lazy()
-   **Memoization**: Gunakan React.memo untuk component yang sering re-render
-   **Virtual Scrolling**: Untuk list dengan banyak item (>100)
-   **Debouncing**: Untuk search input (500ms)
-   **Caching**: Cache master data dengan React Query
-   **Image Optimization**: Compress images sebelum upload, atau gunakan Cloudinary transformations

### Limitations

-   **File Upload Size**: Max 5MB (image) dan 10MB (PDF) - informasikan ke user
-   **Pagination Limit**: Max 1000 records per request
-   **Search Keyword**: Minimal 3 karakter untuk trigger search (optional, di frontend)
-   **Nested Comments**: Unlimited depth, tapi tampilkan maksimal 3 level indentation
-   **History Tracking**: Hanya track 7 fields (title, description, status, priority, assignee, due_date, start_date)

### Known Issues & Workarounds

-   **Timezone**: Timestamps dalam UTC, convert ke local timezone di frontend

    ```javascript
    import { format, parseISO } from 'date-fns';

    const localTime = format(parseISO(task.created_at), 'PPpp');
    ```

-   **Long Text**: Truncate panjang text di list view
    ```javascript
    const truncate = (text, maxLength = 100) => {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    };
    ```
-   **Refresh After Update**: Invalidate React Query cache untuk refresh data
    ```javascript
    queryClient.invalidateQueries(['tasks']);
    ```

---

## Changelog / Version History

### Version 1.0.0 - 2025-01-31

**New Features:**

-   Task thumbnail upload & delete endpoints
-   Bulk attachment upload support
-   Task advanced search with multiple filters
-   Bulk task status update
-   Project statistics endpoint
-   User dashboard endpoint

**Changes:**

-   Master data endpoints changed to READ-ONLY (removed POST, PUT, DELETE)
-   Attachment endpoints moved from `/api/v1/attachments` to `/api/v1/tasks/{tsk_id}/attachments`
-   All nested resources (comments, attachments, history, labels, watchers) now only accessible via `/api/v1/tasks/{tsk_id}/*`

**Improvements:**

-   Auto-join optimization untuk mengurangi N+1 queries
-   Better error messages dengan details object
-   Response encryption support (optional via ENCRYPTION_ENABLED)

---

## Glossary

-   **ATAMS**: Atlas Authentication & Management System - sistem SSO untuk autentikasi
-   **Task Code**: Unique identifier untuk task, auto-generated format `{prj_id}/{type_code}/{number}`
-   **Creator-Only**: Aturan bahwa hanya user yang membuat resource yang bisa update/delete
-   **Assignee-Only**: Khusus untuk due_date, hanya assignee yang bisa set/update
-   **Auto-Join**: Field tambahan di response yang di-join dari tabel lain (e.g., prj_owner_name, tsk_status_name)
-   **Immutable Log**: History yang tidak bisa diubah atau dihapus setelah dibuat
-   **Cascade Delete**: Saat parent dihapus, child records juga ikut terhapus
-   **Bulk Operation**: Operasi yang bisa dilakukan untuk multiple records sekaligus
-   **Cloudinary**: Cloud storage service untuk menyimpan file attachments dan thumbnails
-   **Public ID**: Identifier unik file di Cloudinary (e.g., "atask/thumbnails/abc123")
-   **Public URL**: URL publik untuk akses file di Cloudinary
-   **Role Level**: Level akses user, minimal 10 untuk akses API
-   **Cross-Schema Query**: Query yang mengambil data dari schema database lain (pt_atams_indonesia)
