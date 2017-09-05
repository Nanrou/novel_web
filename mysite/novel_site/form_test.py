#! -*- coding:utf-8 -*-

from django.contrib.auth.models import User
from django.forms import ModelForm, BaseForm, Form, CharField, EmailField, PasswordInput
from captcha.fields import CaptchaField

from .models import FormTest


class CaptchaForm(ModelForm):
    captcha = CaptchaField(error_messages={"invalid": "验证码错误"})

    class Meta:
        abstract = True


class TestForm(CaptchaForm):

    class Meta:
        model = FormTest
        fields = '__all__'


class SignInFormBase(Form):
    username = CharField(max_length=80)
    password = CharField(max_length=32, widget=PasswordInput)


class SignInForm(SignInFormBase):
    captcha = CaptchaField(error_messages={"invalid": "验证码错误"})


class SignUpForm(SignInFormBase):
    affirm_password = CharField(max_length=32, widget=PasswordInput)
    email = EmailField()
    captcha = CaptchaField(error_messages={"invalid": "验证码错误"})
