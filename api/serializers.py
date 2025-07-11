from rest_framework import serializers
from core.models import Planta,Categoria

class PlantaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planta
        fields = '__all__' 

    
