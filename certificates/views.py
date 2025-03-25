import fitz  # PyMuPDF
import os
import qrcode
from django.http import JsonResponse, Http404
from django.conf import settings
from django.views import View
from pdf2image import convert_from_path
from django.core.files.storage import default_storage
from .models import User  # User modelini import qilamiz

class GenerateCertificateView(View):
    def get(self, request, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "Ushbu emailga tegishli ma'lumot bazadan topilmadi!"}, status=404)

        output_dir = os.path.join(settings.MEDIA_ROOT, "generated")
        os.makedirs(output_dir, exist_ok=True)

        pdf_path = os.path.join(output_dir, f"{email}.pdf")
        image_path = os.path.join(output_dir, f"{email}.jpg")

        if os.path.exists(pdf_path) and os.path.exists(image_path):
            return JsonResponse({
                "file_url": f"/media/generated/{email}.pdf",
                "image_url": f"/media/generated/{email}.jpg"
            })

        template_path = os.path.join(settings.MEDIA_ROOT, "certificates", "certificate_template1.pdf")
        if not os.path.exists(template_path):
            raise Http404("Sertifikat shabloni topilmadi!")

        doc = fitz.open(template_path)
        page = doc[0]

        # Foydalanuvchi ismi va fan
        text = user.full_name  
        fan = getattr(user, "fan", "Fan nomi mavjud emas")

        font_size = 26
        fan_font_size = 14
        font_name = "times-bolditalic"
        color_blue = (37/255, 59/255, 128/255)

        font = fitz.Font(font_name)
        text_width = font.text_length(text, fontsize=font_size)
        max_width = 300  

        x = 300 - (text_width / 3) if text_width < max_width else 180
        y = 350  
        x1, y1 = 350, 400  

        page.insert_text((x, y), text, fontsize=font_size, fontname=font_name, color=color_blue)
        page.insert_text((x1, y1), fan, fontsize=fan_font_size, fontname=font_name, color=color_blue)

        # **QR kod yaratish**
        qr_data = f"https://cert.tma.uz/media/generated/{email}.pdf"
        qr = qrcode.QRCode(box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill="black", back_color="white")
        qr_path = os.path.join(output_dir, f"{email}_qr.png")
        qr_img.save(qr_path)

        if os.path.exists(qr_path):
            img = fitz.Pixmap(qr_path)
            rect = fitz.Rect(40, 342, 120, 422)
            page.insert_image(rect, pixmap=img)

        doc.save(pdf_path)
        doc.close()

        # **PDF'ni JPG ga aylantirish**
        images = convert_from_path(pdf_path)
        if images:
            images[0].save(image_path, 'JPEG')

        if os.path.exists(qr_path):
            os.remove(qr_path)

        return JsonResponse({
            "file_url": f"/media/generated/{email}.pdf",
            "image_url": f"/media/generated/{email}.jpg"
        })
