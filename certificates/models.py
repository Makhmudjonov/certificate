from django.db import models

class Certificate(models.Model):
    email = models.EmailField(unique=True)
    file_path = models.FileField(upload_to="certificates/", blank=True, null=True)

    def __str__(self):
        return self.email
