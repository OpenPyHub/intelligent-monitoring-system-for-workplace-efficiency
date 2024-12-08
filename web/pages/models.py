from django.db import models
from django.urls import reverse

# Create your models here.

class Affiliation(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Workplace(models.Model):
    name = models.CharField(max_length=50)
    affiliation = models.ForeignKey('Affiliation', on_delete=models.CASCADE)
    body = models.TextField(max_length=150)
    media = models.FileField(upload_to='')

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('workplace_detail', kwargs={"pk": self.pk})
    
    def get_media_url(self):
        if self.media:
            return self.media.url
        return 'media/no-media.mp4'
