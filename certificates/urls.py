from django.urls import path

from certificates.diplom_create import DiplomView
from .views import GenerateCertificateView

urlpatterns = [
    path("certificate/<str:email>/", GenerateCertificateView.as_view(), name="generate_certificate"),
    path("diplom/<str:email>/", DiplomView.as_view(), name="generate_certificate"),
]
