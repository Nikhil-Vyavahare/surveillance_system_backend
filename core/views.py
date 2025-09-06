from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .gemini_utils import analyze_image_with_gemini
from .email_utils import send_email_with_image
from .storage_utils import (
    upload_to_appwrite, 
    store_response_in_firebase, 
    fetch_appwrite_files, 
    fetch_firebase_detections
)
from .models import Detection


class ProcessImageView(APIView):
    def post(self, request, *args, **kwargs):
        if 'image' not in request.FILES:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']

        # ✅ Save file temporarily
        temp_path = default_storage.save(image_file.name, ContentFile(image_file.read()))
        absolute_path = default_storage.path(temp_path)

        try:
            # Analyze with Gemini
            gemini_response = analyze_image_with_gemini(absolute_path)

            if 'garbage' in gemini_response.lower() or 'open drainage' in gemini_response.lower():
                # Upload to Appwrite
                image_url = upload_to_appwrite(absolute_path)

                # Store in Firebase
                firebase_ref = store_response_in_firebase(gemini_response, image_url)

                # Send email
                recipient_email = 'recipient@example.com'  # Change later
                send_email_with_image(recipient_email, absolute_path, gemini_response)

                # Save to DB
                Detection.objects.create(image_url=image_url, gemini_response=gemini_response)

                return Response({
                    'status': 'success',
                    'response': gemini_response,
                    'image_url': image_url
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'status': 'no_detection',
                    'response': gemini_response
                }, status=status.HTTP_200_OK)

        finally:
            # ✅ Always delete temporary file
            if default_storage.exists(temp_path):
                default_storage.delete(temp_path)


class GetData(APIView):
    def get(self, request):
        try:
            detections = fetch_firebase_detections()

            # ✅ Sort detections by timestamp (latest first if timestamp exists)
            detections = sorted(
                detections,
                key=lambda x: x.get("timestamp", 0),
                reverse=True
            )

            return Response({"detections": detections}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
