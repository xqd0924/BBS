from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from blog import models

class RegForms(forms.Form):
    username = forms.CharField(min_length=3, max_length=8, label='用户名',
                               error_messages={'min_length': '太短了', 'max_length': '太长了',
                                               'required': '该字段必填'},
                               widget=widgets.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(min_length=3, max_length=8, label='密码',
                               error_messages={'min_length': '太短了', 'max_length': '太长了',
                                               'required': '该字段必填'},
                               widget=widgets.PasswordInput(attrs={'class': 'form-control'}))
    re_pwd = forms.CharField(min_length=3, max_length=8, label='确认密码',
                             error_messages={'min_length': '太短了', 'max_length': '太长了',
                                             'required': '该字段必填'},
                             widget=widgets.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='邮箱', error_messages={'invalid': '不是邮箱格式', 'required': '该字段必填'},
                             widget=widgets.EmailInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        name = self.cleaned_data.get('username')
        user = models.UserInfo.objects.filter(username=name).first()
        if user:
            raise ValidationError('该用户名已经被注册')
        else:
            return name

    def clean(self):
        pwd = self.cleaned_data.get('password')
        re_pwd = self.cleaned_data.get('re_pwd')
        if pwd == re_pwd:
            return self.cleaned_data
        else:
            raise ValidationError('两次密码不一致')
