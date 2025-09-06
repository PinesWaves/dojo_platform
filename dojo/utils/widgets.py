from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.dateformat import format as django_date_format
from datetime import date, datetime


class CustomSwitchWidget(forms.CheckboxInput):
    def __init__(self, label_text, a_tag=(None, None), *args, **kwargs):
        self.label_text = label_text
        self.a_tag = a_tag
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        switch_id = attrs.get("id", name)  # Get ID or use name
        attrs["class"] = "custom-control-input"  # Ensure Bootstrap styling

        checkbox_html = super().render(name, value, attrs)
        a_text, a_url = self.a_tag
        link = f'<a href="{a_url}" target="_blank">{a_text}</a>' if a_text else ''
        switch_html = f'''
        <div class="custom-control custom-switch custom-switch-on-danger">
            {checkbox_html}
            <label class="custom-control-label" for="{switch_id}">
                {self.label_text} {link}
            </label>
        </div>
        '''
        return mark_safe(switch_html)


class CustomDatePickerWidget(forms.DateInput):
    def __init__(self, label_text=None, attrs=None, format='%m/%d/%Y'):
        self.label_text = label_text or ""
        final_attrs = {'required': 'required'}
        if attrs:
            final_attrs.update(attrs)
        super().__init__(attrs=final_attrs, format=format)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        datepicker_id = attrs.get("id", name)  # Get ID or use name

        if isinstance(value, (datetime, date)):
            value = value.strftime(self.format)

        existing_class = attrs.get("class", "")
        attrs["class"] = f"{existing_class} form-control datetimepicker-input".strip()
        # attrs["class"] = "form-control datetimepicker-input"
        attrs["data-target"] = f"#{datepicker_id}"
        attrs["data-toggle"] = "datetimepicker"

        input_html = super().render(name, value, attrs, renderer)
        # checkbox_html = super().render(name, value, attrs)

        # label_html = f"<label>{self.label_text}</label>" if self.label_text else ""
        html = f"""
            <div class="input-group date" id="{datepicker_id}" data-target-input="nearest">
                {input_html}
                <div class="input-group-append" data-target="#{datepicker_id}" data-toggle="datetimepicker">
                    <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                </div>
            </div>
        """
        return mark_safe(html)
