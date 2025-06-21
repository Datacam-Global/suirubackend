# API Reference

This document provides an overview of the main API endpoints exposed by the SuiRu Backend. All endpoints follow RESTful conventions and return JSON responses.

## Authentication
- **POST /api/auth/login/**: User login
- **POST /api/auth/register/**: User registration
- **POST /api/auth/logout/**: User logout

## User Management
- **GET /api/users/profile/**: Retrieve user profile
- **PUT /api/users/profile/**: Update user profile

## Facebook Integration
- **GET /api/facebook/data/**: Fetch Facebook data
- **POST /api/facebook/post/**: Create a Facebook post

## Suspicious Content Reporting
- **POST /api/reports/**: Report suspicious content
- **GET /api/reports/**: List all reports
- **GET /api/reports/{id}/**: Retrieve a specific report

## Monitoring
- **GET /api/monitoring/status/**: Get system status
- **GET /api/monitoring/logs/**: Retrieve monitoring logs

---

For more details on request/response formats, authentication, and error handling, see the main `README.md` and the codebase documentation.
