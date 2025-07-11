from rest_framework import response
from .serializers import PlantaSerializer
from rest_framework.views import APIView
from rest_framework import status

class PlantasAPI (APIView):
    def post (self, request):
        serializer = PlantaSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return response(serializer.data, status= status.HTTP_201_CREATED)
        else:
            return response(serializer.data, status = status.HTTP_400_BAD_REQUEST)