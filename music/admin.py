from django.contrib import admin

# Register your models here.
from .models import Album
from .models import song
from .models import video
admin.site.register(Album)
admin.site.register(song)
admin.site.register(video)