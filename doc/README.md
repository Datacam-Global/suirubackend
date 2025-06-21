# Project Documentation: SuiRu Backend

## Overview
This project is a Django-based backend for the SuiRu platform. It provides RESTful APIs, user authentication, content management, and monitoring features. The backend interacts with a SQLite database and supports modular app development.

## Project Structure
- **manage.py**: Django's command-line utility for administrative tasks.
- **requirements.txt**: Lists Python dependencies.
- **db.sqlite3**: SQLite database file.
- **core/**: Contains core Django app logic, models, serializers, and views.
- **monitoring/**: Handles monitoring, verification, and data management.
- **reportsuspeciouscontent/**: Manages reporting and handling of suspicious content.
- **sui_ru_main/**: Main Django project settings, URLs, and WSGI/ASGI configuration.
- **media/**: Stores uploaded media files.
- **static/**, **staticfiles/**: Static assets for the project.

## Key Features
- User authentication and profile management
- Facebook API integration and data handling
- Suspicious content reporting and verification
- Modular app structure for scalability
- REST API endpoints for frontend consumption

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Apply migrations:
   ```bash
   python manage.py migrate
   ```
3. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Development Guidelines
- Follow Django best practices for app and model structure.
- Write tests for new features in the respective app's `tests.py`.
- Use serializers for API data validation and transformation.
- Store sensitive information in environment variables or Django settings.

## Contributing
1. Fork the repository and create a new branch for your feature or bugfix.
2. Write clear, concise commit messages.
3. Ensure all tests pass before submitting a pull request.

## License
This project is licensed under the MIT License.

---
For detailed API documentation and further information, see additional files in this `doc/` folder as the project evolves.
