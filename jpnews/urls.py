from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    #only an empty string will match
    url(r'^$', views.news_list, name='news_list'), 
    # URL for recording the history
    url(r'^record/', views.record_history, name='record_history'), 
    # URL for recommending the news
    url(r'^news_recommend/$', views.news_recommend, name='news_recommend'),
    # URL for viewing the history
    url(r'^history/$', views.news_history, name='history'), 
    # URL for updating the news
    # url(r'^news_update/$', views.news_update, name='news_update'),
    # URL for sign up
    url(r'^signup/$', views.signup, name='signup'),
    # URL for activating the email of the account after the user sign up
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    # URL for log in and log out
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    # URL for reset the password
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    # URL for change passwd
    url(r'^change_password/$', views.change_password, name='change_password'),
    # URL for contact information
    url(r'^contact/$', views.contact, name='contact'),
    # URL for news of different categories
    url(r'^finance/$', views.finance, name='finance'),
    url(r'^technology/$', views.technology, name='technology'),
    url(r'^sports/$', views.sports, name='sports'),
    url(r'^education/$', views.education, name='education'),
    url(r'^important_news/$', views.important_news, name='important_news'),
    url(r'^change_like_channel/$', views.change_like_channel, name='change_like_channel'),
]