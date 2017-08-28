#! -*- coding:utf-8 -*-

from django.forms import ModelForm, modelformset_factory
from .models import FormTest
from captcha.fields import CaptchaField


class TestForm(ModelForm):
    captcha = CaptchaField(error_messages={"invalid": "验证码错误"})

    class Meta:
        model = FormTest
        fields = '__all__'

TestFormSet = modelformset_factory(FormTest, fields='__all__')
