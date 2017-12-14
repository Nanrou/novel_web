from django.forms import Form, CharField, PasswordInput,EmailField
from captcha.fields import CaptchaField


class FormBase(Form):
    username = CharField(max_length=16, empty_value='请输入用户名')
    password = CharField(max_length=16, widget=PasswordInput)


class SignInForm(FormBase):
    captcha = CaptchaField(error_messages={'invalid': '验证码错误'})


class SignUpForm(SignInForm):
    email = EmailField()
    invite_code = CharField(max_length=8, empty_value='请输入邀请码')
