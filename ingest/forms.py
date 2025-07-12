from django import forms

class TranscriptTSVUploadForm(forms.Form):
    tsv_file = forms.FileField(label="Upload .tsv file")
    year = forms.ChoiceField(
        choices=[(i, f'Year {i}') for i in range(1, 6)],
        label="Select Year"
    )
