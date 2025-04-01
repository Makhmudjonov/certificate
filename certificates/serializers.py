from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "orin": {"required": False, "allow_null": True}  # ✅ Ixtiyoriy va null bo‘lishi mumkin
        }
