from django import forms

from dashboard.models import TrainingScheduling, Training, Kata, Kumite, Technique
from utils.widgets import CustomDateTimePickerWidget, CustomSelectMultipleWidget


class TrainingSchedulingForm(forms.ModelForm):
    time = forms.TimeField(
        widget=CustomDateTimePickerWidget(
            label_text="Time",
            picker_type="time"
        ),
        required=True
    )
    details = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
            }
        ),
        required=False
    )

    class Meta:
        model = TrainingScheduling
        fields = ['day_of_week', 'time', 'details']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['day_of_week'].widget.attrs['class'] = 'form-control select2'
    #     for field in self.fields.values():
    #         existing_classes = field.widget.attrs.get('class', '')
    #         field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()


class TrainingForm(forms.ModelForm):
    date = forms.DateTimeField(
        widget=CustomDateTimePickerWidget(
            label_text="Date and time",
            picker_type="date-time"
        ),
        required=True
    )
    details = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
            }
        ),
        required=False
    )
    techniques = forms.ModelMultipleChoiceField(
        queryset=Technique.objects.all(),
        widget=CustomSelectMultipleWidget(),
        required=False,
        label="Techniques"
    )
    katas = forms.ModelMultipleChoiceField(
        queryset=Kata.objects.all(),
        widget=CustomSelectMultipleWidget(),
        required=False,
        label="Katas"
    )
    kumites = forms.ModelMultipleChoiceField(
        queryset=Kumite.objects.all(),
        widget=CustomSelectMultipleWidget(),
        required=False,
        label="Kumite types"
    )

    class Meta:
        model = Training
        fields = ["date", "type", "status", "techniques", "details", "katas", "kumites"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].widget.attrs['class'] = 'form-control select2'
        self.fields['status'].widget.attrs['class'] = 'form-control select2'

    # def is_valid(self):
    #     # change date to timezone aware
    #     date = self.data.get('date')
    #     if date:
    #         from django.utils import timezone
    #         from django.conf import settings
    #         import pytz
    #         user_tz = pytz.timezone(settings.TIME_ZONE)
    #         naive_date = timezone.datetime.fromisoformat(date)
    #         aware_date = user_tz.localize(naive_date)
    #         self.data = self.data.copy()
    #         self.data['date'] = aware_date.isoformat()
    #     return super().is_valid()
