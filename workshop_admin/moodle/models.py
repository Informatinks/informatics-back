from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils.functional import cached_property


class Role(models.Model):
    shortname = models.CharField(max_length=100)

    superuser_roles = (
        'admin',
    )

    staff_roles = (
        'coursecreator',
        'editingteacher',
    )

    class Meta:
        managed = False
        db_table = 'mdl_role'


class RoleAssignment(models.Model):
    role = models.ForeignKey('Role', models.DO_NOTHING, blank=True, null=True, db_column='roleid')
    user = models.ForeignKey('MoodleUser', models.DO_NOTHING, blank=True, null=True, db_column='userid')

    class Meta:
        managed = False
        db_table = 'mdl_role_assignments'


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        raise ValueError('Сегодня без пользователей')

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        raise ValueError('Сегодня без пользователей')


class MoodleUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    roles = models.ManyToManyField(Role, related_name='users', verbose_name='Роли', through=RoleAssignment)

    objects = UserManager()

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'username'
    is_anonymous = False
    is_authenticated = True
    is_active = True  # TODO

    def get_username(self):
        """Get human-readable user full name.

        Used in Grapelli navbar, generate complex
        name instead of plain username.

        :return: String representation for navbar
        """
        return f'{self.firstname} {self.username} {self.lastname}'

    @cached_property
    def is_staff(self):
        is_staff = any(map(lambda r: r.shortname in (Role.staff_roles + Role.superuser_roles),
                           self.roles.all()))
        return self.is_superuser or is_staff

    @cached_property
    def is_superuser(self):
        is_superuser = any(map(lambda r: r.shortname in Role.superuser_roles,
                               self.roles.all()))
        return is_superuser

    def has_perm(self, *__, **___):
        return self.is_staff

    def has_module_perms(self, *__):
        return True

    def __str__(self):
        return f'#{self.pk} {self.firstname} {self.lastname} ({self.username})'

    class Meta:
        managed = False
        db_table = 'mdl_user'


class Statement(models.Model):
    name = models.CharField(max_length=256)
    summary = models.TextField()

    class Meta:
        managed = False
        db_table = 'mdl_statements'


class CourseModule(models.Model):
    instance = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'mdl_course_modules'
