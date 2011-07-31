from django.forms import fields
from django.utils.translation import get_language

from ckeditor.widgets import CKEditorWidget as BaseCKEditorWidget

from richtext import clean_html, DEFAULT_CONFIG, CKEDITOR_CONFIGS


class CKEditorWidget(BaseCKEditorWidget):

    def __init__(self, config_name='default', *args, **kwargs):
        super(CKEditorWidget, self).__init__(config_name, *args, **kwargs)
        self.config_name = config_name

    def render(self, *args, **kwargs):
        self.config = DEFAULT_CONFIG.copy()
        self.config.update(CKEDITOR_CONFIGS[self.config_name])
        self.config['language'] = get_language()
        return super(CKEditorWidget, self).render(*args, **kwargs)


class RichTextFormField(fields.Field):
    def __init__(self, config_name='default', *args, **kwargs):
        self.config_name = config_name
        kwargs.update({'widget': CKEditorWidget(config_name=config_name)})
        super(RichTextFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(RichTextFormField, self).to_python(value)
        value = clean_html(self.config_name, value)
        if value and value.strip() in ('<br />', '<br>'):
            value = u''
        elif not value:
            value = u''
        return value
