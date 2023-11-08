from rest_framework import serializers
from .models import Kniha, Zanr

class ZanrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zanr
        fields = ('nazev_zanru')

class KnihaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kniha
        fields = ('nazev', 'autor', 'zanr')