from django.urls import path
from .views import ProcessImageView,GetData

urlpatterns = [
    path('process-image/', ProcessImageView.as_view(), name='process_image'),
    path('get-data/', GetData.as_view(), name='get_data'),
]