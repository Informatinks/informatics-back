class MoodleRouter:
    def __init__(self):
        self._models = {
            'WorkshopConnection',
            'Workshop',
            'ContestConnection',
            'Contest',
        }

    def db_for_read(self, model, **hints):
        return 'default'

    def db_for_write(self, model, **hints):
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Disallow migrations for moodle tables
        if app_label == 'moodle':
            return False
        return True
