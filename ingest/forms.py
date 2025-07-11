from django import forms
from .models import TranscriptUpload

class TranscriptUploadForm(forms.ModelForm):
    class Meta:
        model = TranscriptUpload
        fields = ['file', 'description', 'year']
