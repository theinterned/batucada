from ckeditor.fields import RichTextField as BaseRichTextField

from richtext.forms import RichTextFormField
from richtext import clean_html


class RichTextField(BaseRichTextField):

    def formfield(self, **kwargs):
        return super(RichTextField, self).formfield(
            form_class=RichTextFormField, **kwargs)

    def pre_save(self, model_instance, add):
        value = super(RichTextField, self).pre_save(model_instance, add)
        setattr(model_instance, self.attname, clean_html(self.config_name,
            value))
        return value
