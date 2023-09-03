from typing import Iterable, Optional
from django.db import models
from urllib.request import urlretrieve
import os
import time
import requests
from django.core.files import File

# Create your models here.

class Story(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class POST(models.Model):
    message = models.TextField(blank=True)
    # ex) WOW.png 파일을 업로드할 경우, 
    # instagram/post/20210901/WOW.png 경로에 저장되며
    # DB에는 "WOW.png" 문자열을 저장한다.
    image_file = models.ImageField(blank=True, upload_to='photo/%Y%m%d')
    image_url = models.URLField()
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # return f"Custom Post object ({self.id})"
        return self.message
    
    def get_remote_image(self):
        
        if self.image_url and not self.image_file:
            result = urlretrieve(self.image_url)
            print(result)
            self.image_file.save(
                    'test.png',
                    File(open(result[0], 'rb'))
                    )
            self.save()