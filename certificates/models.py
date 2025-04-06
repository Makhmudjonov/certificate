from django.db import models
from django.contrib import admin
import json
import re  # ✅ RegEx kutubxonasi
from django import forms
from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponse


class Certificate(models.Model):
    email = models.EmailField(unique=True)
    pdf_file = models.FileField(upload_to='certificates/')
    image_file = models.ImageField(upload_to='certificates/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class User(models.Model):
    ORIN_CHOICES = [
        (1, "1-o'rin"),
        (2, "2-o'rin"),
        (3, "3-o'rin"),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    fan = models.CharField(max_length=255)
    otm_name = models.CharField(max_length=255,null=True, blank=True)
    orin = models.PositiveIntegerField(choices=ORIN_CHOICES, null=True, blank=True)  # ✅ Null va ixtiyoriy
    musobaqa_nomi = models.CharField(max_length=255, null=True, blank=True)
    certificate_number = models.CharField(max_length=255,unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.musobaqa_nomi}"

    @classmethod
    def load_from_json(cls, file):
        try:
            data = json.load(file)
            for item in data:
                # ✅ Raqamlarni olib tashlash (faqat boshlanish qismidan)
                fan_nom = re.sub(r"^\s*\d+(\.\d+)?\s*\.?\s*", "", item["fan"])

                # ✅ Faqat yangi foydalanuvchilarni qo‘shish
                user, created = cls.objects.get_or_create(
                    email=item["email"],  # Email bo‘yicha tekshiradi
                    defaults={
                        "full_name": item["full_name"],
                        "fan": fan_nom,  # ✅ Tozalangan fan nomi saqlanadi
                        "otm_name": item["otm_name"] if "otm_name" in item else None,
                        "orin": item["orin"] if "orin" in item else None,
                        "musobaqa_nomi": item["musobaqa_nomi"] if "musobaqa_nomi" in item else None,
                        "certificate_number" : item["certificate_number"] if "certificate_number" in item else None,
                    }
                )
                if not created:
                    print(f"❌ {item['email']} foydalanuvchi allaqachon mavjud, yangilanmadi.")
            return True
        except Exception as e:
            print("Error loading JSON:", e)
            return False


class JsonUploadForm(forms.Form):
    json_file = forms.FileField(label="JSON Faylni Yuklash")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id","full_name", "email", "fan", "otm_name", "orin", "musobaqa_nomi")
    readonly_fields = ("id",)  # IDni o‘zgartirishdan himoya qilish
    search_fields = ("full_name", "email", "musobaqa_nomi")
    list_filter = ("orin",)
    list_display_links = ("id", "full_name")  # ID ustiga bosish orqali o‘zgarish sahifasiga o‘tish


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("upload-json/", self.admin_site.admin_view(self.upload_json), name="user_upload_json"),
        ]
        return custom_urls + urls

    def upload_json(self, request):
        if request.method == "POST":
            form = JsonUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES["json_file"]
                if User.load_from_json(file):
                    self.message_user(request, "✅ JSON fayl muvaffaqiyatli yuklandi. Faqat yangi foydalanuvchilar qo‘shildi.")
                    return redirect("..")
                else:
                    self.message_user(request, "❌ JSON yuklashda xatolik yuz berdi.", level="error")
        else:
            form = JsonUploadForm()

        return render(request, "admin/upload_json.html", {"form": form})


class DiplomUser(models.Model):
    ORIN_CHOICES = [
        (1, "1-o'rin"),
        (2, "2-o'rin"),
        (3, "3-o'rin"),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=True, blank=True)
    fan = models.CharField(max_length=255)
    otm_name = models.CharField(max_length=255,null=True, blank=True)
    orin = models.CharField(max_length=255, null=True, blank=True)  # ✅ Null va ixtiyoriy
    musobaqa_nomi = models.CharField(max_length=255, null=True, blank=True)
    diplom_number = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.musobaqa_nomi}"

    @classmethod
    def diplom_load_from_json(cls, file):
        try:
            data = json.load(file)
            for item in data:
                # ✅ Raqamlarni olib tashlash (faqat boshlanish qismidan)
                # fan_nom = re.sub(r"^\s*\d+(\.\d+)?\s*\.?\s*", "", item["fan"])

                # ✅ Faqat yangi foydalanuvchilarni qo‘shish
                user, created = cls.objects.get_or_create(
                    email=item["email"],  # Email bo‘yicha tekshiradi
                    defaults={
                        "full_name": item["full_name"],
                        "fan": 'fan',  # ✅ Tozalangan fan nomi saqlanadi
                        "otm_name": item["otm_name"] if "otm_name" in item else None,
                        "orin": item["orin"] if "orin" in item else None,
                        "musobaqa_nomi": item["musobaqa_nomi"] if "musobaqa_nomi" in item else None,
                        "diplom_number" : item["diplom_number"] if "diplom_number" in item else None,
                    }
                )
                if not created:
                    print(f"❌ {item['email']} foydalanuvchi allaqachon mavjud, yangilanmadi.")
            return True
        except Exception as e:
            print("Error loading JSON:", e)
            return False


class DiplomJsonUploadForm(forms.Form):
    json_file = forms.FileField(label="JSON Faylni Yuklash")


@admin.register(DiplomUser)
class DiplomUserAdmin(admin.ModelAdmin):
    list_display = ("id","full_name", "email", "fan", "otm_name", "orin", "musobaqa_nomi")
    readonly_fields = ("id",)  # IDni o‘zgartirishdan himoya qilish
    search_fields = ("full_name", "email", "musobaqa_nomi")
    list_filter = ("orin",)
    list_display_links = ("id", "full_name")  # ID ustiga bosish orqali o‘zgarish sahifasiga o‘tish


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("diplom-json/", self.admin_site.admin_view(self.upload_json), name="diplom_user_upload_json"),
        ]
        return custom_urls + urls

    def upload_json(self, request):
        if request.method == "POST":
            form = JsonUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES["json_file"]
                if DiplomUser.diplom_load_from_json(file):
                    self.message_user(request, "✅ JSON fayl muvaffaqiyatli yuklandi. Faqat yangi foydalanuvchilar qo‘shildi.")
                    return redirect("..")
                else:
                    self.message_user(request, "❌ JSON yuklashda xatolik yuz berdi.", level="error")
        else:
            form = JsonUploadForm()

        return render(request, "admin/upload_json.html", {"form": form})
