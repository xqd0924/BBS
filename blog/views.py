from django.shortcuts import render, HttpResponse, redirect
from django.db.models import Count
from django.db.models.functions import TruncMonth
from blog.myforms import RegForms
from blog import models
from django.http import JsonResponse


def register(request):
    forms = RegForms()
    if request.method == 'GET':
        return render(request, 'register.html', {'forms': forms})
    elif request.method == 'POST':
        response = {'status': 100, 'msg': None}
        forms = RegForms(request.POST)
        if forms.is_valid():
            dic = forms.cleaned_data
            dic.pop('re_pwd')
            myfile = request.FILES.get('myfile')
            if myfile:
                dic['avatar'] = myfile
            models.UserInfo.objects.create_user(**dic)
            response['msg'] = '注册成功'
            response['url'] = '/login/'
        else:
            response['status'] = 101
            response['msg'] = '注册失败'
            response['errors'] = forms.errors
        return JsonResponse(response)


from django.contrib import auth
from django.contrib.auth import login, logout


def user_login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        valid_code = request.POST.get('valid_code')
        if valid_code.upper() == request.session['valid_code'].upper():
            user = auth.authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('/index/')
            else:
                error = '用户名或密码错误'
                return render(request, 'login.html', {'error': error})
        else:
            error = '验证码错误'
            return render(request, 'login.html', {'error': error})


import random


def get_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


from io import BytesIO
from PIL import Image, ImageFont, ImageDraw


def get_code(request):
    img = Image.new("RGB", (300, 35), get_color())
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font='static/font/ss.TTF', size=20)
    code_str = ''
    for i in range(5):
        num = str(random.randint(0, 9))
        upper_t = chr(random.randint(65, 90))
        lower_t = chr(random.randint(97, 122))
        t = random.choice([num, upper_t, lower_t])
        code_str += t
        draw.text((20 + i * 40, 5), t, fill=get_color(), font=font)
    print(code_str)
    request.session['valid_code'] = code_str
    f = BytesIO()
    img.save(f, 'png')
    data = f.getvalue()
    return HttpResponse(data)


def index(request):
    article_list = models.Article.objects.all()
    return render(request, 'index.html', {'article_list': article_list})


def logout_s(request):
    logout(request)
    return redirect('/index/')


def sitehome(request, username, *args, **kwargs):
    condition = kwargs.get('condition')
    param = kwargs.get('param')
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'error.html')
    blog = user.blog
    article_list = blog.article_set.all()
    if condition == 'tag':
        tag = models.Tag.objects.filter(pk=param)
        article_list = article_list.filter(tag=tag)
    elif condition == 'category':
        article_list = article_list.filter(category_id=param)
    elif condition == 'archive':
        year, month = param.split('-')
        article_list = article_list.filter(create_time__year=year, create_time__month=month)
    ret_category = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values_list('title', 'c',
                                                                                                      'pk')
    print(ret_category)
    ret_tag = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values_list('title', 'c', 'pk')
    print(ret_tag)
    ret_month = models.Article.objects.filter(blog=blog).annotate(y_m=TruncMonth('create_time')).values('y_m').annotate(
        c=Count('pk')).values_list('y_m', 'c').order_by('-y_m')
    print(ret_month)
    return render(request, 'homesite.html', locals())


def article_detail(request, username, pk):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'error.html')
    blog = user.blog
    ret_category = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values_list('title', 'c',
                                                                                                      'pk')
    print(ret_category)
    ret_tag = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values_list('title', 'c', 'pk')
    print(ret_tag)
    ret_month = models.Article.objects.filter(blog=blog).annotate(y_m=TruncMonth('create_time')).values('y_m').annotate(
        c=Count('pk')).values_list('y_m', 'c').order_by('-y_m')
    print(ret_month)
    article = models.Article.objects.filter(blog=blog, pk=pk).first()
    commit_list = article.commit_set.all()
    if not article:
        return render(request, 'error.html')
    return render(request, 'article_detail.html', locals())


import json


def diggit(request):
    response = {'status': 100, 'msg': None}
    user = request.user
    article_id = request.POST.get('article_id')
    is_up = request.POST.get('is_up')
    is_up = json.loads(is_up)
    if user:
        article = models.Article.objects.filter(pk=article_id).first()
        ret = models.UpAndDown.objects.filter(user=user, article=article).first()
        if ret:
            response['status'] = 102
            response['msg'] = '您已经推荐过了'
        else:
            models.UpAndDown.objects.create(user=user, article=article, is_up=is_up)
            if is_up:
                article.up_num += 1
                article.save()
                response['msg'] = '点赞成功'
            else:
                article.down_num += 1
                article.save()
                response['msg'] = '点踩成功'
    else:
        response['status'] = 101
        response['msg'] = '您没有登录，请先登录'
    return JsonResponse(response)

from django.core.mail import send_mail
def commit(request):
    response = {'status': 100, 'msg': None}
    user = request.user
    article_id = request.POST.get('article_id')
    content = request.POST.get('content')
    parent_id = request.POST.get('parent_id')
    if user:
        article = models.Article.objects.filter(pk=article_id).first()
        ret = models.Commit.objects.create(user=user, article=article, content=content, parent_id=parent_id)
        article.commit_num += 1
        article.save()
        if parent_id:
            response['parent_name'] = ret.parent.user.username
            response['parent_content'] = ret.parent.content
        response['username'] = ret.user.username
        response['content'] = ret.content
        response['msg'] = '评论成功'
        from BBS_2 import settings
        article_name = ret.article.title
        user_name = request.user.username
        # send_mail('您的%s文章被%s评论了' % (article_name,user_name),'评论内容：%s' % content,settings.EMAIL_HOST_USER,['xqd0924@163.com'])
        from threading import Thread
        t1 = Thread(target=send_mail,args=('您的%s文章被%s评论了' % (article_name,user_name),'评论内容：%s' % content,settings.EMAIL_HOST_USER,['xqd0924@163.com']))
        t1.start()

    else:
        response['status'] = 101
        response['msg'] = '您没有登录，请先登录'
    return JsonResponse(response)


from django.contrib.auth.decorators import login_required


@login_required(login_url='/login/')
def backend(request):
    blog = request.user.blog
    article_list = models.Article.objects.filter(blog=blog)
    return render(request, 'backend/backend.html', locals())


from bs4 import BeautifulSoup


@login_required(login_url='/login/')
def add_article(request):
    if request.method == 'GET':
        return render(request, 'backend/add_article.html')
    else:
        title = request.POST.get('title')
        content = request.POST.get('content')
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()
        desc = soup.text[0:150]
        blog = request.user.blog
        models.Article.objects.create(title=title, content=str(soup), desc=desc, blog=blog)
        return redirect('/backend/')


def upload_file(request):
    file = request.FILES.get('imgFile')
    with open('media/upload/%s' % file.name, 'wb') as f:
        for line in file:
            f.write(line)
    dic = {'error': 0, 'url': '/media/upload/%s' % file.name}
    return JsonResponse(dic)

@login_required(login_url='/login/')
def update_head(request):
    if request.method == 'GET':
        return render(request,'update_head.html')
    else:
        myfile = request.FILES.get('head')
        user = request.user
        user.avatar = myfile
        user.save()
        return redirect('/index/')


# def update_article(request,pk):
#     if request.method == 'GET':
#         article = models.Article.objects.get(pk=pk)
#         return render(request,'backend/update_article.html',{'article':article})

def update_article(request,pk):
    if request.method == 'GET':
        article = models.Article.objects.get(pk=pk)
        return render(request,'backend/update_article2.html',{'article_id':pk})


def get_article(request,pk):
    article = models.Article.objects.get(pk=pk)
    return JsonResponse({'title':article.title,'content':article.content})
