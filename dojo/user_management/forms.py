from django import forms
from django.core.exceptions import ValidationError

from config.widgets import CustomSwitchWidget, CustomDatePickerWidget
from config.config_vars import regulations, informed_consent
from .models import User, Category


class UserRegisterForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=CustomDatePickerWidget(
            label_text="Birth Date",
        ),
        required=True
    )
    country = forms.CharField(
        widget=forms.Select(
            attrs={
                'class': 'selectpicker countrypicker',
                # 'data-flag': 'true',
                'data-default': 'CO',
            }
        ),
        required=True
    )
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
    date_joined = forms.DateField(
        widget=CustomDatePickerWidget(
            label_text="Date joined",
        ),
        required=True
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'id_type', 'id_number', 'gender', 'birth_date', 'birth_place', 'profession',
            'email', 'phone_number', 'country', 'city', 'address', 'parent', 'parent_phone_number', 'password1',
            'password2', 'eps', 'date_joined', 'physical_cond', 'medical_cond', 'drug_cons', 'allergies',
            'other_activities', 'cardio_prob', 'injuries', 'physical_limit', 'lost_cons', 'sec_recom', 'agreement',
            'accept_regulations', 'accept_inf_cons'
        ]
        labels = {
            'birth_date': '',
            'physical_cond': 'Physical Condition',
            'medical_cond': 'Medical Condition',
            'drug_cons': 'Drug Consumption',
            'eps': 'EPS',
            'date_joined': '',
            'cardio_prob': '',
            'injuries': '',
            'physical_limit': '',
            'lost_cons': '',
            'sec_recom': '',
            'agreement': '',
            'accept_regulations': '',
            'accept_inf_cons': ''
        }

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Asegurar clase form-control (menos checkboxes o switches)
            class_attr = field.widget.attrs.get('class', '')
            if not isinstance(field.widget, forms.CheckboxInput) and 'form-control' not in class_attr:
                class_attr = (class_attr + ' form-control').strip()
            field.widget.attrs['class'] = class_attr

            # Obtener texto base para placeholder/label
            label_text = self.Meta.labels.get(field_name) if hasattr(self.Meta, 'labels') else None
            if not label_text:
                label_text = field.label or field_name.replace('_', ' ').title()

            # Si es un <select>, mantener label y no poner placeholder
            if isinstance(field.widget, forms.Select):
                field.label = label_text
                field.widget.attrs.pop('placeholder', None)
            else:
                # No es select: usar placeholder y quitar label
                field.widget.attrs['placeholder'] = label_text
                field.label = ''

            # Marcar campos con error
            if field_name in self.errors:
                field.widget.attrs['class'] += ' is-invalid'

    def clean(self):
        cleaned_data = super().clean()

        # Validación de campos obligatorios
        required_fields = [
            'first_name', 'last_name', 'id_type', 'id_number', 'gender',
            'birth_date', 'birth_place', 'profession', 'email', 'phone_number',
            'country', 'city', 'address', 'date_joined', 'eps',
            'physical_cond', 'medical_cond',
            'sec_recom', 'agreement', 'accept_inf_cons', 'accept_regulations',
            'password1', 'password2',
        ]

        # for field in required_fields:
        #     value = cleaned_data.get(field)
        #     if value in [None, '', False]:
        #         self.add_error(field, "This field is required.")

        # Validación de contraseña
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")

        # Validación del campo category si cambia
        category = cleaned_data.get("category")
        if category and 'category' in self.changed_data and self.request_user and not self.request_user.is_sensei:
            self.add_error("category", "Only users with category 'Sensei' can change the category.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Establecer la contraseña usando set_password para encriptarla
        user.set_password(self.cleaned_data["password1"])
        user.category = Category.ESTUDIANTE
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=CustomDatePickerWidget(),
        input_formats=['%m/%d/%Y'],
        required=False
    )
    country = forms.CharField(
        widget=forms.Select(
            attrs={
                'class': 'selectpicker countrypicker',
                'data-default': '',
            }),
        required=False
    )
    birth_place = forms.CharField(required=False)
    profession = forms.CharField(required=False)
    city = forms.CharField(required=False)
    parent = forms.CharField(required=False)
    parent_phone_number = forms.CharField(required=False)
    medical_cond = forms.CharField(required=False)
    drug_cons = forms.CharField(required=False)
    allergies = forms.CharField(required=False)
    other_activities = forms.CharField(required=False)
    cardio_prob = forms.BooleanField(required=False)
    injuries = forms.BooleanField(required=False)
    physical_limit = forms.BooleanField(required=False)
    lost_cons = forms.BooleanField(required=False)
    date_joined = forms.DateField(
        widget=CustomDatePickerWidget(
            label_text="Date joined",
        ),
        required=True
    )


    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'category', 'id_type', 'id_number', 'birth_date', 'birth_place', 'profession',
            'eps', 'date_joined', 'phone_number', 'address', 'city', 'country', 'email', 'level', 'parent', 'parent_phone_number',
            'medical_cond', 'drug_cons', 'allergies', 'other_activities', 'cardio_prob', 'injuries', 'physical_limit',
            'lost_cons'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            country_code = self.instance.country
            self.fields['country'].initial = country_code
            self.fields['country'].widget.attrs['data-default'] = country_code

        for field_name, field in self.fields.items():
            class_attr = field.widget.attrs.get('class', 'form-control')
            field.widget.attrs['class'] = class_attr
            if 'form-control' not in class_attr:
                field.widget.attrs['class'] += ' form-control'

            if field_name in self.errors:
                field.widget.attrs['class'] += ' is-invalid'

    def clean(self):
        cleaned_data = super().clean()
        instance = self.instance

        for field_name in self.fields:
            value = cleaned_data.get(field_name)
            if value in [None, '', []]:  # Si el valor es vacío
                previous_value = getattr(instance, field_name, None)
                cleaned_data[field_name] = previous_value  # Lo reemplaza por el valor anterior
                self.data = self.data.copy()  # Necesario para modificar self.data si se usa luego
                self.data[field_name] = previous_value  # Asegura que save() lo vea correctamente

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class ForgotPassForm(forms.Form):
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        required=True
    )


class RecoverPassForm(forms.Form):
    password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        }),
        required=True
    )
    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        }),
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return cleaned_data
