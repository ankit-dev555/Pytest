from rest_framework import serializers

from .models import Album
class AlbumSerialiser(serializers.ModelSerializer):
    class Meta:
        model=Album
        fields=['name']
        #fields='__all__'