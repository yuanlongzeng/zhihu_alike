from django import forms
from django.contrib.auth.forms import UserCreationForm

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator,RegexValidator

from zhihu.models import Answer, UserProfile


def validate_email_phone(value):
    if '@' in value:  #邮箱
        # raise ValidationError(u'请输入正确格式的邮箱:' + value)
        return EmailValidator
    else:
        return RegexValidator(regex="1\d{10}")
class LoginForm(forms.Form):
    account = forms.CharField(max_length=50)
    password = forms.CharField(min_length=6,max_length=30)

class RegisterForm(UserCreationForm):

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'nick_name', 'password1', 'password2',)

class AnswerForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ['content', 'content_text']
        widgets = {
            'content': forms.Textarea(attrs={'style': 'display:none'}),
            'content_text': forms.Textarea(attrs={'style': 'display:none'}),
        }

