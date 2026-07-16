# tests/models.py
from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()


class Tag(models.Model):
    item = models.ForeignKey(Item, related_name="tags", on_delete=models.CASCADE)
    label = models.CharField(max_length=50)
