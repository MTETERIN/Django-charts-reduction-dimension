from django.db import models

# Create your models here.
class Recomendation(models.Model):
    name = models.CharField(max_length=264,unique=True)
    lowerValue = models.IntegerField(unique=True)
    upperValue = models.IntegerField(unique=True)

    def __str__(self):
        return self.name
class Message(models.Model):
    name = models.CharField(max_length=120)
 
    def __str__(self):
        return self.name
 
 
class Feedback(models.Model):
    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    theme = models.ForeignKey(Message)
    details = models.TextField()
    date = models.DateField(auto_now_add=True)
 
    def __str__(self):
        return self.customer_name