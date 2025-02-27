from django import forms
from django.core.exceptions import ValidationError

from config.widgets import CustomSwitchWidget, CustomDatePickerWidget
from config.config_vars import regulations, informed_consent
from .models import User, Category


class UserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    cardio_prob = forms.BooleanField(
        widget=CustomSwitchWidget(
            label_text="Do you have any cardiovascular problems?",
        ),
        required=False
    )
    injuries = forms.BooleanField(
        widget=CustomSwitchWidget(
            label_text="Have you had any injuries in the last 6 months?",
        ),
        required=False
    )
    physical_limit = forms.BooleanField(
        widget=CustomSwitchWidget(
            label_text="Do you have any physical limitations?",
        ),
        required=False
    )
    lost_cons = forms.BooleanField(
        widget=CustomSwitchWidget(
            label_text="Have you lost consciousness or lost balance after feeling dizzy?",
        ),
        required=False
    )
    sec_recom = forms.BooleanField(
        widget=CustomSwitchWidget(
            label_text="I will follow the instructor's recommendations and safety rules during the classes.",
        ),
        required=True
    )
    agreement = forms.BooleanField(
        widget=CustomSwitchWidget(
            label_text="I have read, understand the questions, completed and answered the questionnaire with my acceptance?",
        ),
        required=True
    )
    accept_regulations = forms.BooleanField(
        widget=CustomSwitchWidget(
            label_text="I accept the ",
            a_tag=('Regulations', regulations)
        ),
        required=True
    )
    accept_inf_cons = forms.BooleanField(
        widget=CustomSwitchWidget(
            label_text="I accept the ",
            a_tag=('Informed consent', informed_consent)
        ),
        required=True
    )
    birth_date = forms.DateField(
        widget=CustomDatePickerWidget(
            label_text="Birth Date",
        ),
        required=True
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'id_type', 'id_number', 'birth_date', 'birth_place', 'profession',
            'email', 'phone_number', 'country', 'city', 'address', 'parent', 'parent_phone_number', 'password1',
            'password2', 'eps', 'physical_cond', 'medical_cond', 'drug_cons', 'allergies', 'other_activities',
            'cardio_prob','injuries', 'physical_limit', 'lost_cons', 'sec_recom', 'agreement',
        ]
        labels = {
            "birth_date": "",
            "cardio_prob": "",
            "injuries": "",
            "physical_limit": "",
            "lost_cons": "",
            "sec_recom": "",
            "agreement": "",
            "accept_regulations": "",
            "accept_inf_cons": ""
        }

    def __init__(self, *args, **kwargs):
        # Extraemos el usuario actual del contexto si es pasado
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return password2

    def clean_category(self):
        category = self.cleaned_data['category']
        # Verificar si el usuario actual tiene permiso para cambiar la categoría
        if 'category' in self.changed_data and not self.request_user.is_sensei:
            raise forms.ValidationError("Only users with category 'Sensei' can change the category.")
        return category

    def clean_accept_regulations(self):
        accept = self.cleaned_data.get('accept_terms')
        if not accept:
            raise forms.ValidationError("You must accept the Regulations to continue.")
        return accept

    def clean_accept_inf_cons(self):
        accept = self.cleaned_data.get('accept_terms')
        if not accept:
            raise forms.ValidationError("You must accept the Informed Consent to continue.")
        return accept

    def save(self, commit=True):
        user = super().save(commit=False)
        # Establecer la contraseña usando set_password para encriptarla
        user.set_password(self.cleaned_data["password1"])
        user.category = Category.ESTUDIANTE
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'id_type', 'id_number', 'birth_date', 'birth_place', 'profession', 'eps',
            'phone_number', 'address', 'email', 'parent', 'parent_phone_number', 'category',
        ]
