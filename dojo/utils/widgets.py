from django import forms
from django.utils.safestring import mark_safe
from django.utils.dateformat import format as django_date_format
from datetime import date, time, datetime


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


class CustomDateTimePickerWidget(forms.DateTimeInput):
    def __init__(self, label_text=None, picker_type="date-time", attrs=None):
        if picker_type not in ["date", "time", "date-time"]:
            raise ValueError("picker_type must be 'date', 'time', or 'date-time'")
        else:
            picker_format = 'm/d/Y H:M'
            self.suffix = "_datetimepicker"
            if picker_type == "date":
                picker_format = 'm/d/Y'
                self.suffix = "_datepicker"
            elif picker_type == "time":
                picker_format = 'H:M'
                self.suffix = "_timepicker"

        self.label_text = label_text or ""
        final_attrs = {'required': 'required'}
        if attrs:
            final_attrs.update(attrs)
        super().__init__(attrs=final_attrs, format=picker_format)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        picker_id = f"{name}{self.suffix}"
        if isinstance(value, (datetime, date, time)):
            value = django_date_format(value, self.format)

        existing_class = attrs.get("class", "")
        attrs["class"] = f"{existing_class} form-control datetimepicker-input".strip()
        attrs["data-target"] = f"#{picker_id}"
        attrs["data-toggle"] = "datetimepicker"

        input_html = super().render(name, value, attrs, renderer)
        html = f"""
            <div class="input-group datetime" id="{picker_id}" data-target-input="nearest">
                {input_html}
                <div class="input-group-append" data-target="#{picker_id}" data-toggle="datetimepicker">
                    <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                </div>
            </div>
        """
        return mark_safe(html)


class CustomSelectMultipleWidget(forms.SelectMultiple):
    """
    Custom widget for Bootstrap Duallistbox.
    Renders a multiple select with the proper class.
    """

    def __init__(self, attrs=None):
        default_attrs = {
            "class": "duallistbox",
            "required": "required"
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
