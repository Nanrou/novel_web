from django.forms import Form, CharField, PasswordInput, EmailField
from captcha.fields import CaptchaField


class DisablePlaceholder(CharField):
    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['placeholder'] = ''
        attrs['error_messages'] = '这里忘记填了喔'
        return attrs


class LocalEmailField(DisablePlaceholder, EmailField):
    pass


class FormBase(Form):
    username = DisablePlaceholder(max_length=16, label='用户名')
    password = DisablePlaceholder(max_length=16, widget=PasswordInput, label='密码')


class SignInForm(FormBase):
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'}, label='验证码')


class SignUpForm(SignInForm):
    email = LocalEmailField(label='邮箱地址')
    invite_code = DisablePlaceholder(max_length=8, label='邀请码')
    field_order = ['username', 'password', 'email', 'invite_code', 'captcha']
