from io import BytesIO
from random import randint, choice

from PIL import ImageDraw, Image, ImageFont
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse

from app01 import models
from app01.myforms import regforms
from app01.myfunctions.mypagenator import Pagination

# Create your views here.
def register(request):
    form_obj = regforms.RegForms()
    if request.method == "POST":
        back_dic = {"code": '', 'msg': ''}
        form_obj = regforms.RegForms(request.POST)
        if form_obj.is_valid():
            clean_data = form_obj.cleaned_data
            clean_data.pop('confirm_password')
            file_obj = request.FILES.get('avatar')
            if file_obj:
                clean_data.update({'avatar': file_obj})
            models.User.objects.create_user(**clean_data)
            back_dic['url'] = '/login/'
            back_dic["code"] = 1000
            back_dic["msg"] = "Register Successfully"
        else:
            back_dic['code'] = 2000
            back_dic["msg"] = form_obj.errors
        return JsonResponse(back_dic)

    return render(request, 'register.html', locals())


def login(request):
    """
    error code reference:
    100: login successfully;
    101: Authentication code error;
    102:Wrong Password;
    103:User not exists;
    :param request:
    :return: back
    """
    print(request.user.username, )
    redirect_url = request.GET.get('next')
    if request.method == "POST":
        input_username = request.POST.get('username')
        input_password = request.POST.get('password')
        input_auth_code = request.POST.get('auth_code').lower()
        # Check authentication code if is valid,if not return code 101
        if not request.session.get('auth_code').lower() == input_auth_code:
            print('wrong authcode')
            back_dict = {'code': 101, 'msg': 'Wrong Auth Code'}
            return JsonResponse(back_dict, safe=False)
        # check user existence, if not return code 103
        user_obj = models.User.objects.filter(username=input_username).first()
        if not user_obj:
            back_dict = {'code': 103, 'msg': 'User not exists'}
        # check username and password matches, if match login and return
        elif auth.authenticate(request, username=input_username, password=input_password):
            auth.login(request, user_obj)
            back_dict = {'code': 100, 'msg': 'Login Successfully'}
        # check username and password matches, if not return code 102
        else:
            back_dict = {'code': 102, 'msg': 'wrong  password'}
        return JsonResponse(back_dict, safe=False)

    return render(request, 'login.html', {'redirect_url': redirect_url})


def get_auth_code(request):
    # print('1111',request.session.get('auth_code'))
    auth_code = ''
    img_obj = Image.new('RGB', (194, 37), (randint(0, 255), randint(0, 255), randint(0, 255)))
    img_draw = ImageDraw.Draw(img_obj)
    img_font = ImageFont.truetype(font=r'static/font/cjkfonts_handingwriting4.ttf', size=32)
    for i in range(6):
        random_upper = chr(randint(65, 90))
        random_lower = chr(randint(97, 122))
        random_int = str(randint(0, 9))
        # Choose one from top 3
        letter = choice((random_upper, random_lower, random_int))
        # write the letter into img.
        # divided the width of picture into 8 parts,each letter padding left equals the index*part_width
        img_draw.text(((i + 1) * 24.5, -2), letter, (randint(0, 255), randint(0, 255), randint(0, 255)), font=img_font)
        # auth_code append the current letter
        auth_code += letter
    # print(auth_code)
    # write the code into session
    request.session['auth_code'] = auth_code
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    # print(io_obj.getvalue())
    return HttpResponse(io_obj.getvalue())


def home(request):
    # get all exists articles
    article_query_set = models.Article.objects.all()
    # customized paginator
    current_page=request.GET.get("page",1)
    all_count = article_query_set.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=5)
    page_query_set = article_query_set[page_obj.start:page_obj.end]
    return render(request, 'home.html', locals())


@login_required
def logout(request):
    """

    :param request:
    :return: 'code':1000,'msg':'logged out'
    """
    print(request.user.is_authenticated)
    auth.logout(request)
    back_dict = {'code': 1000, 'msg': 'logged out'}
    return JsonResponse(back_dict, safe=True)


def blog(request, username, **kwargs):
    print(username)
    print(kwargs)
    user_obj = models.User.objects.filter(username=username).first()
    blog_obj = user_obj.blog
    if not blog_obj:
        # print('run 404')
        return render(request, '404.html')
    article_query_set = models.Article.objects.filter(blog=blog_obj)
    if kwargs:
        filter_by = kwargs.get('filterby')
        param = kwargs.get('param')
        try:
            if filter_by == 'tag':
                if models.Tag.objects.filter(pk=param).first().blog != blog_obj:
                    msg = "This user do not have this tag"
                    return render(request, '404.html', {'msg': msg})
                article_query_set = models.Article.objects.filter(blog=blog_obj, tag=param)
            if filter_by == 'category':
                if models.Category.objects.filter(pk=param).first().blog != blog_obj:
                    msg = "This user do not have this Category"
                    return render(request, '404.html', {'msg': msg})
                article_query_set = models.Article.objects.filter(blog=blog_obj, category=param)
            if filter_by == 'archive':
                year, month = param.split('-')
                article_query_set = models.Article.objects.filter(blog=blog_obj, create_time__year=year,
                                                                  create_time__month=month)
                if not article_query_set:
                    msg = "This user do not have Article in this Time Frame"
                    return render(request, '404.html', {'msg': msg})
        except Exception as e:
            return render(request, '404.html')
    """Insert Paginator """
    current_page = request.GET.get("page", 1)
    all_count = article_query_set.count()
    page_obj = Pagination(current_page=current_page, all_count=all_count, per_page_num=5)
    page_query_set = article_query_set[page_obj.start:page_obj.end]
    return render(request, 'blog.html', locals())


def article(request, username, article_pk):
    article_obj = models.Article.objects.filter(blog__user__username=username, pk=article_pk).first()
    blog_obj = article_obj.blog
    comment_query_set = models.Comment.objects.filter(article_id=article_pk,is_del=False)

    return render(request, 'article.html', locals())


def like(request):
    """
    data
    Interface logic:
    step 1.check if logged in if not return code:301 to redirect;if logged in get the data including choice,article_id,
    and user_id
    step 2.check if the user is the articles author if is not allowed to like or dislike the article
    step 3.check if already has record in like table if has change the record if not create a new record; moreover the
    relevant article record should be up_num or down_num field should increase by 1 based on the user choice
    step 4.return back the data
    :param request:
    :return back_dict:{
        :keyword 'code':(
                        301,
                        1001,
                        2000
                        )
        :keyword 'msg':(
                        f'You need login to {choice} this article',
                        f'you can not {choice} your own article',
                        'Thanks for your feedback'
                        )
        }
    """
    if request.is_ajax():
        """step 1"""
        back_dic = {}
        # get choice
        like_choice = request.POST.get('choice')  # like or dislike
        # if not logged in return code=301 and url=current url
        if not request.user.is_authenticated:
            back_dic['code'] = 301
            back_dic['msg'] = f'You need login to {like_choice} this article'
            return JsonResponse(back_dic)
        """step 2"""
        # get article id and user id
        article_id = request.POST.get('article_id')
        user_id = request.user.id
        # get article record
        article_obj = models.Article.objects.filter(id=article_id).first()
        if request.user == article_obj.blog.user:
            back_dic['code'] = 1001
            back_dic['msg'] = f'you can not {like_choice} your own article'
        else:
            """ step 3 """
            like_obj = models.Like.objects.filter(article_id=article_id, user_id=user_id).first()
            # if already like or dislike this article
            if like_obj:
                """# if user already like this article cancel like
                if like_obj.get_is_up_display() == choice and like_obj.is_up:
                    like_obj.is_up = None
                    article_obj.up_num -= 1
                # if user already dislike or not chosen
                elif like_obj.get_is_up_display() == choice and not like_obj.is_up:
                    like_obj.is_up = None
                    # if previous was dislike, dislike -1 ;if was not chosen then the dislike +1
                    if like_obj.is_up is False:
                        article_obj.down_num -= 1
                    else:
                        article_obj.down_num += 1
                # if previous user liked this article and change to dislike:
                elif like_obj.get_is_up_display() != choice and like_obj.is_up:
                    like_obj.is_up = False
                    article_obj.down_num += 1
                    article_obj.up_num -= 1
                # if previous user disliked this article and change to like or change to not chosen:
                elif like_obj.get_is_up_display() != choice and not like_obj.is_up:
                    like_obj.is_up = True
                    # if Previous was dislike dislike-1; if previous was not chosen it remains
                    if like_obj.is_up is False:
                        article_obj.down_num -= 1
                        article_obj.up_num += 1
                    # if previous was not chosen dislike +1
                    else:
                        article_obj.down_num +=1"""
                # condition1, was like change dislike
                if like_obj.is_up is True and like_choice == 'dislike':
                    article_obj.up_num -= 1
                    article_obj.down_num += 1
                    like_obj.is_up = False
                # condition2, was like cancel like
                elif like_obj.is_up is True and like_choice == 'like':
                    article_obj.up_num -= 1
                    like_obj.is_up = None
                # condition3, was not chosen change to like
                elif like_obj.is_up is None and like_choice == 'like':
                    article_obj.up_num += 1
                    like_obj.is_up = True
                # condition4, was not chosen change to dislike
                elif like_obj.is_up is None and like_choice == 'dislike':
                    article_obj.down_num += 1
                    like_obj.is_up = False
                # condition5, was dislike change to like
                elif like_obj.is_up is False and like_choice == 'like':
                    article_obj.down_num -= 1
                    article_obj.up_num += 1
                    like_obj.is_up = True
                # condition6, was dislike cancel dislike:
                elif like_obj.is_up is False and like_choice == 'dislike':
                    article_obj.down_num -= 1
                    like_obj.is_up = None

            else:
                # create new record
                like_obj = models.Like()
                like_obj.user_id = user_id
                like_obj.article_id = article_id
                # set values based on choice
                if like_choice == 'like':
                    like_obj.is_up = True
                    article_obj.up_num += 1
                else:
                    like_obj.is_up = False
                    article_obj.down_num += 1
            like_obj.save()
            article_obj.save()
            back_dic['code'] = 2000
            back_dic['msg'] = 'Thanks for your feedback'
            back_dic['up_num'] = article_obj.up_num
            back_dic['down_num'] = article_obj.down_num
        return JsonResponse(back_dic)
    return render(request, '404.html')


def comment(request):
    """
    Logic:
    step1.check if user is authenticated,if is process further otherwise return code 301 and need to redirect
    step2.check if it is an empty comment, if is alert at front end and redirect to login page
    step3.check if it a child comment, if it is a child comment strip the '@username' in content and check the content
    is empty.If not a child comment do nothing about content.
    step4.store in database
    :param request:
    :return back_dict{"code":int(),msg:str()}:
    1.{'code':301,'msg':'You need login to comment'}
    2.{'code':1001,'msg':'Comment Can not be empty'}

    """
    if request.is_ajax():
        if request.method == "POST":
            """get from variables from ajax request"""
            back_dict = {}
            article_id = request.POST.get('article_id')
            parent_id = request.POST.get('parent_id')
            content = request.POST.get('content')
            print(content, article_id)
            """step1"""
            if request.user.is_authenticated():
                """step2"""
                if not content == '':
                    # open an transaction to prevent any corruption in database
                    with transaction.atomic():
                        """step3"""
                        # check if it is a child comment, if it is then strip the @username when store in database
                        if parent_id != '':
                            content = content.split('\n', 1)[1]
                            # check if content is empty again when it is a child
                            if content == '':
                                back_dict['code'] = 1001
                                back_dict['msg'] = 'Comment Can not be empty'
                                return JsonResponse(back_dict)
                        """step4.store in database"""
                        models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)
                        models.Comment.objects.create(user=request.user,
                                                      article_id=article_id,
                                                      content=content,
                                                      parent_id=parent_id)
                    back_dict['code'] = 2000
                    back_dict['msg'] = 'Thanks for your comment'
                else:
                    back_dict['code'] = 1001
                    back_dict['msg'] = 'Comment Can not be empty'
            else:
                back_dict['code'] = 301
                back_dict['msg'] = 'You need login to comment'
        return JsonResponse(back_dict)
    return render(request, '404.html')


def del_comment(request):
    """
    Logic:
    step1,check wants to del this comment is the user himself, check the user_id == request.user.id
    step2, if user delete own message change database,remove that comment and article comment_num -1,else go to step 3
    step3, if user delete others message, return code 1001 you cant delete someone else code.
    :param request:
    :return:
    """
    from app01.myfunctions.comment_del import CommentDel
    back_dic = {'code': None, 'msg': None}
    if request.is_ajax():
        comment_user_id = int(request.POST.get('comment_user_id'))
        article_id = request.POST.get('article_id')
        comment_id = request.POST.get('comment_id')
        """step1"""
        if request.user.id == comment_user_id:
            del_num = CommentDel.cascade_del(comment_id)
            models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') - del_num)
            back_dic['code'] = 2000
            back_dic['msg'] = "deleted"
        else:
            back_dic['code'] = 1001
            back_dic['msg'] = "Action Forbidden"
        return JsonResponse(back_dic)
    return render(request,'404.html')

