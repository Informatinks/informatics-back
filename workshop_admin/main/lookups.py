from ajax_select import register, LookupChannel
from moodle.models import MoodleUser, Statement, CourseModule


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


@register('statement_lookup')
class StatementLookup(LookupChannel):
    model = Statement

    def get_query(self, q, request):
        try:
            id = int(q)
            return self.find_by_course_module(id)
        except:
            return self.model.objects.filter(name__icontains=q)

    def format_match(self, item):
        # Force cast to str repr as object will be used directry as value of serializable dict,
        # and __str__ or __repr__ methods will not be pre-called. Plan HTML alse can be supplied.
        return item.name

    def format_item_display(self, item):
        return item.name

    def can_add(self, user, model):
        return False

    def find_by_course_module(self, id):
        cm = CourseModule.objects.filter(id=id).first()

        if cm is None:
            return []

        instance_id = cm.instance
        return self.model.objects.filter(id=instance_id)
