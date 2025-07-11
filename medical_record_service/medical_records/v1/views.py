from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
# from ..models import MedicalRecord

# Create your views here.

# class HealthCheckView(APIView):
#     """
#     Health check endpoint cho Consul
#     """
#     def get(self, request):
#         try:
#             # Test database connection
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT 1")
            
#             return Response({
#                 "service": "medical_record_service",
#                 "status": "healthy",
#                 "version": "1.0.0",
#                 "database": "connected"
#             }, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({
#                 "service": "medical_record_service",
#                 "status": "unhealthy",
#                 "error": str(e)
#             }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

# class MedicalRecordListCreateView(APIView):
#     def get(self, request):
#         try:
#             records = MedicalRecord.objects.all()
#             return Response({
#                 "total": records.count(),
#                 "records": list(records.values())
#             })
#         except Exception as e:
#             return Response({
#                 "error": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#     def post(self, request):
#         return Response({
#             "message": "Medical record creation endpoint"
#         }, status=status.HTTP_201_CREATED)
