from django import forms
from django.core.exceptions import ValidationError
from config.config_vars import regulations, informed_consent
from .models import User, Category
from django.utils.safestring import mark_safe


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

    accept_regulations = forms.BooleanField(
        label=mark_safe(f'I accept the <a href="{regulations}" target="_blank">Regulations</a>'),
        widget=forms.CheckboxInput(attrs={'class': 'form-control'}),
        required=True
    )

    accept_inf_cons = forms.BooleanField(
        label=mark_safe(f'I accept the <a href="{informed_consent}" target="_blank">Informed consent</a>'),
        widget=forms.CheckboxInput(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'id_type', 'id_number', 'birth_date', 'birth_place', 'profession', 'eps',
            'phone_number', 'address', 'city', 'country', 'email', 'parent', 'parent_phone_number', 'password1',
            'password2', 'accept_inf_cons', 'medical_cond', 'drug_cons', 'allergies', 'other_activities', 'cardio_prob',
            'injuries', 'physical_limit', 'lost_cons', 'physical_cond', 'sec_recom', 'agreement'
        ]
        exclude = ['accept_regulations', 'accept_inf_cons']

    def __init__(self, *args, **kwargs):
        # Extraemos el usuario actual del contexto si es pasado
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

        # Si no es un usuario Sensei, deshabilitar el campo `categoria`
        # if not self.request_user or not self.request_user.is_sensei:
        #     self.fields['category'].disabled = True

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
