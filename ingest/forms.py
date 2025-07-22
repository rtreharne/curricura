from django import forms
import os
from .models import Course
import json

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

import json
from django import forms
from .models import Course  # Adjust import as needed


class YouTubeUploadForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=True)
    url = forms.URLField(label="YouTube URL", required=False)  # No longer required
    json_file = forms.FileField(
        label="JSON file (list of YouTube URLs)",
        required=False,
        help_text="Upload a JSON file containing an array of YouTube links."
    )

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        json_file = cleaned_data.get('json_file')

        # Ensure that at least one of URL or JSON file is provided
        if not url and not json_file:
            raise forms.ValidationError(
                "Please provide either a YouTube URL or upload a JSON file."
            )

        # Validate the JSON file
        if json_file:
            try:
                # Read and decode the uploaded JSON file
                content = json_file.read().decode("utf-8")
                json_file.seek(0)  # Reset pointer for future use
                data = json.loads(content)

                # Ensure the JSON content is a list of strings
                if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
                    raise forms.ValidationError(
                        "The JSON file must contain a list of YouTube URL strings."
                    )

                # Attach the validated list to cleaned_data
                cleaned_data['json_links'] = data

            except json.JSONDecodeError as e:
                raise forms.ValidationError(
                    f"Invalid JSON file. JSON parsing error: {e.msg}"
                )

        return cleaned_data
