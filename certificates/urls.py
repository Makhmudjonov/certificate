from django.urls import path
from .views import GenerateCertificateView

urlpatterns = [
    path("certificate/<str:email>/", GenerateCertificateView.as_view(), name="generate_certificate"),
]
