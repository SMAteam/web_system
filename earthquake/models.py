from django.db import models

class disaster_info(models.Model):
    province = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    area = models.CharField(max_length=30)
    time = models.DateTimeField(null=True, blank=True)
    info = models.CharField(max_length=255)
    number = models.IntegerField()
    grade = models.CharField(max_length=30)
    task_id = models.CharField(max_length=10)
    authority = models.CharField(max_length=10)
    # 接下来设置联合主键
    class Meta:
        db_table = "disaster_info"
class disaster_info_cache(models.Model):
    province = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    area = models.CharField(max_length=30)
    post_time = models.DateTimeField(null=True, blank=True)
    info = models.CharField(max_length=255)
    post_id = models.CharField(max_length=30)
    task_id = models.CharField(max_length=10)
    # 接下来设置联合主键
    class Meta:
        db_table = "disaster_info_cache"
class parameter(models.Model):
    task_id = models.CharField(max_length=10)
    last_time = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "parameter"
class post_extra(models.Model):
    task_id = models.CharField(max_length=10)
    post_id = models.CharField(max_length=30)
    cluster = models.IntegerField()
    class Meta:
        db_table = "post_extra"