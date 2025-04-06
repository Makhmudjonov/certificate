from django.http import JsonResponse, Http404
from django.conf import settings
from django.views import View
from .models import User
from PIL import Image, ImageDraw, ImageFont
import os
import qrcode

class GenerateCertificateView(View):
    def get(self, request, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "Ushbu emailga tegishli ma'lumot bazadan topilmadi!"}, status=404)

        output_dir = os.path.join(settings.MEDIA_ROOT, "generated")
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f"{email}.jpg")

        if os.path.exists(output_path):
            file_url = f"/media/generated/{email}.jpg"
            return JsonResponse({"file_url": file_url})

        template_path = os.path.join(settings.MEDIA_ROOT, "certificates", "nomination_template.jpg")
        if not os.path.exists(template_path):
            raise Http404("Sertifikat shabloni topilmadi!")

        # Rasmni ochish
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)

        # Foydalanuvchi ismi va fan
        text = user.full_name or ""
        fan = user.fan or ""
        code = user.certificate_number or ""

        font_size = 110
        fan_font_size = 70
        fan_font_size2 = 40
        font_path = os.path.join(settings.MEDIA_ROOT, "font", "5555-bold.ttf")  # O'zingizga mos font faylini ko'rsating
        bold_font_path = os.path.join(settings.MEDIA_ROOT, "font", "5555-bold.ttf")  # O'zingizga mos font faylini ko'rsating

        # Tekshirish va fontni yuklash
        if not os.path.exists(font_path):
            raise Http404("Font topilmadi!")

        try:
            font = ImageFont.truetype(bold_font_path, font_size)
            fan_font = ImageFont.truetype(bold_font_path, fan_font_size)
            fan_font2 = ImageFont.truetype(font_path, fan_font_size2)
        except IOError:
            return JsonResponse({"error": "Fontni ochishda xatolik!"}, status=500)

        # **Matn uzunligiga qarab x koordinatani aniqlash**
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = len(user.full_name)  # width of the text
        max_width = 25  

        if text_width < max_width:
            x = 1450  # O'rtaga moslash
        else:
            x = 800  # Uzoq ism bo‘lsa chapga yaqinroq 

        y = 1370  # Ismni joylashuvi (vertikal)
        x1, y1 = 1450, 1620  # Fan joylashuvi (vertikal)
        x2, y2 = 190, 1550  # Fan joylashuvi (vertikal)

        # Matnni joylashtirish
        draw.text((x, y), text, font=font, fill=(37, 59, 128))  # Ko'k rang
        draw.text((x1, y1), fan, font=fan_font, fill=(37, 59, 128))
        draw.text((x2, y2), code, font=fan_font2, fill=(37, 59, 128))

        # Debugging: Save intermediate image to check if text is placed correctly
        img.save(os.path.join(settings.MEDIA_ROOT, "generated", "debug_image.jpg"))

        # QR-kod yaratish
        qr_data = f"https://mforms.uz/media/generated/{email}.jpg"
        qr = qrcode.QRCode(box_size=9.5, border=0)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill="black", back_color="white")
        qr_path = os.path.join(output_dir, f"{email}_qr.png")
        qr_img.save(qr_path)

        # QR-kodni rasmga joylashtirish
        qr_img = Image.open(qr_path)
        img.paste(qr_img, (175, 1200))  # Joylashuvni tekshirish

        # Rasmni saqlash
        img.save(output_path)

        # QR rasmni o'chirish
        if os.path.exists(qr_path):
            os.remove(qr_path)

        file_url = f"/media/generated/{email}.jpg"
        return JsonResponse({"file_url": file_url})
