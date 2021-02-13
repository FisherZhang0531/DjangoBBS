from django import template
from app01 import models
from django.db.models.functions import TruncMonth
from django.db.models import Count

register = template.Library()

@register.inclusion_tag('blog_left_menu.html')
def left_menu(username):
    user_obj = models.User.objects.filter(username=username).first()
    blog_obj = user_obj.blog
    # query all tags belong to this user and article number included in this tag
    tag_query_set = models.Tag.objects.filter(blog=blog_obj).annotate(count=Count('article__id')).values('name',
                                                                                                         'count', 'pk')
    # query all categories belong to this user and article number included in this tag
    category_query_set = models.Category.objects.filter(blog=blog_obj).annotate(count=Count('article__id')).values(
        'name', 'count', 'pk')
    # query by create time based on Month to show user's article
    month_query_set = models.Article.objects.filter(blog=blog_obj).annotate(date=TruncMonth('create_time')).values(
        'date').annotate(count=Count('id')).values('date', 'count')
    return locals()