import fitz  # PyMuPDF
import os
from django.http import FileResponse, Http404
from django.conf import settings
from django.views import View

class GenerateCertificateView(View):
    def get(self, request, email):
        # Asl shablon PDF faylini tanlash
        template_path = os.path.join(settings.MEDIA_ROOT, "certificates", "certificate_template.pdf")

        # Agar shablon mavjud bo‘lmasa, xatolik chiqarish
        if not os.path.exists(template_path):
            raise Http404("Sertifikat shabloni topilmadi!")

        # Foydalanuvchi ismini olish (email-dan ajratish yoki bazadan olish)
        user_name = email.split("@")[0].replace(".", " ").title()  # Misol uchun: lazizbek.shukurov -> Lazizbek Shukurov

        # Sertifikatni yangi fayl sifatida yaratish
        output_path = os.path.join(settings.MEDIA_ROOT, "generated", f"{email}.pdf")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Papkani yaratish

        # PDF-ni ochamiz
        doc = fitz.open(template_path)
        page = doc[0]  # 1-sahifani tanlaymiz

        # Matnni joylashtirish (X, Y koordinatalarini moslang)
        text = user_name
        font_size = 30  # Shrift o‘lchami
        x, y = 270, 350  # Ismni joylashtirish koordinatalari (ehtiyojga qarab o‘zgartiring)

        # Matnni joylashtirish
        page.insert_text((x, y), text, fontsize=font_size, color=(0, 0, 0))

        # Yangi PDFni saqlash
        doc.save(output_path)
        doc.close()

        # PDF faylni foydalanuvchiga yuborish
        return FileResponse(open(output_path, "rb"), content_type="application/pdf")
