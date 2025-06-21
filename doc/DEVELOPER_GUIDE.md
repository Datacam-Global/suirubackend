# Developer Guide

## Setting Up the Development Environment
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd suirubackend
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply migrations and run the server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Code Structure
- **core/**: Core business logic, models, and serializers
- **monitoring/**: Monitoring, verification, and data management
- **reportsuspeciouscontent/**: Suspicious content reporting
- **sui_ru_main/**: Project settings and configuration

## Testing
- Write tests in each app's `tests.py` file.
- Run all tests with:
  ```bash
  python manage.py test
  ```

## Adding New Apps
1. Create a new app:
   ```bash
   python manage.py startapp <appname>
   ```
2. Register the app in `sui_ru_main/settings.py` under `INSTALLED_APPS`.

## Code Style
- Follow PEP8 guidelines.
- Use descriptive commit messages.
- Document new modules and functions.

---
For more information, see the main `README.md` and `API_REFERENCE.md` in the `doc/` folder.
