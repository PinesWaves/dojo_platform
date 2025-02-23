from django import forms
from django.utils.safestring import mark_safe

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

        switch_html = f'''
        <div class="custom-control custom-switch custom-switch-on-danger">
            {checkbox_html}
            <label class="custom-control-label" for="{switch_id}">
                {self.label_text} {"" if not a_text else f'<a href="{a_url}" target="_blank">{a_text}</a>'}
            </label>
        </div>
        '''
        return mark_safe(switch_html)
