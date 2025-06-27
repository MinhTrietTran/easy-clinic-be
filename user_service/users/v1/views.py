from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .services import register_user


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        data = request.data
        try:
            result = register_user(request.data)
            return Response({"message":"User registered successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
