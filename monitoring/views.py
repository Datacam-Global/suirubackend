from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import random
import json
import os
from datetime import datetime, timedelta
from django.conf import settings
from .data365_config import USE_JSON_DATA_SOURCE, JSON_DATA_FILE
from .models import (
    Alert, Report, ContentAnalysis, GeographicData,
    PlatformAnalytics, ChatMessage, UserSettings, FacebookPost
)
from .serializers import (
    UserSerializer, AlertSerializer, ReportSerializer,
    ContentAnalysisSerializer, GeographicDataSerializer,
    PlatformAnalyticsSerializer, ChatMessageSerializer,
    UserSettingsSerializer, FacebookPostSerializer, FacebookAPIResponseSerializer
)
import google.generativeai as genai
import openai
import requests

# Create your views here.

def load_facebook_data():
    """
    Load Facebook data from JSON file (temporary - will be replaced with Data365 API calls)
    """
    json_file_path = os.path.join(
        os.path.dirname(__file__), 
        'data', 
        JSON_DATA_FILE
    )
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data['cameroon_posts']
    except FileNotFoundError:
        # Fallback if JSON file not found
        return []
    except Exception as e:
        print(f"Error loading Facebook data: {e}")
        return []

def save_post_to_database(post_data):
    """
    Save a Facebook post to the database
    This simulates the behavior when receiving data from Data365 API
    After saving, send relevant fields to the model API for analysis.
    """
    post_id = post_data.get('id')

    # Check if post already exists
    if FacebookPost.objects.filter(post_id=post_id).exists():
        return FacebookPost.objects.get(post_id=post_id)

    # Create new post
    facebook_post = FacebookPost.objects.create(
        post_id=post_data.get('id', ''),
        created_time=post_data.get('created_time', ''),
        timestamp=post_data.get('timestamp', 0),
        post_type=post_data.get('post_type', ''),
        text=post_data.get('text', ''),
        text_lang=post_data.get('text_lang', ''),
        text_tagged_users=post_data.get('text_tagged_users', []),
        text_tags=post_data.get('text_tags', []),
        attached_link=post_data.get('attached_link', ''),
        attached_link_description=post_data.get('attached_link_description', ''),
        attached_image_url=post_data.get('attached_image_url', ''),
        attached_image_url_s3=post_data.get('attached_image_url_s3', ''),
        attached_image_content=post_data.get('attached_image_content', ''),
        attached_medias_id=post_data.get('attached_medias_id', []),
        attached_medias_preview_url=post_data.get('attached_medias_preview_url', []),
        attached_medias_preview_url_s3=post_data.get('attached_medias_preview_url_s3', ''),
        attached_medias_preview_content=post_data.get('attached_medias_preview_content', []),
        attached_post_id=post_data.get('attached_post_id', ''),
        attached_video_preview_url=post_data.get('attached_video_preview_url', ''),
        attached_video_preview_url_s3=post_data.get('attached_video_preview_url_s3', ''),
        attached_video_url=post_data.get('attached_video_url', ''),
        post_screenshot=post_data.get('post_screenshot', ''),
        reactions_like_count=post_data.get('reactions_like_count', 0),
        reactions_love_count=post_data.get('reactions_love_count', 0),
        reactions_haha_count=post_data.get('reactions_haha_count', 0),
        reactions_wow_count=post_data.get('reactions_wow_count', 0),
        reactions_sad_count=post_data.get('reactions_sad_count', 0),
        reactions_angry_count=post_data.get('reactions_angry_count', 0),
        reactions_support_count=post_data.get('reactions_support_count', 0),
        reactions_total_count=post_data.get('reactions_total_count', 0),
        comments_count=post_data.get('comments_count', 0),
        shares_count=post_data.get('shares_count', 0),
        video_view_count=post_data.get('video_view_count', 0),
        video_duration=post_data.get('video_duration', 0),
        overlay_text=post_data.get('overlay_text', ''),
        fact_checks=post_data.get('fact_checks', []),
        owner_id=post_data.get('owner_id', ''),
        owner_username=post_data.get('owner_username', ''),
        owner_full_name=post_data.get('owner_full_name', ''),
        group_id=post_data.get('group_id', ''),
        recommends=post_data.get('recommends', False),
        tagged_location_id=post_data.get('tagged_location_id', ''),
        post_location_id=post_data.get('post_location_id', ''),
    )

    # --- Send to model API for analysis ---
    try:
        from monitoring.model_client import analyze_hate, analyze_misinformation
        from .models import ContentModelAnalysis, Alert
        
        content = post_data.get('text', '')
        # Only send if content is not empty
        if content.strip():
            # Send content to hate speech analysis endpoint
            hate_result = analyze_hate(content)
            print(f"Analysis for post {post_id}:\n  Hate: {hate_result}")
            
            # Save hate speech analysis result
            if 'error' not in hate_result:
                # Create ContentModelAnalysis record for hate speech
                hate_analysis = ContentModelAnalysis.objects.create(
                    post=facebook_post,
                    analysis_type='hate',
                    is_harmful=hate_result.get('is_hate_speech', False),
                    confidence=hate_result.get('confidence'),
                    severity=hate_result.get('severity'),
                    category=hate_result.get('category'),
                    explanation=hate_result.get('explanation', ''),
                    detected_keywords=hate_result.get('detected_keywords', []),
                    raw_response=hate_result
                )
                
                # If harmful content detected with high confidence, create an alert
                if hate_analysis.is_harmful and hate_analysis.confidence and hate_analysis.confidence > 0.7:
                    Alert.objects.create(
                        title=f"Hate Speech Detected in Post {post_id}",
                        description=f"Hate speech detected with {hate_analysis.confidence:.2f} confidence. Severity: {hate_analysis.severity}.",
                        severity='high' if hate_analysis.severity == 'high' else 'medium',
                        source='Model API - Hate Speech',
                        status='new'
                    )
            
            # Send content to misinformation analysis endpoint
            misinformation_result = analyze_misinformation(content)
            print(f"Analysis for post {post_id}:\n  Misinformation: {misinformation_result}")
            
            # Save misinformation analysis result
            if 'error' not in misinformation_result:
                # Create ContentModelAnalysis record for misinformation
                misinfo_analysis = ContentModelAnalysis.objects.create(
                    post=facebook_post,
                    analysis_type='misinformation',
                    is_harmful=misinformation_result.get('label') == 'misinformation',
                    confidence=misinformation_result.get('confidence'),
                    severity=misinformation_result.get('severity'),
                    explanation=misinformation_result.get('explanation', ''),
                    raw_response=misinformation_result
                )
                
                # If misinformation detected with high confidence, create an alert
                if misinfo_analysis.is_harmful and misinfo_analysis.confidence and misinfo_analysis.confidence > 0.7:
                    Alert.objects.create(
                        title=f"Misinformation Detected in Post {post_id}",
                        description=f"Misinformation detected with {misinfo_analysis.confidence:.2f} confidence. Severity: {misinfo_analysis.severity}.",
                        severity='high' if misinfo_analysis.severity == 'high' else 'medium',
                        source='Model API - Misinformation',
                        status='new'
                    )
    except Exception as e:
        print(f"Error processing model analysis for post {post_id}: {e}")

    return facebook_post

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    
    list:
    Return a list of all users.
    
    retrieve:
    Return the details of a specific user.
    
    create:
    Create a new user.
    
    update:
    Update all fields of a user.
    
    partial_update:
    Update one or more fields of a user.
    
    destroy:
    Delete a user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

class AlertViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing alerts.
    
    list:
    Return a list of all alerts assigned to the current user.
    
    retrieve:
    Return the details of a specific alert.
    
    create:
    Create a new alert.
    
    update:
    Update all fields of an alert.
    
    partial_update:
    Update one or more fields of an alert.
    
    destroy:
    Delete an alert.
    """
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(assigned_to=self.request.user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update the status of an alert.
        
        Parameters:
        - status: string (new, in_progress, resolved, closed)
        
        Returns:
        - 200: Alert status updated successfully
        - 400: Invalid status provided
        """
        alert = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Alert.STATUS_CHOICES):
            alert.status = new_status
            alert.save()
            return Response({'status': 'success'})
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)

class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing reports.
    
    list:
    Return a list of all reports created by the current user.
    
    retrieve:
    Return the details of a specific report.
    
    create:
    Create a new report.
    
    update:
    Update all fields of a report.
    
    partial_update:
    Update one or more fields of a report.
    
    destroy:
    Delete a report.
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ContentAnalysisViewSet(viewsets.ModelViewSet):
    """
    API endpoint for content analysis.
    
    list:
    Return a list of all content analyses.
    
    retrieve:
    Return the details of a specific content analysis.
    
    create:
    Create a new content analysis.
    
    update:
    Update all fields of a content analysis.
    
    partial_update:
    Update one or more fields of a content analysis.
    
    destroy:
    Delete a content analysis.
    """
    queryset = ContentAnalysis.objects.all()
    serializer_class = ContentAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def analyze_content(self, request):
        """
        Analyze content and return results.
        
        Parameters:
        - content_url: string (URL of the content to analyze)
        - content_type: string (Type of content: text, image, video)
        
        Returns:
        - 200: Content analysis completed successfully
        - 400: Invalid content provided
        """
        # Implement content analysis logic here
        return Response({'status': 'success'})

class GeographicDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint for geographic data.
    
    list:
    Return a list of all geographic data points.
    
    retrieve:
    Return the details of a specific geographic data point.
    
    create:
    Create a new geographic data point.
    
    update:
    Update all fields of a geographic data point.
    
    partial_update:
    Update one or more fields of a geographic data point.
    
    destroy:
    Delete a geographic data point.
    """
    queryset = GeographicData.objects.all()
    serializer_class = GeographicDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_heatmap_data(self, request):
        """
        Get heatmap data for visualization.
        
        Returns:
        - 200: Heatmap data retrieved successfully
        """
        # Implement heatmap data aggregation logic here
        return Response({'status': 'success'})

class PlatformAnalyticsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for platform analytics.
    
    list:
    Return a list of all platform analytics.
    
    retrieve:
    Return the details of specific platform analytics.
    
    create:
    Create new platform analytics.
    
    update:
    Update all fields of platform analytics.
    
    partial_update:
    Update one or more fields of platform analytics.
    
    destroy:
    Delete platform analytics.
    """
    queryset = PlatformAnalytics.objects.all()
    serializer_class = PlatformAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_dashboard_metrics(self, request):
        """
        Get dashboard metrics.
        
        Returns:
        - 200: Dashboard metrics retrieved successfully
        """
        # Implement dashboard metrics aggregation logic here
        return Response({'status': 'success'})

class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for chat messages.
    
    list:
    Return a list of all chat messages for the current user.
    
    retrieve:
    Return the details of a specific chat message.
    
    create:
    Create a new chat message.
    
    update:
    Update all fields of a chat message.
    
    partial_update:
    Update one or more fields of a chat message.
    
    destroy:
    Delete a chat message.
    """
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """
        Send a message and get bot response.
        
        Parameters:
        - message: string (Message to send)
        
        Returns:
        - 200: Message sent and response received successfully
        - 400: Invalid message provided
        """
        message = request.data.get('message')
        if message:
            chat_message = ChatMessage.objects.create(
                user=self.request.user,
                message=message,
                is_bot=False
            )
            # Implement bot response logic here
            bot_response = ChatMessage.objects.create(
                user=self.request.user,
                message="Bot response placeholder",
                is_bot=True
            )
            return Response({
                'user_message': ChatMessageSerializer(chat_message).data,
                'bot_response': ChatMessageSerializer(bot_response).data
            })
        return Response({'status': 'error'}, status=status.HTTP_400_BAD_REQUEST)

class UserSettingsViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user settings.
    
    list:
    Return a list of all user settings for the current user.
    
    retrieve:
    Return the details of specific user settings.
    
    create:
    Create new user settings.
    
    update:
    Update all fields of user settings.
    
    partial_update:
    Update one or more fields of user settings.
    
    destroy:
    Delete user settings.
    """
    queryset = UserSettings.objects.all()
    serializer_class = UserSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSettings.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FacebookPostViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Facebook posts from Data365 integration
    """
    queryset = FacebookPost.objects.all()
    serializer_class = FacebookPostSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def facebook_api_data(request):
    """
    Facebook API endpoint with data for Cameroon
    Simulates Data365 API response format
    Loads data from JSON file and saves to database when queried
    """
    
    # Load data from JSON file (will be replaced with Data365 API call)
    posts_data = fetch_facebook_data_from_api(limit=1)
    
    if not posts_data:
        return Response({
            "data": None,
            "error": "No data available",
            "status": "error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Get the first (and only) post
    selected_post_data = posts_data[0] if isinstance(posts_data, list) else posts_data
    
    # Add some randomization to make it feel more "real-time"
    current_time = datetime.now()
    selected_post_data['created_time'] = current_time.strftime("%Y-%m-%dT%H:%M:%S")
    selected_post_data['timestamp'] = int(current_time.timestamp())
    
    # Add some random variation to engagement metrics
    selected_post_data['reactions_like_count'] += random.randint(-10, 50)
    selected_post_data['reactions_love_count'] += random.randint(-5, 20)
    selected_post_data['comments_count'] += random.randint(-5, 30)
    selected_post_data['shares_count'] += random.randint(-2, 15)
    
    # Ensure non-negative values
    for key in ['reactions_like_count', 'reactions_love_count', 'comments_count', 'shares_count']:
        if selected_post_data[key] < 0:
            selected_post_data[key] = 0
    
    # Recalculate total reactions
    total_reactions = (
        selected_post_data['reactions_like_count'] +
        selected_post_data['reactions_love_count'] +
        selected_post_data['reactions_haha_count'] +
        selected_post_data['reactions_wow_count'] +
        selected_post_data['reactions_sad_count'] +
        selected_post_data['reactions_angry_count'] +
        selected_post_data['reactions_support_count']
    )
    selected_post_data['reactions_total_count'] = total_reactions
    
    # Save to database (simulating external API call behavior)
    try:
        facebook_post = save_post_to_database(selected_post_data)
        print(f"Saved Facebook post {facebook_post.post_id} to database")
    except Exception as e:
        print(f"Error saving post to database: {e}")
    
    # Construct response in Data365 format
    response_data = {
        "data": selected_post_data,
        "error": None,
        "status": "ok"
    }
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def facebook_api_posts_list(request):
    """
    Get multiple Facebook posts for Cameroon
    Loads data from JSON file and saves to database when queried
    """
    
    # Get number of posts to return (default 5, max 10)
    limit = min(int(request.GET.get('limit', 5)), 10)
    
    # Load data from JSON file (will be replaced with Data365 API call)
    posts_data = fetch_facebook_data_from_api(limit=limit)
    
    if not posts_data:
        return Response({
            "data": [],
            "error": "No data available",
            "status": "error",
            "count": 0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Ensure posts_data is a list
    if not isinstance(posts_data, list):
        posts_data = [posts_data]
    
    # Process each post
    processed_posts = []
    current_time = datetime.now()
    
    for i, post_data in enumerate(posts_data):
        # Create a copy to avoid modifying the original
        post_copy = post_data.copy()
        
        # Add some time variation (posts from different times)
        post_time = current_time - timedelta(hours=i*2, minutes=random.randint(0, 120))
        post_copy['created_time'] = post_time.strftime("%Y-%m-%dT%H:%M:%S")
        post_copy['timestamp'] = int(post_time.timestamp())
        
        # Make each post unique by modifying the ID slightly
        original_id = post_copy['id']
        post_copy['id'] = f"{original_id}_{int(post_time.timestamp())}"
        
        # Add some random variation to engagement metrics
        post_copy['reactions_like_count'] += random.randint(-20, 100)
        post_copy['reactions_love_count'] += random.randint(-10, 50)
        post_copy['reactions_haha_count'] += random.randint(-2, 10)
        post_copy['reactions_wow_count'] += random.randint(-5, 30)
        post_copy['reactions_sad_count'] += random.randint(-3, 15)
        post_copy['reactions_angry_count'] += random.randint(-2, 8)
        post_copy['reactions_support_count'] += random.randint(-10, 40)
        post_copy['comments_count'] += random.randint(-10, 60)
        post_copy['shares_count'] += random.randint(-5, 30)
        
        if post_copy.get('video_view_count', 0) > 0:
            post_copy['video_view_count'] += random.randint(-100, 500)
        
        # Ensure non-negative values
        for key in ['reactions_like_count', 'reactions_love_count', 'reactions_haha_count', 
                   'reactions_wow_count', 'reactions_sad_count', 'reactions_angry_count', 
                   'reactions_support_count', 'comments_count', 'shares_count', 'video_view_count']:
            if post_copy.get(key, 0) < 0:
                post_copy[key] = 0
        
        # Recalculate total reactions
        total_reactions = (
            post_copy['reactions_like_count'] +
            post_copy['reactions_love_count'] +
            post_copy['reactions_haha_count'] +
            post_copy['reactions_wow_count'] +
            post_copy['reactions_sad_count'] +
            post_copy['reactions_angry_count'] +
            post_copy['reactions_support_count']
        )
        post_copy['reactions_total_count'] = total_reactions
        
        # Save to database (simulating external API call behavior)
        try:
            facebook_post = save_post_to_database(post_copy)
            print(f"Saved Facebook post {facebook_post.post_id} to database")
        except Exception as e:
            print(f"Error saving post {post_copy['id']} to database: {e}")
        
        processed_posts.append(post_copy)
    
    response_data = {
        "data": processed_posts,
        "error": None,
        "status": "ok",
        "count": len(processed_posts)
    }
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def facebook_saved_posts(request):
    """
    Get Facebook posts that have been saved to the database
    """
    
    # Get query parameters
    limit = min(int(request.GET.get('limit', 10)), 50)  # Max 50 posts
    offset = int(request.GET.get('offset', 0))
    
    # Get posts from database
    posts = FacebookPost.objects.all()[offset:offset+limit]
    total_count = FacebookPost.objects.count()
    
    # Serialize the posts
    serializer = FacebookPostSerializer(posts, many=True)
    
    response_data = {
        "data": serializer.data,
        "error": None,
        "status": "ok",
        "count": len(serializer.data),
        "total_count": total_count,
        "has_next": (offset + limit) < total_count
    }
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def facebook_clear_saved_posts(request):
    """
    Clear all saved Facebook posts from database (for testing purposes)
    """
    
    deleted_count = FacebookPost.objects.count()
    FacebookPost.objects.all().delete()
    
    response_data = {
        "message": f"Deleted {deleted_count} Facebook posts from database",
        "deleted_count": deleted_count,
        "error": None,
        "status": "ok"
    }
    
    return Response(response_data, status=status.HTTP_200_OK)

def fetch_facebook_data_from_api(post_id=None, limit=5):
    """
    Fetch Facebook data from Data365 API
    Currently loads from JSON file, will be replaced with actual API calls
    
    Args:
        post_id (str, optional): Specific post ID to fetch
        limit (int): Number of posts to fetch (for list requests)
    
    Returns:
        dict or list: Facebook post data in Data365 format
    """
    # TODO: Replace with actual Data365 API integration
    # For now, load from JSON file
    posts_data = load_facebook_data()
    
    if post_id:
        # Return specific post if post_id provided
        for post in posts_data:
            if post['id'] == post_id:
                return post
        return None
    else:
        # Return list of posts
        if len(posts_data) <= limit:
            return posts_data
        else:
            return random.sample(posts_data, limit)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def gemini_ask(request):
    """
    Send a question to Google Gemini and return the response.
    Gemini is strictly instructed to only answer with information related to Cameroon.
    If the question is not about Cameroon, Gemini will politely refuse to answer.
    
    Instructions for Gemini:
    - Only provide information, facts, or context that is directly related to Cameroon (its people, history, geography, politics, culture, economy, news, etc.).
    - If the question is not about Cameroon, respond with a polite refusal such as: "Sorry, I can only answer questions related to Cameroon."
    - If the question is ambiguous, ask the user to clarify how it relates to Cameroon.
    - Never provide information about other countries, regions, or topics unless it is directly connected to Cameroon.
    - Always keep answers concise, factual, and relevant to Cameroon.
    
    Parameters:
    - question: string (required)
    Returns:
    - 200: Gemini response
    - 400: Invalid input or Gemini error
    """
    question = request.data.get('question')
    if not question:
        return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)

    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        return Response({'error': 'Gemini API key not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        genai.configure(api_key=api_key)
        # Use a supported Gemini model for text generation
        # 'gemini-1.5-pro-latest' is generally available for text tasks
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        cameroon_instruction = (
            "You are an assistant that only provides information related to Cameroon. "
            "If the question is not about Cameroon, politely refuse to answer. "
            "If the question is ambiguous, ask the user to clarify how it relates to Cameroon. "
            "Never provide information about other countries, regions, or topics unless it is directly connected to Cameroon. "
            "Always keep answers concise, factual, and relevant to Cameroon."
        )
        full_prompt = f"{cameroon_instruction}\n\nUser question: {question}"
        response = model.generate_content(full_prompt)
        answer = response.text if hasattr(response, 'text') else str(response)
        return Response({'question': question, 'answer': answer}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def azure_openai_ask(request):
    """
    Send a question to Azure OpenAI and return the response.
    Only provides information related to Cameroon.
    Parameters:
    - question: string (required)
    Returns:
    - 200: Azure OpenAI response
    - 400: Invalid input or OpenAI error
    """
    question = request.data.get('question')
    if not question:
        return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)

    api_key = getattr(settings, 'AZURE_OPENAI_API_KEY', None)
    endpoint = getattr(settings, 'AZURE_OPENAI_ENDPOINT', None)
    deployment = getattr(settings, 'AZURE_OPENAI_DEPLOYMENT', None)
    api_version = getattr(settings, 'AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    if not api_key or not endpoint or not deployment:
        return Response({'error': 'Azure OpenAI configuration missing'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        # Use the new OpenAI v1 API for chat completions
        client = openai.AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        system_prompt = (
            "You are an assistant that only provides information related to Cameroon. "
            "If the question is not about Cameroon, politely refuse to answer. "
            "If the question is ambiguous, ask the user to clarify how it relates to Cameroon. "
            "Never provide information about other countries, regions, or topics unless it is directly connected to Cameroon. "
            "Always keep answers concise, factual, and relevant to Cameroon."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
            temperature=0.7,
            max_tokens=512
        )
        answer = response.choices[0].message.content
        return Response({'question': question, 'answer': answer}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def hate_speech_analyze(request):
    """
    Analyze text for hate speech using external FastAPI model.
    Expects JSON: {"text": "..."}
    Returns: FastAPI model response or error.
    """
    text = request.data.get("text")
    if not text:
        return Response({"error": "No text provided."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        api_url = "https://model.sui-ru.com/hate-speech/analyze"
        resp = requests.post(api_url, json={"text": text}, timeout=10)
        resp.raise_for_status()
        result = resp.json()
    except requests.RequestException as e:
        return Response({"error": "Model service unavailable.", "details": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(result, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def hate_speech_analyze_random_facebook_post(request):
    """
    Select a random Facebook post from facebook_data.json, send its text to the hate speech model, and return the result.
    """
    posts = load_facebook_data()
    if not posts:
        return Response({"error": "No Facebook data available."}, status=status.HTTP_404_NOT_FOUND)
    post = random.choice(posts)
    text = post.get("text", "")
    if not text:
        return Response({"error": "Selected post has no text."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        api_url = "https://model.sui-ru.com/hate-speech/analyze"
        resp = requests.post(api_url, json={"text": text}, timeout=10)
        resp.raise_for_status()
        result = resp.json()
    except requests.RequestException as e:
        return Response({"error": "Model service unavailable.", "details": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({"post_id": post.get("id"), "text": text, "hate_speech_result": result}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def misinformation_analyze(request):
    """
    Analyze text for misinformation using external FastAPI model.
    Expects JSON: {"text": "..."}
    Returns: FastAPI model response or error.
    """
    text = request.data.get("text")
    if not text:
        return Response({"error": "No text provided."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        api_url = "https://model.sui-ru.com/misinformation/analyze"
        resp = requests.post(api_url, json={"text": text}, timeout=10)
        resp.raise_for_status()
        result = resp.json()
    except requests.RequestException as e:
        return Response({"error": "Model service unavailable.", "details": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(result, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def misinformation_analyze_random_facebook_post(request):
    """
    Select a random Facebook post from facebook_data.json, send its text to the misinformation model, and return the result.
    """
    posts = load_facebook_data()
    if not posts:
        return Response({"error": "No Facebook data available."}, status=status.HTTP_404_NOT_FOUND)
    post = random.choice(posts)
    text = post.get("text", "")
    if not text:
        return Response({"error": "Selected post has no text."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        api_url = "https://model.sui-ru.com/misinformation/analyze"
        resp = requests.post(api_url, json={"text": text}, timeout=10)
        resp.raise_for_status()
        result = resp.json()
    except requests.RequestException as e:
        return Response({"error": "Model service unavailable.", "details": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({"post_id": post.get("id"), "text": text, "misinformation_result": result}, status=status.HTTP_200_OK)
