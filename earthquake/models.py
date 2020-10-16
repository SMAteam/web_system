from django.db import models

class DisasterInfo(models.Model):
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
class DisasterInfoCache(models.Model):
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
class Parameter(models.Model):
    task_id = models.CharField(max_length=10)
    last_time = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "parameter"
class PostExtra(models.Model):
    # weiboPost = models.OneToOneField("WeiboPost", on_delete=models.CASCADE, to_field=t)

    task_id = models.CharField(max_length=10)
    post_id = models.CharField(max_length=30)
    cluster = models.IntegerField()
    class Meta:
        db_table = "post_extra"
class WeiboPost(models.Model):
    user_id = models.BigIntegerField(null=True,blank=True)
    post_id = models.CharField(max_length=100,)
    post_content = models.TextField(null=True,blank=True)
    post_time = models.DateTimeField(null=True,blank=True)
    forward_num = models.IntegerField(null=True,blank=True)
    comment_num = models.IntegerField(null=True,blank=True)
    like_num = models.IntegerField(null=True,blank=True)
    repost_id = models.CharField(max_length=20,null=True,blank=True)
    task_id = models.CharField(max_length=20)
    class Meta:
        unique_together = ("post_id","task_id")
        ordering = ["-post_time","-forward_num","-comment_num","-like_num"]
        db_table = "weibo_post"