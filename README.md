# Django Image Processing & Feed Management Application

This project is a Django-based image processing and feed management application. The main purpose of the project is to automatically add frames to products in XML feeds.

## 🚀 Features

- **User Authentication**: Django built-in authentication system
- **Frame Management**: Upload and manage frame templates
- **XML Feed Processing**: Automatic feed parsing and product image fetching
- **Coordinate Configuration**: Interactive product positioning in preview screen
- **Bulk Image Generation**: Background processing with Celery
- **DataTable Management**: Server-side pagination and search functionality
- **Image Download/Delete**: Manage generated outputs
- **Frame CRUD Operations**: Create, read, update, delete frames
- **Real-time Preview**: Interactive coordinate adjustment with drag & resize

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7
- **Image Processing**: Pillow (PIL)
- **Background Jobs**: Celery + Redis
- **Frontend**: Bootstrap 5, jQuery, DataTables
- **Database**: SQLite (for development)

## 📋 Installation

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
`.env` file is already available. Edit if necessary:
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

### 7. Start Redis Server
```bash
# Windows (Redis for Windows required)
redis-server
# Linux/Mac
sudo service redis-server start
```

### 8. Start Celery Worker
Open new terminal:
```bash
cd django_app
venv\Scripts\activate  # Windows
celery -A project worker --loglevel=info
```

### 9. Start Django Server
```bash
python manage.py runserver
```

## 🎯 Usage

### 1. System Access
- Go to `http://127.0.0.1:8000/`
- Register or login

### 2. Adding New Frame
- Click "Add New Frame" button
- Enter frame name
- Upload frame image (JPG/PNG)
- Enter XML Feed URL: `https://cdn.goanalytix.io/assets/casestudy/CaseStudyFeed.xml`

### 3. Coordinate Configuration
- Adjust product image position in preview screen
- Set X, Y coordinates and dimensions
- See result with real-time preview
- Save with "Save & Generate Images"

### 4. Bulk Processing
- System automatically applies frame to all feed products
- Performant processing with background processing
- Progress can be tracked

### 5. Output Management
- View generated images on Frame Details page
- Search and pagination with DataTable
- Download and delete operations

### 6. Frame Management
- Edit frame information and settings
- Delete frames with confirmation
- View frame statistics and status

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
│   ├── tasks.py          # Celery tasks
│   ├── utils.py          # Helper functions
│   └── forms.py          # Django forms
│
├── project/              # Django project settings
│   ├── settings.py       # Main settings
│   ├── urls.py          # URL routing
│   └── celery.py        # Celery configuration
│
├── requirements.txt      # Python dependencies
├── manage.py            # Django management script
└── README.md            # This file
```

## 🔧 API Endpoints

- `/` - Home page (Frame list)
- `/login/` - User login
- `/register/` - User registration
- `/add-frame/` - Add new frame
- `/frame/<id>/preview/` - Coordinate configuration
- `/frame/<id>/edit/` - Edit frame
- `/frame/<id>/delete/` - Delete frame
- `/frame_detail/<id>/` - Frame details
- `/frame/<id>/outputs-ajax/` - DataTable AJAX
- `/delete_output/<id>/` - Delete output

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

1. **Redis Connection**: Redis server must be active for Celery to work
2. **File Sizes**: Large images may increase processing time
3. **Feed Access**: XML feed URLs must be accessible
4. **Media Directory**: `media/` folder must have write permissions
5. **Duplicate Handling**: System handles duplicate product IDs automatically

## 🔧 Development Notes

- **Debug Mode**: Set `DEBUG=False` in production
- **Database**: PostgreSQL recommended for production
- **Static Files**: Use Nginx/Apache in production
- **Logging**: Detailed logs in `django_frame.log` file

## 🆕 Recent Updates

- Added frame edit and delete functionality
- Implemented interactive coordinate adjustment
- Added Bootstrap styling throughout the application
- Enhanced error handling and user feedback
- Improved duplicate product ID handling
- Added comprehensive form validation

## 📝 License

This project is prepared for educational purposes.

## 🤝 Contributing

1. Fork the project
2. Create feature branch
3. Commit your changes
4. Send pull request

## 📞 Support

You can open an issue for any questions.
