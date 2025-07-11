from django.http import JsonResponse
from .service_discovery import get_service_address
from django.views.decorators.http import require_POST
from datetime import datetime
from .tasks import process_appointment_data, process_prescription_data
import json

import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import process_appointment_data

@csrf_exempt
def receive_appointment_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Assuming JSON payload
            time_start = data.get('time_start')
            patient_id = data.get('patient_id')
            appointment_id = data.get('appointment_id')

            if not all([time_start, appointment_id, patient_id]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            try:
                start_datetime = datetime.strptime(time_start, '%Y-%m-%dT%H:%M:%SZ')
                date = start_datetime.date()
                time = start_datetime.time()
            except ValueError:
                return JsonResponse({'error': 'Invalid starttime format. Use YYYY-MM-DDTHH:MM:SSZ'}, status=400)

            # Call external user API to get email
            def get_base_url():
                address, port = get_service_address("user_service")
                return f"http://{address}:{port}"
            base_url = get_base_url()

            user_api_url = f'{base_url}/api/v1/users/patient/{patient_id}/email'  
            response = requests.get(user_api_url)
            response.raise_for_status()  # Raise exception for 4xx/5xx errors
            user_data = response.json()
            email = user_data.get('email')  # Adjust based on API response structure

            if not email:
                return JsonResponse({'error': 'Email not found for patient ID'}, status=400)

            # Queue Celery task with all data
            process_appointment_data.delay({
                'id': appointment_id,
                'patient_email': email,  # Key phải match với task
                'date': str(date),  # Convert date object to string
                'time': str(time)   # Convert time object to string
            })

            return JsonResponse({'status': 'Appointment data received and processing'}, status=201)
        except requests.RequestException as e:
            return JsonResponse({'error': f'Failed to fetch user data: {str(e)}'}, status=502)
        except ValueError as e:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def receive_prescription_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            medication = data.get('medication')
            patient_id = data.get('patient_id')
            prescription_id = data.get('prescription_id')

            if not all([medication, patient_id,prescription_id]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            # Call external user API to get email
            def get_base_url():
                address, port = get_service_address("user_service")
                return f"http://{address}:{port}"
            base_url = get_base_url()

            user_api_url = f'{base_url}/api/v1/users/patient/{patient_id}/email' 
            response = requests.get(user_api_url)
            response.raise_for_status()  # Raise exception for 4xx/5xx errors
            user_data = response.json()
            email = user_data.get('email')  # Adjust based on API response structure

            process_prescription_data.delay({
                'id': prescription_id,
                'patient_email': email,
                'medication': medication
            })
            return JsonResponse({'status': 'Prescription data received and processing'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Internal server error'}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
