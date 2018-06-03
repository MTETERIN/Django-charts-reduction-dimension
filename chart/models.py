from django.db import models

# Create your models here.
class Recomendation(models.Model):
    name = models.CharField(max_length=264,unique=True)
    lowerValue = models.IntegerField(unique=True)
    upperValue = models.IntegerField(unique=True)

    def __str__(self):
        return self.name
