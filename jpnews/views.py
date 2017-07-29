import json
import random
import ast
import operator
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .models import News, UserProfile
from .forms import SignUpForm
from .forms import ChangeChannelForm
from .tokens import account_activation_token
from .LoadJsonNews import LoadJsonNews
from .jisu import jisu

def news_list(request):
    news = list(News.objects.all())
    # random.shuffle(news)
    finance_news = []
    finance_news_4 = ""
    tech_news = []
    tech_news_4 = ""
    news_news = []
    news_news_4 = ""
    sports_news = []
    sports_news_4 = ""
    edu_news = []
    edu_news_4 = ""
    for news_it in news:
        if(news_it.pic == ""):
            continue
        if(news_it.category == "finance"):
            finance_news.append(news_it)
        elif(news_it.category == "tech"):
            tech_news.append(news_it)
        elif(news_it.category == "news"):
            news_news.append(news_it)
        elif(news_it.category == "sports"):
            sports_news.append(news_it)
        elif(news_it.category == "edu"):
            edu_news.append(news_it)
    finance_news_1 = finance_news[-4:]
    finance_news_2 = finance_news[-8:-4]
    tech_news_1 = tech_news[-4:]
    tech_news_2 = tech_news[-8:-4]
    news_news_1 = news_news[-4:]
    news_news_2 = news_news[-8:-4]
    sports_news_1 = sports_news[-4:]
    sports_news_2 = sports_news[-8:-4]
    edu_news_1 = edu_news[-4:]
    edu_news_2 = edu_news[-8:-4]
    news_dict = {}
    news_dict['经济金融'] = [finance_news_1, finance_news_2]
    news_dict['科技动态'] = [tech_news_1, tech_news_2]
    news_dict['体育新闻'] = [sports_news_1, sports_news_2]
    news_dict['教育风向'] = [edu_news_1, edu_news_2]
    news_dict['近日要闻'] = [news_news_1, news_news_2]
    # Get the user's prefer about the new's categorries
    channel_list = ['经济金融', '科技动态', '体育新闻', '教育风向', '近日要闻']
    if(request.user.is_authenticated()):
        current_user = request.user
        user = User.objects.get(username=current_user.username)
        user_profile = user.userprofile
        channel_sequence = ast.literal_eval(user_profile.channel_like)
        for channel_it in channel_sequence:
            channel_list.remove(channel_it)
        for channel_it in channel_list:
            channel_sequence.append(channel_it)
        channel_list = list(channel_sequence)
    # Use news_1[0] to denote the first important news and the first collection of this kind of news
    news_1 = [0]*len(news_dict)
    news_2 = [0]*len(news_dict)
    for (i, channel_it) in enumerate(channel_list):
        news_1[i] = news_dict[channel_it][0]
        news_2[i] = news_dict[channel_it][1]
    # We use news_m_n to denote the nth component of the mth importance news
    context = {"channel_list": channel_list, "news_1_1": news_1[0], "news_1_2": news_2[0], "news_2_1": news_1[1], "news_2_2": news_2[1],
               "news_3_1": news_1[2], "news_3_2": news_2[2], "news_4_1": news_1[3], "news_4_2": news_2[3], "news_5_1": news_1[4], "news_5_2": news_2[4]}
    # context = {"channel_list": channel_list, "news_1": news_1, "news_2": news_2}
    # So we can access ith important category by channel_list[i], news_1[i] and news_2[i]
    return render(request, 'news/news_list.html', context=context)

def record_history(request):
    # The Maxmimul length of the user's history and the label of user
    max_history = 100
    max_label = 200
    # The type of news_url is string
    news_url = request.GET.get('next')
    news_click = News.objects.get(pk=news_url)
    news_tags = ast.literal_eval(news_click.tags)
    # Judge if the user is logged in
    if request.user.is_authenticated():
        # Do something for authenticated users.
        current_user = request.user
        print("When click the news, the currently logged in user is: ", current_user.username)
        user = User.objects.get(username=current_user.username)
        user_profile = user.userprofile
        # Add the news url to the history
        if(user_profile.click_history == ""):
            temp_list = []
        else:
            temp_list = ast.literal_eval(user_profile.click_history)
        news_attr = {}
        news_attr["title"] = news_click.title
        news_attr["pic"] = news_click.pic
        news_attr["weburl"] = news_click.weburl
        if(news_attr in temp_list):
            temp_list.remove(news_attr)
        temp_list.append(news_attr)
        if(len(temp_list) > max_history):
            temp_list.pop(0)
        user_profile.click_history = str(temp_list)    
        print("Now the user's history is: ", user_profile.click_history)
        # Add the tag to the user's label
        if(user_profile.label == ""):
            temp_dict = {}
        else:
            temp_dict = ast.literal_eval(user_profile.label)
        for tag in news_tags:
            if(tag not in temp_dict):
                temp_dict[tag] = 1
            else:
                temp_dict[tag] += 1
        if(len(temp_dict) > max_label):
            smallest_label = min(temp_dict, key=temp_dict.get)
            temp_dict.pop(smallest_label, None)
        user_profile.label = str(temp_dict)
        print("Now the user's label is: ", user_profile.label)
        # Save the user's profile
        user_profile.save()
    else:
        # Do something for anonymous users.
        print("When click the news, no user currently logged in")
    # Redirect to the target website of news
    return HttpResponseRedirect(news_url)

def news_recommend(request):
    news = []
    if request.user.is_authenticated():
        news_collect = News.objects.all()
        current_user = request.user
        user = User.objects.get(username=current_user.username)
        if(user.userprofile.label == ""):
            user_label = {}
        else:
            user_label = ast.literal_eval(user.userprofile.label)
        if(user.userprofile.click_history == ""):    
            history_list = []
        else:
            history_list = ast.literal_eval(user.userprofile.click_history)
        similarity_dict = {}
        for news_ins in news_collect:
            visited_flag = 0
            for history_record in history_list:
                if(news_ins.weburl == history_record["weburl"]):
                    visited_flag = 1
            if(visited_flag):
                continue
            news_tags = ast.literal_eval(news_ins.tags)
            temp_similarity = 0
            for tag in news_tags:
                if(tag in user_label):
                    temp_similarity += user_label[tag]
            if(temp_similarity > 0):
                similarity_dict[news_ins] = temp_similarity
        sorted_similarity_dict = sorted(similarity_dict.items(), key=operator.itemgetter(1), reverse=True)
        for it in sorted_similarity_dict:
            news.append(it[0])
    else:
        pass
    return render(request, 'news/news_recommend.html', {'news': news})

def news_history(request):
    user_history = []
    if request.user.is_authenticated():
        current_user = request.user
        user = User.objects.get(username=current_user.username)
        if(user.userprofile.click_history == ""):
            user_history = []
        else:
            user_history = ast.literal_eval(user.userprofile.click_history)
    else:
        pass
    user_history = reversed(user_history)
    return render(request, 'news/history.html', {'news': user_history})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # user can not login without email confirmation
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate your jpnews account.'
            message = render_to_string('registration/acc_active_email.html', {
                'user':user, 'domain':current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            # user.email_user(subject, message)
            toemail = form.cleaned_data.get('email')
            email = EmailMessage(subject, message, 'mail@jpzhou.me', to=[toemail])
            email.send()
            # Get the user's preferred channels from the multiple choice
            picked = form.cleaned_data.get('picked')
            user = User.objects.get(username=form.cleaned_data.get('username'))
            user_profile = user.userprofile
            user_profile.channel_like = picked
            user_profile.save()
            return render(request, 'registration/please_confirm.html')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


# This page offer a form for the user to change the channel he likes
def change_like_channel(request):
    if request.method == 'POST':
        form = ChangeChannelForm(request.POST)
        if form.is_valid() and request.user.is_authenticated():
            current_user = request.user
            user = User.objects.get(username=current_user.username)
            user_profile = user.userprofile
            picked = form.cleaned_data.get('picked')
            user_profile.channel_like = picked
            user_profile.save()
            return render(request, 'registration/channel_change_success.html')
        else:
            pass
    else:
        form = ChangeChannelForm()
    return render(request, 'registration/change_like_channel.html', {'form': form})

# This function will check token if it valid then user will active and login
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        # This allow the user to log in
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
        return render(request, 'registration/activ_valid.html')
    else:
        return render(request, 'registration/activ_invalid.html')


# Save the corresponding profile automatically when the User is saved
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        print("The corresponding user_profile is created!")


def contact(request):
    return render(request, 'news/contact.html')

def finance(request):
    news_list = News.objects.filter(category="finance").reverse()
    paginator = Paginator(news_list, 11)
    page = request.GET.get('page', 1)
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)

    # res_news = []
    # for news_it in news:
    #     if (news_it.category == "finance"):
    #         res_news.append(news_it)
    return render(request, 'news/news_list_finance.html', {'news': news})

def technology(request):
    news_list = News.objects.filter(category="tech").reverse()
    paginator = Paginator(news_list, 8)
    page = request.GET.get('page', 1)
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)
    return render(request, 'news/news_list_tech.html', {'news': news})

def sports(request):
    news_list = News.objects.filter(category="sports")
    paginator = Paginator(news_list, 8)
    page = request.GET.get('page', 1)
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)
    return render(request, 'news/news_list_sports.html', {'news': news})

def education(request):
    news_list = News.objects.filter(category="edu")
    paginator = Paginator(news_list, 8)
    page = request.GET.get('page', 1)
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)
    return render(request, 'news/news_list_education.html', {'news': news})


def important_news(request):
    news_list = News.objects.filter(category="news")
    paginator = Paginator(news_list, 8)
    page = request.GET.get('page', 1)
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)
    return render(request, 'news/news_list_important_news.html', {'news': news})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })