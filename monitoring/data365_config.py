# Data365 API Configuration
# This file will contain the configuration for the actual Data365 API integration

# API Settings
DATA365_API_BASE_URL = 'https://api.data365.com'  # Replace with actual Data365 API URL
DATA365_API_KEY = ''  # Will be set from environment variable
DATA365_API_VERSION = 'v1'

# Facebook API specific settings
FACEBOOK_DATA365_ENDPOINT = '/facebook/posts'
FACEBOOK_COUNTRY_FILTER = 'cameroon'  # Country filter for posts

# Rate limiting
API_RATE_LIMIT_PER_MINUTE = 60
API_RATE_LIMIT_PER_HOUR = 1000

# Caching settings
CACHE_FACEBOOK_POSTS = True
CACHE_DURATION_MINUTES = 15

# Development settings (temporary)
USE_JSON_DATA_SOURCE = True  # Set to False when using real API
JSON_DATA_FILE = 'facebook_data.json'

# When ready to switch to real API:
# 1. Set USE_JSON_DATA_SOURCE = False
# 2. Set DATA365_API_KEY in environment variables
# 3. Update DATA365_API_BASE_URL with the real API URL
# 4. The fetch_facebook_data_from_api function will automatically use the real API
