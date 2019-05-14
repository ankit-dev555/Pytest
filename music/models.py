from django.db import models
from django.core.urlresolvers import reverse

# Create your models here.
class Album(models.Model):
    name=models.CharField(max_length=250)
    def __str__(self):
        return self.name


class song(models.Model):
    name=models.CharField(max_length=250)
    album=models.ForeignKey(Album,on_delete=models.CASCADE)


class video(models.Model):
    videox=models.FileField()
    videoname=models.CharField(max_length=250)
    def get_absolute_url(self):
        return reverse('details', kwargs={'album_id': 1})