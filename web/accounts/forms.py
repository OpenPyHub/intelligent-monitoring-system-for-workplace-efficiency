from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from pages.models import Affiliation

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=50, label='Kullanıcı adı',
                               help_text='<ul><li>Boş bırakılamaz.</li><li>Maksimum 50 karakter olmalıdır.</li><li>Sadece harf, rakam ve @/./+/-/_ karakterlerini içermelidir.</li></ul>',)
    password1 = forms.CharField(label='Şifre:',
                                help_text='<ul><li>Boş bırakılamaz.</li><li>Diğer kişisel bilgilerinizle aynı olmamalıdır.</li><li>En az 8 karakterden oluşmalıdır.</li><li>Yaygın bir şifre olmamalıdır. (Örn.: "abcd1234")</li><li>Tamamen rakam içermemelidir.</li></ul>',
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label='Şifre Tekrar:',
                                help_text='Şifreyi doğrulayın.',
                                widget=forms.PasswordInput)
    affiliation = forms.ModelChoiceField(
        queryset=Affiliation.objects.all(),
        required=False,
        label='Bağlı olduğu kurum/kuruluş',
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'affiliation', 'password1', 'password2')
        labels = {
            'email': 'E-posta',
            'first_name': 'Ad',
            'last_name': 'Soyad',
        }
