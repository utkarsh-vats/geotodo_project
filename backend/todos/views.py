from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.db import models
import requests
from .models import Todo, TodoLocation
from .serializers import TodoSerializer, TodoLocationSerializer

class TodoListCreateView(generics.ListCreateAPIView):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Todo.objects.filter(user=self.request.user)
        
        # Filter by location proximity if provided
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')
        radius = self.request.query_params.get('radius', '10')  # km
        
        if lat and lon:
            user_location = Point(float(lon), float(lat))
            queryset = queryset.filter(
                location__distance_lte=(user_location, Distance(km=int(radius)))
            )
        
        # Filter by sentiment
        sentiment = self.request.query_params.get('sentiment')
        if sentiment:
            queryset = queryset.filter(sentiment_label=sentiment)
        
        return queryset

class TodoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_location_from_ip(request):
    """Get user's approximate location from IP address"""
    try:
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # For development, use a public IP
        if ip == '127.0.0.1' or ip.startswith('192.168'):
            ip = '8.8.8.8'  # Google DNS for testing
        
        # Use a geolocation service
        response = requests.get(f'http://ip-api.com/json/{ip}')
        data = response.json()
        
        if data['status'] == 'success':
            return Response({
                'latitude': data['lat'],
                'longitude': data['lon'],
                'city': data['city'],
                'country': data['country']
            })
        else:
            return Response({'error': 'Could not determine location'}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sentiment_analysis_stats(request):
    """Get sentiment analysis statistics for user's todos"""
    todos = Todo.objects.filter(user=request.user)
    
    stats = {
        'total': todos.count(),
        'positive': todos.filter(sentiment_label='positive').count(),
        'negative': todos.filter(sentiment_label='negative').count(),
        'average_sentiment': todos.aggregate(
            avg_sentiment=models.Avg('sentiment_score')
        )['avg_sentiment'] or 0
    }
    
    return Response(stats)