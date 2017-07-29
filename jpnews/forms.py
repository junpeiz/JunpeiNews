from django import forms
from .models import News
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from captcha.fields import CaptchaField

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    captcha = CaptchaField()

    CHOICES = (('经济金融', '经济金融'),
               ('科技动态', '科技动态'),
               ('体育新闻', '体育新闻'),
               ('教育风向', '教育风向'),
               ('近日要闻', '近日要闻'),)
    picked = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(u'Email address has already exists.')
        return email


class ChangeChannelForm(forms.Form):
    CHOICES = (('经济金融', '经济金融'),
               ('科技动态', '科技动态'),
               ('体育新闻', '体育新闻'),
               ('教育风向', '教育风向'),
               ('近日要闻', '近日要闻'),)
    picked = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple())
