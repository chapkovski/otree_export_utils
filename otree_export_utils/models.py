from django.db import models

class TestModel(models.Model):
    title=models.CharField(max_length=100)
    myf=models.CharField(max_length=100)