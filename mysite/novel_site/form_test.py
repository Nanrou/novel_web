#! -*- coding:utf-8 -*-

from django.forms import ModelForm, modelformset_factory
from .models import FormTest


class TestForm(ModelForm):
    class Meta:
        model = FormTest
        fields = '__all__'

TestFormSet = modelformset_factory(FormTest, fields='__all__')
