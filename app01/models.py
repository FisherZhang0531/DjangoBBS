from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

# Store User Information,In order to user Auth Package. We need it to inherit AbstractUser Class
class User(AbstractUser):
    phone = models.CharField(max_length=32, null=True, blank=True)
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.svg')
    create_time = models.DateTimeField(auto_now_add=True)

    """Foreign Keys"""
    blog = models.OneToOneField('Blog', null=True, blank=True)

    def __str__(self):
        return self.username


class Blog(models.Model):
    site_name = models.CharField(max_length=255)
    site_title = models.CharField(max_length=255)
    site_theme = models.CharField(max_length=255)  # css/js的文件路径
    """Foreign Keys"""

    def __str__(self):
        return self.site_name


class Category(models.Model):
    name = models.CharField(max_length=32)
    """Foreign Keys"""
    blog = models.ForeignKey('Blog')

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=32)
    """Foreign Keys"""
    blog = models.ForeignKey('Blog', null=True, blank=True)
    articles = models.ManyToManyField(
        to='Article',
        through='Tags2Article',
        through_fields=('tag', 'article')
    )

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    When use those Optimization Fields You can use JOIN Search in Database to get those data in those
    fields by build foreign keys. In order to get data in an efficient way, we create those fields in the table
    to reduce the Query to release the load for data base.

    To be noticed that, when you operate the Tables Include Link and Comment, the field should be auto_increment
    or auto_decrement by 1.
    """
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)

    # Optimization Fields(data should link to the Like Table and Comment Table)
    up_num = models.IntegerField(default=0, verbose_name='Thumb_up_number')
    down_num = models.IntegerField(default=0, verbose_name='Thumb_down_number')
    comment_num = models.IntegerField(default=0, )

    """Foreign Keys"""
    blog = models.ForeignKey("Blog")
    category = models.ForeignKey('Category')
    tags = models.ManyToManyField(
        to='Tag',
        through='Tags2Article',
        through_fields=('article', 'tag'))

    def __str__(self):
        return self.title


# Relationship Table for Article and Tags
class Tags2Article(models.Model):
    article = models.ForeignKey('Article')
    tag = models.ForeignKey('Tag')


class Like(models.Model):
    # If the Thumb_UP button is clicked, this field should be 1. Otherwise, it will be 0.
    IS_UP_CHOICES = ((True, 'like'), (False, 'dislike'))
    is_up = models.NullBooleanField(choices=IS_UP_CHOICES, null=True, blank=True)
    """foreign keys"""
    # Link to user who press the Like Buuton
    user = models.ForeignKey('User')
    article = models.ForeignKey('Article')


class Comment(models.Model):
    content = models.CharField(max_length=255)
    comment_time = models.DateTimeField(auto_now_add=True)
    is_del = models.BooleanField(default=False)
    """Foreign Keys"""
    # Link to the user who left the comment
    user = models.ForeignKey("User")
    # Link to the article where the comment should belongs to
    article = models.ForeignKey('Article')
    # Link to the father comment where the comment is a reply
    parent = models.ForeignKey('self', null=True, blank=True,)
