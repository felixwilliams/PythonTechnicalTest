from django.db import models
from django.utils import timezone

class Bond(models.Model):
    isin = models.CharField(max_length=12)
    size = models.IntegerField(default=0)
    currency = models.CharField(max_length=3)
    maturity = models.DateField()
    lei = models.CharField(max_length=20)
    legal_name = models.CharField(max_length=12)
    owner = models.ForeignKey('auth.User', related_name='bonds', on_delete=models.CASCADE)

    # optional for readability within admin view
    def __str__(self):
        return self.isin + ' - ' + self.legal_name
