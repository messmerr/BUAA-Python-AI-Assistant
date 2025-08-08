# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered Teaching Assistant System developed as a Python summer course project. The system is a full-stack application that helps teachers with assignment grading, Q&A, and provides intelligent tutoring for students.

**Tech Stack:**
- **Frontend**: Vue 3 + TypeScript + Element Plus + Pinia + Vue Router + Vite
- **Backend**: Django 5.2.4 + Django REST Framework + SQLite
- **AI Integration**: Google Generative AI API
- **Authentication**: JWT with djangorestframework-simplejwt

## Development Commands

### Backend (Django)
```bash
cd backend

# Environment setup
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt

# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # optional

# Development server
python manage.py runserver     # http://127.0.0.1:8000
```

### Frontend (Vue 3)
```bash
cd frontend

# Install dependencies
npm install

# Development
npm run dev                    # http://localhost:5173
npm run build                  # production build
npm run preview                # preview production build

# Code quality
npm run lint                   # ESLint with auto-fix
npm run type-check             # TypeScript type checking
npm run format                 # Prettier formatting
npm run test:unit              # Vitest unit tests
```

## Project Architecture

### Backend Structure
The Django backend follows a modular app-based architecture:

- **ai_tutor_system/**: Main Django project configuration
- **accounts/**: User authentication and management (teachers/students)
- **assignments/**: Assignment creation, submission, and grading system
- **qa/**: Q&A system for student questions and AI responses
- **chat/**: Real-time communication between students and teachers
- **reports/**: Learning progress reports and analytics
- **ai_services.py**: AI integration service using Google Generative AI

### Frontend Structure
Vue 3 application with TypeScript and composition API:

- **src/views/**: Page-level components organized by feature
- **src/components/**: Reusable UI components
- **src/stores/**: Pinia state management stores
- **src/api/**: API client modules for backend communication
- **src/router/**: Vue Router configuration with auth guards
- **src/types/**: TypeScript type definitions

### Key Features
1. **Assignment System**: Text and image-based assignment submissions with OCR support
2. **AI Grading**: Automatic grading using AI with customizable rubrics
3. **Intelligent Q&A**: NLP-powered question answering system
4. **Learning Analytics**: Progress tracking and report generation
5. **Real-time Chat**: Communication between students and teachers
6. **Role-based Access**: Separate interfaces for teachers and students

## API Documentation
- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **API Schema**: http://127.0.0.1:8000/api/schema/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Environment Configuration

Create `.env` file in `backend/` directory with:
```
GOOGLE_AI_API_KEY=your_google_ai_api_key
SECRET_KEY=your_django_secret_key
DEBUG=True
```

## Testing

Backend tests are located in `backend/tests/` directory. Run specific test files:
```bash
cd backend
python manage.py test tests.test_api
python manage.py test tests.test_assignment_filters
```

Frontend tests use Vitest:
```bash
cd frontend
npm run test:unit
```

## Important Notes

- The system uses JWT authentication with automatic token refresh
- Image uploads are handled through Django's media files system
- AI services require Google Generative AI API key configuration
- CORS is configured for local development (frontend on 5173, backend on 8000)
- Database migrations should be run after any model changes
- The project includes OCR functionality for image-based assignment submissions