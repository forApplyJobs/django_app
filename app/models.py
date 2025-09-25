from django.contrib.auth.models import User
from django.db import models

class Frame(models.Model):
    name = models.CharField(max_length=100)
    xmlFeedPath = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='frames/')
    coordinates = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
class OutputImage(models.Model):
    product_id = models.CharField(max_length=100)
    product_image_url = models.URLField()
    frame = models.ForeignKey(Frame, on_delete=models.CASCADE, related_name='outputs')
    image = models.ImageField(upload_to='output_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure unique product_id per frame to prevent duplicates
        unique_together = ['frame', 'product_id']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['frame', 'product_id']),
            models.Index(fields=['frame', '-created_at']),
        ]
    
    def __str__(self):
        return f"OutputImage for {self.frame.name} - {self.product_id} at {self.created_at}"