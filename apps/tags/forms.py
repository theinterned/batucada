from taggit.forms import TagWidget, TagField

class GeneralTagField(TagField):
   widget = TagWidget

   def clean(self, value):
       value = super(GeneralTagField, self).clean(value)
       value = [i.lower() for i in value]
       return value