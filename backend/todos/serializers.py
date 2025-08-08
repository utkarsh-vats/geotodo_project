from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.gis.geos import Point
from .models import Todo, TodoLocation

class TodoSerializer(GeoFeatureModelSerializer):
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)
    
    class Meta:
        model = Todo
        geo_field = "location"
        fields = '__all__'
        read_only_fields = ('user', 'sentiment_score', 'sentiment_label', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        # Extract lat/lon and create Point
        lat = validated_data.pop('latitude', None)
        lon = validated_data.pop('longitude', None)
        
        if lat is not None and lon is not None:
            validated_data['location'] = Point(lon, lat)  # PostGIS uses lon, lat
        
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TodoLocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    
    class Meta:
        model = TodoLocation
        fields = '__all__'
        read_only_fields = ('user',)
    
    def create(self, validated_data):
        lat = validated_data.pop('latitude')
        lon = validated_data.pop('longitude')
        validated_data['location'] = Point(lon, lat)
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)