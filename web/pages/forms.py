from django import forms
from .models import Workplace

class WorkplaceForm(forms.ModelForm):
    class Meta:
        model = Workplace
        fields = ['name', 'affiliation', 'body', 'media']
        labels = {
            'name': 'Çalışma Alanı Adı',
            'affiliation': 'Bağlantılı Kurum',
            'body': 'Açıklama',
            'media': 'Medya (Video veya Dosya)',
        }
