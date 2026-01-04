# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django-based karate dojo management platform that handles student enrollment, training schedules, attendance tracking, kata/kumite library, and user management. The project uses Docker for containerization with PostgreSQL as the database.

## Development Setup

### Docker Environment (Recommended)

**PowerShell (Windows):**
```sh
docker-compose --env-file .env_local -f docker-compose-local.yml up -d
```

**Linux/Mac:**
```sh
chmod 755 dojo/entrypoint_local.sh
docker-compose --env-file .env_local -f docker-compose-local.yml up -d
```

**Rebuild containers after updates:**
```sh
docker compose --env-file .env_local -f docker-compose-local.yml down -v
docker rm nginx
docker rm kapp_web_local
docker compose --env-file .env_local -f docker-compose-local.yml build nginx
docker compose --env-file .env_local -f docker-compose-local.yml build kapp_web_local
docker-compose --env-file .env_local -f docker-compose-local.yml up -d
```

### Django Management Commands

All Django commands should be run from the `dojo/` directory:

```sh
cd dojo
python manage.py <command>
```

**Common Commands:**
- `python manage.py runserver` - Run development server (port 8000)
- `python manage.py makemigrations` - Create database migrations
- `python manage.py migrate` - Apply database migrations
- `python manage.py collectstatic` - Collect static files
- `python manage.py createsuperuser` - Create admin user
- `python manage.py create_test_data` - Load test/dummy data
- `python manage.py load_library_data` - Load kata/kumite library data
- `python manage.py cleanup_expired_tokens` - Remove expired tokens

## Architecture

### Project Structure

```
karate_site/
├── dojo/                          # Main Django project directory
│   ├── dojo/                      # Project settings and configuration
│   │   ├── settings.py            # Main settings (uses python-decouple for env vars)
│   │   ├── urls.py                # Root URL configuration
│   │   ├── views.py               # Landing page and error handlers
│   │   └── middlewares.py         # Custom middleware (ClearMessagesIfLoggedOutMiddleware)
│   ├── user_management/           # User authentication and management app
│   ├── dashboard/                 # Main dashboard app for students and sensei
│   ├── test/                      # Test data generation and fixtures
│   ├── utils/                     # Shared utilities
│   │   ├── config_vars.py         # Belt rank definitions (Ranges)
│   │   ├── utils.py               # Helper functions
│   │   └── widgets.py             # Custom form widgets
│   ├── templates/                 # HTML templates
│   ├── static/                    # Static files (CSS, JS, images)
│   ├── media/                     # User-uploaded files
│   └── manage.py                  # Django management script
├── nginx/                         # Nginx configuration for production
├── docker-compose-local.yml       # Local development Docker setup
├── docker-compose-release.yml     # Production Docker setup
└── .env_local                     # Local environment variables
```

### Django Apps

**user_management:**
- Custom User model (AUTH_USER_MODEL = 'user_management.User')
- Uses `id_number` as USERNAME_FIELD instead of email/username
- Token-based signup and password recovery
- User categories: SENSEI, SEMPAI, STUDENT
- UserDocument model for storing user-related files
- Management command: `cleanup_expired_tokens`

**dashboard:**
- Dual interface: student dashboard and sensei (instructor) dashboard
- URL routing splits at `/dashboard/` and `/dashboard/student/`
- Models:
  - **Dojo**: Represents the dojo with sensei and students
  - **Kata**: Kata forms with levels, embusen diagrams, and video references
  - **KataSerie**: Groups related katas
  - **KataLesson**: Individual lessons for each kata
  - **KataLessonActivity**: Activities within lessons with images/videos
  - **Kumite**: Kumite types (ippon, sanbon, jiyu, etc.)
  - **Technique**: Training techniques categorized by type (JOINT, STRETCH, KIHON, KATA, KUMITE)
  - **Training**: Training sessions with date, type, status, and techniques
  - **TrainingScheduling**: Automatic recurring training schedules by day/time
  - **Attendance**: Student attendance records for each training

**test:**
- Contains management commands for generating test data
- `create_test_data`: Generates dummy users, dojos, trainings, etc.
- `load_library_data`: Loads kata/kumite library from YAML files in utils/library_data/

### Key Patterns

**Custom User Model:**
The project uses a custom User model with `id_number` as the unique identifier. When creating users programmatically:
```python
from user_management.models import User
user = User.objects.create_user(
    id_number='12345',
    password='password',
    first_name='John',
    last_name='Doe',
    email='john@example.com'
)
```

**Video URL Embedding:**
The `KataLessonActivityVideo` model has an `embed_url` property that converts YouTube and Google Drive URLs to embeddable formats. Always use this property when rendering videos.

**KataLesson JSONFields:**
The `KataLesson` model uses JSONField for `objectives` and `content` to store lists of strings. When creating or updating KataLesson instances:
```python
from dashboard.models import KataLesson

# Create a lesson with objectives and content as lists
lesson = KataLesson.objects.create(
    kata=kata_instance,
    title="Basic Stances",
    objectives=["Learn zenkutsu-dachi", "Practice kokutsu-dachi", "Understand weight distribution"],
    content=["Demonstrate front stance", "Hold position for 30 seconds", "Practice transitions"],
    order='b1'
)

# Update existing lesson
lesson.objectives.append("Master stance transitions")
lesson.save()

# Access individual items
for objective in lesson.objectives:
    print(objective)
```

**Token-Based Registration:**
- Registration requires a signup token
- Tokens have expiration times
- URL pattern: `/signup/<str:token>/`
- Password recovery: `/recover-password/<str:token>/`

**Training Scheduling:**
TrainingScheduling creates recurring training sessions. The system distinguishes between scheduled trainings (from TrainingScheduling) and one-off Training instances.

**Middleware:**
`ClearMessagesIfLoggedOutMiddleware` clears Django messages when users log out to prevent message leakage.

### Configuration

**Environment Variables (python-decouple):**
All sensitive configuration is loaded from environment files using `decouple.config()`:
- Database: `DOJO_ENGINE`, `DOJO_DB_NAME`, `DOJO_DB_USER`, `DOJO_DB_PASS`, `DOJO_DB_HOST`, `DOJO_DB_PORT`
- Django: `DJANGO_SECRET_KEY`, `DEBUG`, `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`
- Email: `DOJO_EMAIL_HOST`, `DOJO_EMAIL_PORT`, `DOJO_EMAIL_HOST_USER`, `DOJO_EMAIL_HOST_PASSWORD`
- Admin: `ALLOW_ADMIN` (enables /admin/ even in production)

**Static Files:**
- Uses WhiteNoise for serving static files
- `STATIC_URL = "static/"`
- `STATIC_ROOT = BASE_DIR / "staticfiles"`
- Run `collectstatic` before production deployment

**Media Files:**
- `MEDIA_URL = '/media/'`
- `MEDIA_ROOT = BASE_DIR / 'media'`
- User documents stored at: `users/{id_number}/documents/{filename}`

**Sessions:**
- Session expires when browser closes (`SESSION_EXPIRE_AT_BROWSER_CLOSE = True`)
- Session timeout: 30 minutes (1800 seconds)

### Templates

Uses AdminLTE 3.2.0 for the admin interface. Base templates:
- `base-login.html`: Login/registration pages
- `base-user.html`: Authenticated user pages
- Templates organized by app in subdirectories

### URL Routing

```
/                          - Landing page
/login/                    - Login
/signup/<token>/           - Registration
/forgot-password/          - Password recovery request
/recover-password/<token>/ - Password reset
/dashboard/                - Sensei dashboard (includes all management views)
/dashboard/student/        - Student dashboard
/dashboard/library/        - Kata/Kumite library
/admin/                    - Django admin (only if DEBUG=True or ALLOW_ADMIN=True)
```

## Database

**PostgreSQL** is used in both local and production environments via Docker.

**Migrations:**
Always create migrations when modifying models:
```sh
python manage.py makemigrations
python manage.py migrate
```

**Important Model Constraints:**
- `Dojo.sensei` must have `category='SENSEI'` (enforced in model's `clean()` method)
- `Training.date` is unique
- `TrainingScheduling` has unique constraint on (`day_of_week`, `time`)
- `Attendance` has unique constraint on (`training`, `student`)

## Testing

The project uses Django's testing framework. Tests are located in each app's `tests.py` file.

Run tests:
```sh
python manage.py test
```

User management app has extensive tests in `user_management/tests.py`.

## Deployment Notes

- Production uses gunicorn as WSGI server
- Nginx serves as reverse proxy (configured in `nginx/`)
- Docker images can be pushed to Docker Hub (see README.md)
- Use ngrok for local HTTPS testing: `ngrok http 8000`
- For SSL testing locally: install django-sslserver and use `python manage.py runsslserver`

## Important Development Notes

- Admin interface is conditionally enabled based on `DEBUG` or `ALLOW_ADMIN` settings
- Logging configuration differs between DEBUG and production (see settings.py:175-239)
- Timezone: `America/Bogota`
- The entrypoint script automatically runs migrations and loads test data in local development
