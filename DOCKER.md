# Docker Deployment Guide - Atask

Panduan lengkap untuk menjalankan aplikasi Atask menggunakan Docker.

## 📋 Prerequisites

- Docker 20.10 atau lebih baru
- Docker Compose 2.0 atau lebih baru
- File `.env` yang sudah dikonfigurasi (copy dari `.env.example`)

## 🚀 Quick Start

### 1. Persiapan Environment

Copy file `.env.example` menjadi `.env` dan sesuaikan konfigurasi:

```bash
cp .env.example .env
```

Edit file `.env` dan pastikan konfigurasi berikut sudah benar:

```env
# Application
APP_NAME=atask
APP_VERSION=1.0.0
DEBUG=false

# Database (Cloud Database - sudah ada)
DATABASE_URL=postgresql://user:password@your-cloud-db-host:5432/atask

# Atlas SSO (wajib diisi)
ATLAS_SSO_URL=https://api.atlas-microapi.atamsindonesia.com/api/v1
ATLAS_APP_CODE=ATASK
ATLAS_ENCRYPTION_KEY=your-32-char-encryption-key
ATLAS_ENCRYPTION_IV=your-16-char-iv

# Response Encryption (opsional)
ENCRYPTION_ENABLED=false
ENCRYPTION_KEY=your-encryption-key
ENCRYPTION_IV=your-encryption-iv

# CORS (opsional)
CORS_ORIGINS=["*"]

# Logging
LOGGING_ENABLED=true
LOG_LEVEL=INFO
LOG_TO_FILE=false
```

### 2. Build Docker Image

```bash
docker-compose build
```

### 3. Run Application

```bash
docker-compose up -d
```

Aplikasi akan berjalan di `http://localhost:8000`

### 4. Check Logs

```bash
docker-compose logs -f app
```

### 5. Stop Application

```bash
docker-compose down
```

## 📝 Docker Commands Reference

### Build & Run

```bash
# Build image
docker-compose build

# Run in background
docker-compose up -d

# Run in foreground (see logs directly)
docker-compose up

# Force recreate containers
docker-compose up -d --force-recreate

# Build and run
docker-compose up -d --build
```

### Logs & Monitoring

```bash
# View logs
docker-compose logs app

# Follow logs (real-time)
docker-compose logs -f app

# View last 100 lines
docker-compose logs --tail=100 app

# Check container status
docker-compose ps

# Check container health
docker inspect atask_app --format='{{.State.Health.Status}}'
```

### Container Management

```bash
# Stop containers
docker-compose stop

# Start stopped containers
docker-compose start

# Restart containers
docker-compose restart

# Remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

### Exec Commands

```bash
# Access container shell
docker-compose exec app bash

# Run Python commands
docker-compose exec app python -c "import sys; print(sys.version)"

# Check database connection
docker-compose exec app python -c "from app.db.session import engine; print(engine)"
```

## 🔧 Configuration

### Environment Variables

Semua environment variables diambil dari file `.env`. Berikut variabel yang tersedia:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Nama aplikasi | atask |
| `APP_VERSION` | Versi aplikasi | 1.0.0 |
| `DEBUG` | Debug mode | false |
| `DATABASE_URL` | Database connection string | - |
| `ATLAS_SSO_URL` | Atlas SSO API URL | - |
| `ATLAS_APP_CODE` | Atlas application code | ATASK |
| `ATLAS_ENCRYPTION_KEY` | Atlas encryption key | - |
| `ATLAS_ENCRYPTION_IV` | Atlas encryption IV | - |
| `ENCRYPTION_ENABLED` | Enable response encryption | false |
| `ENCRYPTION_KEY` | Response encryption key | - |
| `ENCRYPTION_IV` | Response encryption IV | - |
| `CORS_ORIGINS` | Allowed CORS origins | - |
| `LOGGING_ENABLED` | Enable logging | true |
| `LOG_LEVEL` | Log level | INFO |
| `LOG_TO_FILE` | Write logs to file | false |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | true |
| `RATE_LIMIT_REQUESTS` | Max requests | 100 |
| `RATE_LIMIT_WINDOW` | Time window (seconds) | 60 |

### Volumes

Docker compose meng-mount 2 direktori:

1. **`./logs:/app/logs`** - Untuk menyimpan log files (jika `LOG_TO_FILE=true`)
2. **`./uploads:/app/uploads`** - Untuk menyimpan uploaded files (future feature)

### Ports

- **8000**: HTTP API port (mapped ke host)

## 🏥 Health Check

Container memiliki built-in health check yang mengecek endpoint `/health` setiap 30 detik.

Status health check:

```bash
docker inspect atask_app --format='{{.State.Health.Status}}'
```

Possible statuses:
- `starting` - Container baru saja start
- `healthy` - Container berjalan normal
- `unhealthy` - Ada masalah dengan container

## 🐛 Troubleshooting

### Container tidak bisa start

1. Check logs:
```bash
docker-compose logs app
```

2. Check environment variables:
```bash
docker-compose config
```

3. Check database connection:
```bash
docker-compose exec app python -c "from app.db.session import engine; engine.connect()"
```

### Container restart terus-menerus

1. Check health check status:
```bash
docker inspect atask_app --format='{{.State.Health}}'
```

2. Disable auto restart sementara di `docker-compose.yml`:
```yaml
restart: "no"
```

### Cannot connect to database

1. Pastikan `DATABASE_URL` di `.env` sudah benar
2. Test koneksi dari container:
```bash
docker-compose exec app psql $DATABASE_URL -c "SELECT 1"
```

### Port 8000 already in use

Stop service yang menggunakan port 8000, atau ubah port di `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Host:Container
```

## 📦 Production Deployment

### Best Practices

1. **Jangan gunakan DEBUG=true di production**
2. **Gunakan ENCRYPTION_ENABLED=true untuk keamanan**
3. **Set LOG_TO_FILE=true dan monitor logs**
4. **Gunakan reverse proxy (nginx/traefik) di depan container**
5. **Gunakan secrets management untuk sensitive data**
6. **Set resource limits di docker-compose.yml**

### Resource Limits

Tambahkan resource limits di `docker-compose.yml`:

```yaml
services:
  app:
    # ... existing config
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Using with Nginx

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔐 Security Notes

1. **Never commit `.env` file to git**
2. **Use strong encryption keys**
3. **Keep Docker and base images updated**
4. **Run container as non-root user** (future improvement)
5. **Use read-only root filesystem** (future improvement)

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [ATAMS Documentation](https://docs.atamsindonesia.com)

## 🆘 Support

Untuk bantuan lebih lanjut, hubungi tim development atau buat issue di repository.
