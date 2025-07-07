from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Order, Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('Ваш отзыв...')
            }),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
        labels = {
            'text': _(''),
            'rating': _('Оценка'),
        }


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput
    )
    confirm_password = forms.CharField(
        label=_('Подтвердите пароль'),
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['username', 'email', ]
        labels = {
            'username': _('Имя пользователя'),
            'email': _('Электронная почта'),
            'password': _('Пароль'),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError(_('Пароли не совпадают'))
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(label=_('Имя пользователя'))
    password = forms.CharField(label=_('Пароль'), widget=forms.PasswordInput)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'name', 'surname', 'phone', 'address', 'payment_method',
            'ip_address', 'country', 'region', 'city', 'isp', 'org',
            'latitude', 'longitude', 'user_agent'
        ]
        labels = {
            'name': _('Имя'),
            'surname': _('Фамилия'),
            'phone': _('Телефон'),
            'address': _('Адрес'),
            'payment_method': _('Способ оплаты'),
            'ip_address': _('IP-адрес'),
            'country': _('Страна'),
            'region': _('Регион'),
            'city': _('Город'),
            'isp': _('Провайдер'),
            'org': _('Организация'),
            'latitude': _('Широта'),
            'longitude': _('Долгота'),
            'user_agent': _('Устройство'),
        }
        widgets = {
            'address': forms.Textarea(attrs={
                'placeholder': _('Улица, дом, квартира'),
                'rows': 3
            }),
            'ip_address': forms.HiddenInput(),
            'country': forms.HiddenInput(),
            'region': forms.HiddenInput(),
            'city': forms.HiddenInput(),
            'isp': forms.HiddenInput(),
            'org': forms.HiddenInput(),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'user_agent': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hidden_fields = [
            'ip_address', 'country', 'region', 'city',
            'isp', 'org', 'latitude', 'longitude', 'user_agent'
        ]
        for field in hidden_fields:
            self.fields[field].required = False
