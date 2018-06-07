from django import forms

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator,RegexValidator

from zhihu.models import Answer


def validate_email_phone(value):
    if '@' in value:  #邮箱
        # raise ValidationError(u'请输入正确格式的邮箱:' + value)
        return EmailValidator
    else:
        return RegexValidator(regex="1\d{10}")
class LoginForm(forms.Form):
    account = forms.CharField(max_length=50)
    password = forms.CharField(min_length=6,max_length=30)

class AnswerForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ['content', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'style': 'display:none'}),
            'content': forms.Textarea(attrs={'style': 'display:none'}),
        }

