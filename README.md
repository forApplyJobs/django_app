# Django Image Processing & Feed Management Application with WebSockets

This project is a Django-based image processing and feed management application with real-time WebSocket progress updates. The main purpose of the project is to automatically add frames to products in XML feeds with live progress tracking.

## 🚀 Features

- **User Authentication**: Django built-in authentication system
- **Frame Management**: Upload and manage frame templates
- **XML Feed Processing**: Automatic feed parsing and product image fetching
- **Coordinate Configuration**: Interactive product positioning in preview screen
- **Bulk Image Generation**: Background processing with Celery
- **Real-time Progress Updates**: WebSocket-based live progress tracking
- **DataTable Management**: Server-side pagination and search functionality
- **Image Download/Delete**: Manage generated outputs
- **Frame CRUD Operations**: Create, read, update, delete frames
- **Interactive Preview**: Drag & resize coordinates with real-time preview

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7
- **Database**: PostgreSQL (Docker) / SQLite (Development)
- **Image Processing**: Pillow (PIL)
- **Background Jobs**: Celery + Redis
- **WebSockets**: Django Channels + Redis Channel Layer
- **ASGI Server**: Daphne (required for WebSocket support)
- **Frontend**: Bootstrap 5, jQuery, DataTables
- **Deployment**: Docker + Docker Compose

## 🐳 Docker Deployment (Recommended)

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd django_app
```

2. **Create environment file**
```bash
cp .env.docker .env
# Edit .env with your settings
```

3. **Start all services**
```bash
# For production
docker-compose up -d

# For development (with hot reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

4. **Access the application**
- **Web Interface**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin (admin/admin123456)
- **Database**: localhost:5432
- **Redis**: localhost:6379

### Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f web
docker-compose logs -f celery

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access Django shell
docker-compose exec web python manage.py shell

# Stop services
docker-compose down

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Production with Nginx

```bash
# Start with Nginx proxy
docker-compose --profile production up -d

# Access via Nginx
curl http://localhost/
```

## 📋 Local Development Installation

### 1. Clone the Project
```bash
git clone <repository-url>
cd django_app
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
Create `.env` file:
```env
DJANGO_SETTINGS_MODULE=project.settings
SECRET_KEY=xqm_&lp6bi_4vl4ebx11$v!lp^sl^+lrp5znckfoxj-^q3v&+k
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Start Redis Server (Required for Celery and WebSockets)
```bash
# Windows (Redis for Windows required)
redis-server

# Linux/Mac
sudo service redis-server start
# or
sudo systemctl start redis-server

# macOS with Homebrew
brew services start redis
```

### 8. Start Celery Worker (Background Processing)
Open new terminal:
```bash
cd django_app
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
celery -A project worker --loglevel=info
```

### 9. Start Django with Daphne (WebSocket Support)
**Important**: Use Daphne instead of regular Django dev server for WebSocket support:
```bash
# Start with Daphne (required for WebSockets)
daphne project.asgi:application

# For specific host/port
daphne -b 127.0.0.1 -p 8000 project.asgi:application

# For production with external access
daphne -b 0.0.0.0 -p 8000 project.asgi:application
```

**Note**: Do NOT use `python manage.py runserver` as it doesn't support WebSockets!

## 🌐 WebSocket Features

### Real-time Progress Updates
When processing XML feeds, the application provides live progress updates via WebSockets:

- **Connection**: `ws://localhost:8000/ws/progress/{frame_id}/`
- **Authentication**: Requires user login
- **Progress Data**: 
  ```json
  {
    "processed": 15,
    "total": 100,
    "product_id": "current_processing_id"
  }
  ```
- **Error Handling**: Real-time error notifications
- **Auto-reload**: Page refreshes when processing completes

### WebSocket Configuration
The application includes:
- **ASGI Configuration**: `project/asgi.py` with WebSocket routing
- **Channel Layers**: Redis-based channel layer for WebSocket communication
- **Consumer**: `app/consumers.py` handles WebSocket connections
- **Routing**: `app/routing.py` defines WebSocket URL patterns

## 🎯 Usage

### 1. System Access
- Go to `http://localhost:8000/` (Docker) or `http://127.0.0.1:8000/` (Local)
- Register or login

### 2. Adding New Frame
- Click "Add New Frame" button
- Enter frame name
- Upload frame image (JPG/PNG)
- Enter XML Feed URL: `https://cdn.goanalytix.io/assets/casestudy/CaseStudyFeed.xml`

### 3. Coordinate Configuration
- Click "Preview & Edit" on your frame
- Adjust product image position in preview screen
- Use drag & drop or manual coordinate input
- Set X, Y coordinates and dimensions
- See result with real-time preview
- Save with "Save & Generate Images"

### 4. Real-time Processing
- After saving coordinates, processing starts automatically
- **Live progress bar** shows current status
- **WebSocket updates** provide real-time feedback:
  - Number of processed items
  - Total items to process
  - Currently processing product ID
  - Error notifications if issues occur
- Page automatically refreshes when complete

### 5. Output Management
- View generated images on Frame Details page
- Search and pagination with DataTable
- Download individual images
- Delete unwanted outputs
- Real-time table updates

## 🔧 Technical Details

### ASGI vs WSGI
- **WSGI** (traditional): HTTP only, no WebSocket support
- **ASGI** (this app): HTTP + WebSocket support via Daphne

### WebSocket Architecture
```
Frontend (JavaScript) ←→ Daphne ←→ Django Channels ←→ Redis ←→ Celery Tasks
```

### Required Services
1. **Database**: PostgreSQL (Docker) or SQLite (Local)
2. **Redis Server**: Message broker + WebSocket channel layer
3. **Celery Worker**: Background image processing
4. **Daphne Server**: ASGI server with WebSocket support

## 📁 Project Structure

```
django_app/
│
├── media/                  # Uploaded files
│   ├── frames/            # Frame templates
│   └── outputs/           # Generated output images
│
├── app/                   # Main Django application
│   ├── templates/         # HTML templates
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── tasks.py          # Celery tasks with WebSocket updates
│   ├── consumers.py      # WebSocket consumers
│   ├── routing.py        # WebSocket URL routing
│   ├── utils.py          # Helper functions
│   └── forms.py          # Django forms
│
├── project/              # Django project settings
│   ├── settings.py       # Main settings + Channels config
│   ├── asgi.py          # ASGI configuration with WebSockets
│   ├── urls.py          # URL routing
│   └── celery.py        # Celery configuration
│
├── docker-compose.yml    # Docker services configuration
├── Dockerfile           # Django app container
├── nginx.conf          # Nginx configuration
├── requirements.txt    # Python dependencies
├── manage.py          # Django management script
└── README.md          # This file
```

## 🔧 API Endpoints & WebSockets

### HTTP Endpoints
- `/` - Home page (Frame list)
- `/login/` - User login
- `/register/` - User registration
- `/add-frame/` - Add new frame
- `/frame/<id>/preview/` - Coordinate configuration
- `/frame/<id>/edit/` - Edit frame
- `/frame/<id>/delete/` - Delete frame
- `/frame_detail/<id>/` - Frame details with progress
- `/frame/<id>/outputs-ajax/` - DataTable AJAX
- `/delete_output/<id>/` - Delete output

### WebSocket Endpoints
- `/ws/progress/{frame_id}/` - Real-time progress updates

## 🎨 XML Feed Structure

The application supports the following XML structure:

```xml
<feed xmlns:g="http://base.google.com/ns/1.0" xmlns="http://www.w3.org/2005/Atom">
    <title>3GEN Case Study Feed</title>
    <entry>
        <id>000000101929043004</id>
        <image_link>https://cdn.goanalytix.io/assets/casestudy/images/1.jpg</image_link>
    </entry>
    <!-- Other products... -->
</feed>
```

## 🚨 Important Notes

### Docker Deployment
1. **Always use Docker for production**: Ensures consistency across environments
2. **Environment variables**: Set proper values in `.env` file
3. **Data persistence**: Volumes ensure data survives container restarts
4. **Health checks**: Services wait for dependencies to be ready

### Local Development
1. **Always use Daphne**: `daphne project.asgi:application`
2. **Never use**: `python manage.py runserver` (no WebSocket support)
3. **Redis must be running** for both Celery and WebSockets
4. **Celery worker must be active** for background processing

### Development vs Production
```bash
# Development with Docker
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production with Docker
docker-compose up -d

# Production with Nginx
docker-compose --profile production up -d
```

### Common Issues
1. **WebSocket connection fails**: 
   - Ensure using Daphne, not Django dev server
   - Check Redis is running
   - Verify ALLOWED_HOSTS includes your domain

2. **Progress updates not working**: 
   - Verify Celery worker is running
   - Check Redis connectivity
   - Ensure user is authenticated

3. **Database connection issues**:
   - Check PostgreSQL is running (Docker)
   - Verify DATABASE_URL environment variable
   - Run migrations: `docker-compose exec web python manage.py migrate`

4. **Image processing errors**: 
   - Check file permissions in MEDIA_ROOT
   - Verify XML feed accessibility
   - Check disk space for output images

### Performance Tips
- **Docker Resources**: Allocate sufficient CPU and memory
- **Redis Configuration**: Tune Redis memory settings for large feeds
- **Image Processing**: Consider image size limits for better performance
- **WebSocket Connections**: Monitor connection count in production
- **Celery Workers**: Scale workers based on processing load

## 📊 Monitoring & Logs

### Docker Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web
docker-compose logs -f celery
docker-compose logs -f db
docker-compose logs -f redis
```

### Application Logs
- **Django Logs**: Available in container logs
- **Celery Logs**: Available in container logs
- **PostgreSQL Logs**: Available via `docker-compose logs db`
- **Redis Logs**: Available via `docker-compose logs redis`

### Health Monitoring
- **Application**: http://localhost:8000/
- **Database Health**: `docker-compose exec db pg_isready`
- **Redis Health**: `docker-compose exec redis redis-cli ping`

## 🔒 Security Notes

- **Environment Variables**: Never commit `.env` files to version control
- **Database Passwords**: Use strong passwords in production
- **Secret Key**: Generate new secret key for production
- **HTTPS**: Enable SSL/TLS in production
- **WebSocket Authentication**: Users must be logged in
- **Frame Ownership**: Users can only access their own frames
- **CSRF Protection**: Enabled for all HTTP requests
- **File Upload**: Limited to image files only
