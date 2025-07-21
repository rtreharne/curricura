from django import forms
import os

class TranscriptTSVUploadForm(forms.Form):
    tsv_file = forms.FileField(label="Upload .tsv file")
    
    course_code = forms.CharField(
        max_length=20,
        label="Course Code",
        required=True
    )

    course_title = forms.CharField(
        max_length=255,
        label="Course Title",
        required=True
    )

    year = forms.ChoiceField(
        choices=[(i, f'Year {i}') for i in range(1, 6)],
        label="Select Year"
    )

from .models import Course


class CanvasJSONUploadForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all())
    zip_file = forms.FileField(label='Upload ZIP of Canvas JSON files')

    def clean_zip_file(self):
        file = self.cleaned_data['zip_file']
        ext = os.path.splitext(file.name)[1].lower()
        if ext != '.zip':
            raise forms.ValidationError("Only .zip files are allowed.")
        return file
