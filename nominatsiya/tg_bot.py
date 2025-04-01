from django.http import JsonResponse, Http404
from django.conf import settings
from django.views import View
from .models import User
from PIL import Image, ImageDraw, ImageFont
import os
import qrcode
import telegram
from telegram import Bot
from telegram.error import TelegramError

TELEGRAM_BOT_TOKEN = "8133152050:AAHpwy9GnL-vLQbqj--vPRQtbT-yYKrAw_g"
TELEGRAM_CHAT_ID = "USER_CHAT_ID"

def send_certificate_via_telegram(file_path):
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        with open(file_path, "rb") as f:
            bot.send_document(chat_id=TELEGRAM_CHAT_ID, document=f, caption="Sizning sertifikatingiz!")
        return True
    except TelegramError as e:
        print(f"Telegramga yuborishda xatolik: {e}")
        return False

class GenerateCertificateView(View):
    def get(self, request, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"error": "Ushbu emailga tegishli ma'lumot bazadan topilmadi!"}, status=404)

        output_dir = os.path.join(settings.MEDIA_ROOT, "generated")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{email}.jpg")

        if not os.path.exists(output_path):
            template_path = os.path.join(settings.MEDIA_ROOT, "certificates", "certificate_template1.jpg")
            if not os.path.exists(template_path):
                raise Http404("Sertifikat shabloni topilmadi!")

            img = Image.open(template_path)
            draw = ImageDraw.Draw(img)
            text = user.full_name  
            fan = user.fan
            font_size = 110
            fan_font_size = 70
            font_path = os.path.join(settings.MEDIA_ROOT, "font", "times.ttf")
            
            if not os.path.exists(font_path):
                raise Http404("Font topilmadi!")
            
            try:
                font = ImageFont.truetype(font_path, font_size)
                fan_font = ImageFont.truetype(font_path, fan_font_size)
            except IOError:
                return JsonResponse({"error": "Fontni ochishda xatolik!"}, status=500)
            
            x, y = 1450, 1380  # Ism joylashuvi
            x1, y1 = 1450, 1630  # Fan joylashuvi
            
            draw.text((x, y), text, font=font, fill=(37, 59, 128))
            draw.text((x1, y1), fan, font=fan_font, fill=(37, 59, 128))
            
            qr_data = f"https://cert.tma.uz/media/generated/{email}.jpg"
            qr = qrcode.QRCode(box_size=10, border=0)
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill="black", back_color="white")
            qr_path = os.path.join(output_dir, f"{email}_qr.png")
            qr_img.save(qr_path)
            
            qr_img = Image.open(qr_path)
            img.paste(qr_img, (150, 1422))
            img.save(output_path)
            
            if os.path.exists(qr_path):
                os.remove(qr_path)
        
        file_url = f"/media/generated/{email}.jpg"
        file_path = os.path.join(settings.MEDIA_ROOT, "generated", f"{email}.jpg")
        
        # Telegramga yuborish
        send_certificate_via_telegram(file_path)
        
        return JsonResponse({"file_url": file_url})
