from django import forms
import os
from .models import Course

class TranscriptTSVUploadForm(forms.Form):
    tsv_file = forms.FileField(label="Upload .tsv file")
    
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        label="Select Course",
        required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile'):
            # Filter courses by user's schools
            self.fields['course'].queryset = Course.objects.filter(
                schools__in=user.profile.schools.all()
            ).distinct()
        else:
            self.fields['course'].queryset = Course.objects.none()


class CanvasJSONUploadForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.none())
    zip_file = forms.FileField(label='Upload ZIP of Canvas JSON files')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and hasattr(user, 'profile'):
            self.fields['course'].queryset = (
                Course.objects.filter(schools__in=user.profile.schools.all())
                .distinct()
                .order_by('code', 'title')  # Alphanumeric ordering
            )
        else:
            self.fields['course'].queryset = Course.objects.none()

    def clean_zip_file(self):
        file = self.cleaned_data['zip_file']
        ext = os.path.splitext(file.name)[1].lower()
        if ext != '.zip':
            raise forms.ValidationError("Only .zip files are allowed.")
        return file


from django import forms
from .models import YouTubeVideo, Course

class YouTubeUploadForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=True)
    url = forms.URLField(label="YouTube URL", required=True)
    title = forms.CharField(label="Video Title", required=False)
    transcript = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 20, "cols": 80}),
        help_text="Paste the transcript here."
    )
