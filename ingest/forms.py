from django import forms

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
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        label="Select Course",
        required=True
    )
