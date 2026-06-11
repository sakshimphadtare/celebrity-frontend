import base64
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .aws_logic import process_celebrity_image


# =========================================================
# HOME API (TEST)
# =========================================================
def home(request):
    return JsonResponse({
        "message": "Celebrity Detection API is running 🚀"
    })


# =========================================================
# MAIN API: Upload Image
# =========================================================
@csrf_exempt
def detect_celebrity(request):

    if request.method == "POST":

        try:
            data = json.loads(request.body)

            image_base64 = data.get("image")
            file_name = data.get("file_name")

            if not image_base64 or not file_name:
                return JsonResponse({
                    "status": "error",
                    "message": "image and file_name required"
                })

            # Call AWS logic
            result = process_celebrity_image(image_base64, file_name)

            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })

    return JsonResponse({
        "message": "Only POST method allowed"
    })