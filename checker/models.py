from django.db import models

class Game(models.Model):
    article_id  = models.IntegerField()
    title_jp    = models.CharField(max_length=512)
    title_en    = models.CharField(max_length=512)
    publisher   = models.CharField(max_length=512, null=True)
    release     = models.IntegerField(null=True)
    media       = models.CharField(max_length=512, null=True)
