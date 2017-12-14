import json
from random import sample

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings

from django.http import HttpResponse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url

from .models import CategoryTable, BookTable, ChapterTable
from .form import SignInForm, SignUpForm


# Create your views here.

def get_recommend_book():
    book_ids = sample(range(1, BookTable.objects.count()), 10)
    q = Q()
    for book_id in book_ids:
        q.add(Q(**{'id': book_id}), Q.OR)
    return BookTable.objects.filter(q).only('title', 'id')


class HomeView(TemplateView):
    template_name = 'pc/home.html'

    @staticmethod
    def get_variety_book():
        cate_list = []

        for index in range(1, 7):
            books = BookTable.objects.filter(category_id=index) \
                        .select_related('author', 'category').all()[:14] \
                        .only('author', 'category', 'image', 'resume', 'id', 'title')
            cate_list.append(books)
        return cate_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['top_four'] = BookTable.top_four_book()

        cate_list = self.get_variety_book()
        context['cate_list1'] = cate_list[:3]
        context['cate_list2'] = cate_list[3:]

        context['latest_books'] = BookTable.objects.select_related('author', 'category') \
                                           .defer('image', 'resume').order_by('update_time').all()[:20]
        context['newest_books'] = BookTable.objects.select_related('author', 'category') \
                                           .only('author', 'title', 'id', 'category', 'update_time') \
                                           .order_by('-id').all()[:20]
        return context


class CategoryView(DetailView):
    template_name = 'pc/category.html'
    context_object_name = 'cate'
    slug_field = 'cate'
    slug_url_kwarg = 'cate'
    model = CategoryTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['cate_books'] = self.object.cate_books.select_related('author') \
                                    .only('author', 'resume', 'image', 'title', 'id', 'category_id') \
                                    .all()[:6]
        context['latest_books'] = self.object.cate_books \
                                      .select_related('author', 'category') \
                                      .defer('image', 'resume') \
                                      .order_by('update_time').all()[:20]
        context['recommend_books'] = self.object.cate_books \
                                         .select_related('author', 'category') \
                                         .only('author', 'title', 'id', 'category').all()[:20]
        return context


class BookView(DetailView):
    template_name = 'pc/book.html'
    context_object_name = 'book'
    queryset = BookTable.objects.select_related('author', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        all_chapters = list(self.object.all_chapters.only('id', 'title_id', 'book_id', 'chapter'))

        context['all_chapters'] = all_chapters

        if len(all_chapters) < 8:
            context['latest_eight_chapters'] = reversed(all_chapters)
        else:
            context['latest_eight_chapters'] = reversed(all_chapters[-8:])

        context['recommend_books'] = get_recommend_book()
        return context


class ChapterView(DetailView):
    template_name = 'pc/chapter.html'
    model = ChapterTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['book'] = BookTable.objects.select_related('category') \
            .only('id', 'title', 'category').get(id=self.kwargs['book_id'])

        context['recommend_books'] = get_recommend_book()
        return context


class QuanbenView(ListView):
    template_name = 'pc/quanben.html'
    context_object_name = 'books'
    queryset = BookTable.objects.select_related('author', 'category') \
        .only('author', 'category', 'id', 'title') \
        .filter(_status=True).order_by('update_time')


class SearchView(TemplateView):
    template_name = 'pc/search.html'


# 更新验证码
def refresh_captcha(request):
    json_content = dict()
    json_content['new_cptch_key'] = CaptchaStore.generate_key()
    json_content['new_cptch_image'] = captcha_image_url(json_content['new_cptch_key'])
    return HttpResponse(json.dumps(json_content), content_type='application/json')


# 注册的处理函数
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['invite_code'] in settings.INVITE_CODE:
                uname = form.cleaned_data['username']
                pwd = form.cleaned_data['password']
                email = form.cleaned_data['email']
                uu = User.objects.create_user(username=uname, email=email, password=pwd)
                uu.save()
                return redirect('/sign_in')

        error_msg = '注册失败喔'
        form = SignUpForm(request.POST)
        return redirect('/sign_up', {'error_msg': error_msg, 'form': form})
    else:
        form = SignUpForm()
        return render(request, 'pc/sign_up.html', {'form': form})


# 登陆的注册函数
def sign_in(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data['username']
            pwd = form.cleaned_data['password']
            user = authenticate(request, username=uname, password=pwd)
            if user is not None:
                login(request, user)
                return redirect(request.content_params.get('next') or '/')

        error_msg = '登陆失败喔'
        form = SignInForm(request.POST)
        return redirect('/sign_in', {'error_msg': error_msg, 'form': form})
    else:
        form = SignInForm()
        return render(request, 'pc/sign_in.html', {'form': form})


def logout_handler(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER') or '/')


@login_required(login_url='/sign_in')
def upload(request):
    pass


def page_not_found(request):
    return render(request, 'pc/404.html')


def page_forbidden(request):
    return render(request, 'pc/403.html')


def server_wrong(request):
    return render(request, 'pc/502.html')
