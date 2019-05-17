from ajax_select import register, LookupChannel
from moodle.models import MoodleUser


@register('moodleuser_lookup')
class MoodleUserLookup(LookupChannel):
    model = MoodleUser

    def get_query(self, q, request):
        return self.model.objects.filter(username=q).order_by('lastname')[:1]

    def format_match(self, item):
        # Force cast to str repr as object will be used directry as value of serializable dict,
        # and __str__ or __repr__ methods will not be pre-called. Plan HTML alse can be supplied.
        return str(item)

    def format_item_display(self, item):
        return str(item)
