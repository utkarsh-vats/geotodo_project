from django.contrib.gis.db import models
from django.contrib.auth.models import User
from textblob import TextBlob

class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('lowb', 'High'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Geospacial fields
    location = models.PointField(null=True, blank=True)
    location_name = models.CharField(max_length=100, blank=True)

    # Sentiment analysis fields
    sentiment_score = models.FloatField(null=True, blank=True)
    sentiment_label = models.CharField(max_length=20, blank=True)  # positive/negative/neutral
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if(self.description):
            blob = TextBlob(self.description)
            self.sentiment_score = blob.sentiment.polarity

            if self.sentiment_score > 0.1:
                self.sentiment_label = 'positive'
            elif self.sentiment_score < -0.1:
                self.sentiment_label = 'negative'
            else:
                self.sentiment_label = 'neutral'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.user.username})"
    

class TodoLocations(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.PointField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"
