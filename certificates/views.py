import fitz  # PyMuPDF
import os
from django.http import JsonResponse, Http404
from django.conf import settings
from django.views import View

class GenerateCertificateView(View):
    def get(self, request, email):
        # Asl shablon PDF faylini olish
        template_path = os.path.join(settings.MEDIA_ROOT, "certificates", "certificate_template.pdf")
        if not os.path.exists(template_path):
            raise Http404("Sertifikat shabloni topilmadi!")

        # Foydalanuvchi ismini chiqarish
        user_name = email.split("@")[0].replace(".", " ").title()

        # Generatsiya qilingan sertifikatlar katalogi
        output_dir = os.path.join(settings.MEDIA_ROOT, "generated")
        os.makedirs(output_dir, exist_ok=True)  # Katalog yaratish

        # Foydalanuvchi sertifikati yo‘li
        output_path = os.path.join(output_dir, f"{email}.pdf")

        # PDFni ochish va o‘zgartirish
        doc = fitz.open(template_path)
        page = doc[0]  # 1-sahifa

        # Sertifikatga matn yozish
        text = user_name
        font_size = 30  
        x, y = 270, 350  

        page.insert_text((x, y), text, fontsize=font_size, color=(0, 0, 0))

        # Yangi PDFni saqlash
        doc.save(output_path)
        doc.close()

        # Fayl yo‘lini qaytarish (JSON formatda)
        file_url = f"/media/generated/{email}.pdf"
        return JsonResponse({"file_url": file_url})
