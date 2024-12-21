from django import forms
from .models import Affiliation, Workplace

class WorkplaceForm(forms.ModelForm):
    class Meta:
        model = Workplace
        fields = ['name', 'affiliation', 'body', 'media', 'coordinates']
        labels = {
            'name': 'Çalışma Alanı Adı',
            'affiliation': 'Bağlantılı Kurum',
            'body': 'Açıklama',
            'media': 'Medya (Video veya Dosya)',
            'coordinates': 'Sandalye Koordinatları'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if not user.is_superuser:
                affiliation = Affiliation.objects.get(name=user.affiliation)
                self.fields['affiliation'].initial = affiliation
                self.fields['affiliation'].widget.attrs['disabled'] = 'disabled'
            else:
                self.fields['affiliation'].widget.attrs['disabled'] = False

        
        self.fields['coordinates'].widget.attrs.update({
            'placeholder': 'Koordinatlar JSON formatında girin (örneğin: [[180, 100, 280, 300]])'
        })
        self.fields['coordinates'].help_text = 'Sandalyelerin koordinatlarını JSON formatında girin.'
