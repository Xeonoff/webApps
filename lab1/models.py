from django.db import models
class Card(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    class Meta:
        app_label = 'lab1'
    def __str__(self):
        return self.title
# Create your models here.
