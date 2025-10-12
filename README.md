# Atask - Task Management API

Atask is a task management application built with FastAPI and integrated with ATAMS (Atlas Authentication & Management System). This system provides a complete REST API to manage projects, tasks, comments, attachments, history, labels, and watchers.

## Table of Contents

* [Main Features](#main-features)
* [Technology](#technology)
* [Installation](#installation)
* [Configuration](#configuration)
* [Running the Application](#running-the-application)
* [API Endpoints](#api-endpoints)

  * [Master Data](#master-data)
  * [Projects](#projects)
  * [Tasks](#tasks)
  * [Nested Resources](#nested-resources)
  * [Labels](#labels)
  * [Users](#users)
  * [Notifications](#notifications)
* [Explanation of Unique Parameters](#explanation-of-unique-parameters)
* [Response Format](#response-format)
* [Authentication & Authorization](#authentication--authorization)
* [Validation Rules](#validation-rules)

## Main Features

* **Project Management**: Full CRUD for projects with task statistics and auto-join owner information
* **Task Management**: Task CRUD with support for sub-tasks, priority, status, and type
* **Auto-Generated Task Code**: Task code is automatically generated based on project and task type
* **Task Duration Auto-Calculate**: Duration is automatically calculated in hours from start_date to due_date
* **Comments & Discussion**: Comment system with threading (reply to comment)
* **File Attachment**: Upload and download files for each task using Cloudinary
* **Email Notification**: Automated daily task reminder via email for assignees (scheduled with GitHub Actions)
* **Immutable Audit Trail**: Automatically track task changes in history (log-only, cannot be changed/deleted)
* **Labeling System**: Flexible tags/labels for task categorization with bulk operations
* **Task Watcher**: Subscribe to receive task change notifications with bulk operations
* **Advanced Search**: Task search with multiple filters
* **Bulk Operations**: Update the status of multiple tasks at once
* **User Dashboard**: Personal dashboard with statistics and activity
* **Response Encryption**: Automatic encryption for response data (optional)
* **Atlas SSO Integration**: Authentication integrated with ATAMS
* **Role-based Access**: Access control based on user role level
* **Creator-only Modification**: Only the creator can update/delete resources

## Technology

* **Framework**: FastAPI (Python 3.8+)
* **Database**: PostgreSQL
* **ORM**: SQLAlchemy
* **Authentication**: Atlas SSO (ATAMS)
* **Validation**: Pydantic
* **Server**: Uvicorn
* **File Storage**: Cloudinary
* **Email**: SMTP (Gmail, SendGrid, etc.)
* **Template Engine**: Jinja2
* **Scheduling**: GitHub Actions (Serverless Cron)

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/GratiaManullang03/atask.git
cd atask
```

2. **Create a virtual environment**

```bash
python -m venv venv
```

3. **Activate the virtual environment**

* Windows:

```bash
venv\Scripts\activate
```

* Linux/Mac:

```bash
source venv/bin/activate
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root folder with the following configuration:

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

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
CLOUDINARY_FOLDER=atask

# Email Configuration
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=noreply@yourdomain.com
MAIL_FROM_NAME=Atask Notification
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_USE_TLS=True
MAIL_USE_SSL=False

# App URL
APP_URL=YOUR_APP_URL

# Cron API Key (generate: openssl rand -hex 32)
CRON_API_KEY=your_secure_random_key_here

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

## Running the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will run at `http://localhost:8000`

* **API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **API Documentation (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

Base URL: `/api/v1`

### Master Data

#### Master Status

Endpoint to manage master data for task status (To Do, In Progress, Done, etc.).

* `GET /api/v1/master-statuses` - Get all statuses
* `GET /api/v1/master-statuses/{ms_id}` - Get status by ID
* `POST /api/v1/master-statuses` - Create new status
* `PUT /api/v1/master-statuses/{ms_id}` - Update status (creator only)
* `DELETE /api/v1/master-statuses/{ms_id}` - Delete status (creator only)

#### Master Priority

Endpoint to manage master data for task priority (Low, Medium, High, Critical).

* `GET /api/v1/master-priorities` - Get all priorities
* `GET /api/v1/master-priorities/{mp_id}` - Get priority by ID
* `POST /api/v1/master-priorities` - Create new priority
* `PUT /api/v1/master-priorities/{mp_id}` - Update priority (creator only)
* `DELETE /api/v1/master-priorities/{mp_id}` - Delete priority (creator only)

#### Master Task Type

Endpoint to manage master data for task types (Task, Bug, Feature, etc.).

* `GET /api/v1/master-task-types` - Get all task types
* `GET /api/v1/master-task-types/{mtt_id}` - Get task type by ID
* `POST /api/v1/master-task-types` - Create new task type
* `PUT /api/v1/master-task-types/{mtt_id}` - Update task type (creator only)
* `DELETE /api/v1/master-task-types/{mtt_id}` - Delete task type (creator only)

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

**Response:** `201 Created` with an additional field `prj_owner_name` (auto-joined)

#### Get All Projects

```http
GET /api/v1/projects?skip=0&limit=100
```

**Response:** `200 OK` - All projects with `prj_owner_name` (auto-joined)

#### Get Project by ID

```http
GET /api/v1/projects/{prj_id}
```

**Response:** `200 OK` - Project details with `prj_owner_name` (auto-joined)

#### Update Project

```http
PUT /api/v1/projects/{prj_id}
```

**Authorization:** ⚠️ **Only creator (created_by) can update**

**Request Body:** (all fields optional)

```json
{
  "prj_name": "Website Redesign v2",
  "prj_description": "Updated description",
  "prj_end_date": "2025-07-15",
  "prj_is_active": true
}
```

**Response:** `200 OK` or `403 Forbidden` if not the creator

#### Delete Project

```http
DELETE /api/v1/projects/{prj_id}
```

**Authorization:** ⚠️ **Only creator (created_by) can delete**

**Response:** `204 No Content` or `403 Forbidden`

#### Get Project Statistics

```http
GET /api/v1/projects/{prj_id}/statistics
```

**Response:** `200 OK` - Complete statistics with nested structure:

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

* ✅ `tsk_code` is **auto-generated** (format: `{prj_id}/{task_type_code}/{number}`)
* ❌ `tsk_due_date` **cannot be set at creation** (only the assignee can set it later)
* ❌ `tsk_duration` **is auto-calculated** (read-only, in hours)

**Response:** `201 Created` with joins:

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

**Response:** `200 OK` - All tasks with auto-joins (project_name, status_name, etc.)

#### Get Task by ID

```http
GET /api/v1/tasks/{tsk_id}
```

**Response:** `200 OK` - Complete details with auto-joins

#### Update Task

```http
PUT /api/v1/tasks/{tsk_id}
```

**Authorization:** ⚠️ **Only creator (created_by) can update**

**Request Body:** (all fields optional)

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

* ✅ `tsk_due_date` **can only be set by the assignee** (or null to clear)
* ✅ `due_date >= start_date` (validation error if due_date is earlier)
* ✅ `tsk_duration` **auto-calculated in hours** from (due_date - start_date)
* ❌ `tsk_duration` **cannot be manually set** (read-only)
* ❌ Non-creator **cannot update task** (403 Forbidden)

**Response:** `200 OK` or `400 Bad Request` or `403 Forbidden`

#### Delete Task

```http
DELETE /api/v1/tasks/{tsk_id}
```

**Authorization:** ⚠️ **Only creator (created_by) can delete**

**Response:** `204 No Content` or `403 Forbidden`

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

**Response:** `200 OK` - Info on the number of tasks successfully updated

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

**Response:** `200 OK` with pagination and auto-joins

### Nested Resources

> **Important:** Comments, History, Labels, and Watchers are nested resources under tasks.
> Standalone endpoints (`/api/v1/comments`, `/api/v1/history`, etc.) **have been removed**.

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

**Response:** List of comments with auto-joins: `tc_task_title`, `tc_user_name`, `tc_user_email`

#### Task History (Audit Log)

```http
GET /api/v1/tasks/{tsk_id}/history?skip=0&limit=100&field_name=status
```

**Important:**

* 📝 History is an **immutable audit log**
* ✅ **Auto-created** when a task is updated
* ✅ **Only GET** endpoint available
* ❌ **NO POST/PUT/DELETE** endpoints (cannot manually create/update/delete)
* ❌ **NO updated_by/updated_at** fields (log is immutable)

**Response:** History list with auto-joins: `th_task_title`, `th_user_name`

**Tracked Fields:**

* `title`, `description`, `status`, `priority`, `assignee`, `due_date`, `start_date`

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

**Response:** Label list with auto-joins: `tl_task_title`, `tl_label_name`, `tl_label_color`

```http
DELETE /api/v1/tasks/{tsk_id}/labels/{lbl_ids}
```

**Bulk Delete:** `lbl_ids` can be comma-separated (e.g., `1,2,3`)

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

**Response:** Watcher list with auto-joins: `tw_task_title`, `tw_user_name`, `tw_user_email`

```http
DELETE /api/v1/tasks/{tsk_id}/watchers/{u_ids}
```

**Bulk Delete:** `u_ids` can be comma-separated (e.g., `2,3,4`)

#### Task Attachments

**Upload File Attachment**

```http
POST /api/v1/attachments?task_id={tsk_id}
Content-Type: multipart/form-data
```

**Request:**

* Form field `file`: File to upload
* Query param `task_id`: Task ID

**Validation:**

* Allowed types: PDF (.pdf), Images (.png, .jpg, .jpeg)
* Max size: 5MB (images), 10MB (PDF)
* Files uploaded to Cloudinary

**Get All Attachments**

```http
GET /api/v1/attachments?skip=0&limit=100
```

**Get Attachment by ID**

```http
GET /api/v1/attachments/{ta_id}
```

**Update Attachment Metadata**

```http
PUT /api/v1/attachments/{ta_id}
```

**Request Body:**

```json
{
  "ta_file_name": "new_filename.pdf"
}
```

**Delete Attachment**

```http
DELETE /api/v1/attachments/{ta_id}
```

Deletes from the database and Cloudinary.

**Download Attachment**

```http
GET /api/v1/attachments/{ta_id}/download
```

Forces download with the proper Content-Disposition header.

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

**Response:** User list from Atlas SSO

#### Get User Dashboard

```http
GET /api/v1/users/{u_id}/dashboard
```

**Response:** User dashboard with statistics (assigned tasks, reported tasks, watched tasks, recent activities)

#### Get Watched Tasks by User

```http
GET /api/v1/users/{u_id}/watched-tasks?skip=0&limit=100&status_id=2
```

### Notifications

Email notification system to remind assignees about tasks starting today.

#### Send Daily Reminders (Scheduled Endpoint)

```http
POST /api/v1/notifications/send-daily-reminders
Headers:
  X-Api-Key: {CRON_API_KEY}
```

**Security:** Requires `CRON_API_KEY` in the header

**Triggered by:** GitHub Actions at 9 AM

**Logic:**

* Find tasks where `tsk_start_date = today`
* Filter tasks that have an assignee (`tsk_assignee_u_id NOT NULL`)
* Send HTML email to the assignee

**Response:**

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

#### Notification Health Check

```http
GET /api/v1/notifications/health
```

**No authentication required** - for monitoring

**Response:**

```json
{
  "status": "ok",
  "email_configured": true,
  "cron_api_key_configured": true
}
```

#### Email Template Info

The email notification contains:

* Greeting with the assignee's name
* Task code & title
* Project name & code
* Status, Priority, Type
* Reporter name
* Start date
* Task description (if any)
* Beautiful responsive HTML design

#### GitHub Actions Setup

1. **Add GitHub Secrets:**

   * `APP_URL`: Your application URL (e.g., `https://your-app.vercel.app`)
   * `CRON_API_KEY`: Same value as the env variable `CRON_API_KEY`

2. **Workflow File:** `.github/workflows/daily-task-reminder.yml`

3. **Schedule:** Runs at `02:00 UTC` daily (09:00 WIB)

4. **Manual Trigger:** Can be triggered manually from the GitHub Actions tab

## Explanation of Unique Parameters

### Project Parameters

| Parameter         | Type    | Description                                 |
| ----------------- | ------- | ------------------------------------------- |
| `prj_id`          | Integer | Unique project ID (Primary Key)             |
| `prj_code`        | String  | Unique project code                         |
| `prj_name`        | String  | Project name                                |
| `prj_description` | Text    | Full project description                    |
| `prj_start_date`  | Date    | Project start date                          |
| `prj_end_date`    | Date    | Target completion date                      |
| `prj_u_id`        | Integer | Project owner user ID                       |
| `prj_owner_name`  | String  | **Auto-joined** owner name from Atlas users |
| `prj_is_active`   | Boolean | Project active/inactive status              |

### Task Parameters

| Parameter            | Type      | Description                                                |
| -------------------- | --------- | ---------------------------------------------------------- |
| `tsk_id`             | Integer   | Unique task ID (Primary Key)                               |
| `tsk_code`           | String    | **Auto-generated** format: `{prj_id}/{type_code}/{number}` |
| `tsk_title`          | String    | Task title/summary                                         |
| `tsk_description`    | Text      | Full task description                                      |
| `tsk_prj_id`         | Integer   | Project ID (required)                                      |
| `tsk_ms_id`          | Integer   | Master status ID (required)                                |
| `tsk_mp_id`          | Integer   | Master priority ID (required)                              |
| `tsk_mtt_id`         | Integer   | Master task type ID (required)                             |
| `tsk_assignee_u_id`  | Integer   | Assigned user ID (optional)                                |
| `tsk_reporter_u_id`  | Integer   | Reporter user ID (required)                                |
| `tsk_start_date`     | Timestamp | Start date                                                 |
| `tsk_due_date`       | Timestamp | Deadline (**only assignee can set**)                       |
| `tsk_duration`       | Decimal   | **Auto-calculated in hours** (read-only)                   |
| `tsk_parent_tsk_id`  | Integer   | Parent task ID for sub-tasks                               |
| `tsk_project_name`   | String    | **Auto-joined** project name                               |
| `tsk_status_name`    | String    | **Auto-joined** status name                                |
| `tsk_priority_name`  | String    | **Auto-joined** priority name                              |
| `tsk_priority_color` | String    | **Auto-joined** priority color                             |
| `tsk_type_name`      | String    | **Auto-joined** type name                                  |
| `tsk_assignee_name`  | String    | **Auto-joined** assignee name                              |
| `tsk_reporter_name`  | String    | **Auto-joined** reporter name                              |

### History Parameters

| Parameter       | Type      | Description                     |
| --------------- | --------- | ------------------------------- |
| `th_id`         | Integer   | Unique history ID (Primary Key) |
| `th_tsk_id`     | Integer   | Task ID that changed            |
| `th_field_name` | String    | Field that was changed          |
| `th_old_value`  | String    | Old value                       |
| `th_new_value`  | String    | New value                       |
| `th_u_id`       | Integer   | User ID who made the change     |
| `th_task_title` | String    | **Auto-joined** task title      |
| `th_user_name`  | String    | **Auto-joined** user name       |
| `created_by`    | String    | User who created the record     |
| `created_at`    | Timestamp | Creation time                   |

**Note:** History **does not have** `updated_by` and `updated_at` (immutable log)

## Response Format

### Success Response with Data

```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Success Response with Pagination

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

All endpoints require an authentication header:

```
Authorization: Bearer {token}
```

The token is obtained from Atlas SSO. Every request will be validated and will receive user information (user_id, username, role_level, etc.).

### Authorization Rules

**Minimum Role Level:** Minimum role level **10** for API access.

**Creator-Only Operations:**

* ⚠️ **UPDATE**: Only the creator (`created_by == current_user_id`) can update
* ⚠️ **DELETE**: Only the creator (`created_by == current_user_id`) can delete
* Applies to: Projects, Tasks, Master Data

**Special Task Rules:**

* ⚠️ **tsk_due_date**: Only the assignee (`tsk_assignee_u_id == current_user_id`) can set/update
* ⚠️ **tsk_duration**: Read-only, auto-calculated (cannot be manually set)

## Validation Rules

### Task Validation

1. **Task Code**: Auto-generated, format `{prj_id}/{type_code}/{number}` (e.g., `005/BUG/001`)
2. **Due Date**: Must be >= start_date (error if due_date is earlier)
3. **Duration**: Auto-calculated in **hours** from (due_date - start_date), read-only
4. **Assignee-Only Due Date**: Only the assignee can set/update `tsk_due_date`
5. **Creator-Only Modification**: Only the creator can update/delete the task

### Project Validation

1. **Project Code**: Must be unique
2. **Creator-Only Modification**: Only the creator can update/delete the project

### History (Audit Log)

1. **Immutable Log**: Cannot be updated or deleted via API
2. **Auto-Created**: Automatically created on task updates
3. **No Manual Creation**: No POST endpoint available
4. **Tracked Fields**: title, description, status, priority, assignee, due_date, start_date

### Label & Watcher

1. **Unique Assignment**: A task cannot have the same label/watcher more than once
2. **Bulk Delete**: Supports comma-separated IDs (e.g., `DELETE /tasks/1/labels/1,2,3`)

## Audit Fields

Every table has audit fields:

* `created_by` - ID of the user who created the record
* `created_at` - Creation timestamp
* `updated_by` - ID of the user who last updated the record
* `updated_at` - Last update timestamp

**Exception:** The `task_history` table only has `created_by` and `created_at` (immutable log).

## Response Encryption

Response data can be automatically encrypted if `ENCRYPTION_ENABLED=true`. The client needs to decrypt using the appropriate key and IV.

## Important Notes

1. **Clean Architecture**: Uses 3-layer architecture (Presentation → Service → Repository)

2. **Immutable Audit Trail**: History is a log that cannot be changed/deleted

3. **Auto-Generated Fields**:

   * Task code auto-generated
   * Task duration auto-calculated
   * History auto-created on updates

4. **Auto-Joins**: All foreign keys are auto-joined with related data (user name, project name, etc.)

5. **Cascade Delete**: When a task is deleted, all related data (comments, history, labels, watchers) is also deleted

6. **Nested Resources**: Comments, history, labels, watchers are only accessible via `/tasks/{tsk_id}/*`

7. **Duration in Hours**: Task duration is calculated in **hours**

8. **File Upload**: Attachments use Cloudinary for cloud storage

9. **Email Notifications**:

   * Automated daily reminders via GitHub Actions
   * Triggered at 9 AM (WIB)
   * Beautiful HTML email template
   * Supports Gmail, SendGrid, Mailgun, and other SMTP providers

10. **Serverless Deployment**: Compatible with Vercel serverless deployment
