import random
import string

from django.db import models
from utils.types import DateTimeBasedDuration

from informatics_front.utils.enums import WorkshopStatus, WorkshopVisibility, WorkshopConnectionStatus, \
    WorkshopMonitorType, WorkshopMonitorUserVisibility, ContestProtocolVisibility

ACCESS_TOKEN_LENGTH = 32

CONTEST_PROTOCOL_VISIBILLITY_CHOICES = (
    (ContestProtocolVisibility.FULL.value, 'Полностью'),
    (ContestProtocolVisibility.FIRST_BAD_TEST.value, 'До первого непройденного теста'),
    (ContestProtocolVisibility.INVISIBLE.value, 'Не виден'),
)

WORKSHOP_MONITOR_USER_VISIBILLITY_CHOICES = (
    (WorkshopMonitorUserVisibility.FOR_USER_ONLY.value, 'Ученик видит свои результаты'),
    (WorkshopMonitorUserVisibility.FULL.value, 'Ученик видит все результаты'),
    (WorkshopMonitorUserVisibility.DISABLED_FOR_STUDENT.value, 'Ученик не видит результаты'),
)

WORKSHOP_CONNECTION_STATUS_CHOICES = (
    (WorkshopConnectionStatus.APPLIED.value, 'Новый'),
    (WorkshopConnectionStatus.ACCEPTED.value, 'Одобрен'),
    (WorkshopConnectionStatus.DISQUALIFIED.value, 'Отчислен'),
    (WorkshopConnectionStatus.REJECTED.value, 'Отклонен'),
    (WorkshopConnectionStatus.PROMOTED.value, 'Редактор'),
)

WORKSHOP_STATUS_CHOICES = (
    (WorkshopStatus.DRAFT.value, 'Черновик'),
    (WorkshopStatus.ONGOING.value, 'Опубликованный'),
)

WORKSHOP_VISIBILITY_CHOICES = (
    (WorkshopVisibility.PUBLIC.value, 'Открытый'),
    (WorkshopVisibility.PRIVATE.value, 'Приватный'),
)

WORKSHOP_MONITOR_TYPE_CHOICES = (
    (WorkshopMonitorType.IOI.value, 'IOI'),
    (WorkshopMonitorType.ACM.value, 'ACM'),
    (WorkshopMonitorType.LightACM.value, 'LightACM'),
)


class Contest(models.Model):
    workshop = models.ForeignKey('Workshop', models.DO_NOTHING, blank=True, null=True)
    statement = models.ForeignKey('moodle.Statement', on_delete=models.DO_NOTHING, blank=True, null=True,
                                  help_text='ID можно найти в ссылке на Informatics. '
                                             'Зайдите в нужный стейтмент и скопируйте его из URL. '
                                             'Пример: https://informatics.msk.ru/mod/statements/view.php?id=2296. '
                                             '2296 будет ID стейтмента.',
                                  verbose_name='ID стейтмента')
    author = models.ForeignKey('moodle.MoodleUser', blank=True, null=True, on_delete=models.CASCADE, editable=False)
    position = models.PositiveIntegerField(default=0, blank=False, null=False)
    is_virtual = models.BooleanField(default=False)
    protocol_visibility = models.IntegerField(choices=CONTEST_PROTOCOL_VISIBILLITY_CHOICES,
                                              blank=False, null=False)
    time_start = models.DateTimeField()
    time_stop = models.DateTimeField()
    virtual_duration = DateTimeBasedDuration(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contest'

        verbose_name = 'Контест'
        verbose_name_plural = 'Контесты'

    def __str__(self):
        return self.statement.name


class ContestConnection(models.Model):
    user = models.ForeignKey('moodle.MoodleUser', blank=True, null=True, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contest_connection'
        unique_together = (('user', 'contest'),)


class RefreshToken(models.Model):
    token = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    valid = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'refresh_token'


def generate_access_token():
    """Generate workshop access token when workshop is created from admin panel.

    Access token is 32-length digit-letter string.
    """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=ACCESS_TOKEN_LENGTH))


class Workshop(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    status = models.IntegerField(choices=WORKSHOP_STATUS_CHOICES, verbose_name='Статус')
    visibility = models.IntegerField(choices=WORKSHOP_VISIBILITY_CHOICES,
                                     verbose_name='Видимость')
    access_token = models.CharField(max_length=ACCESS_TOKEN_LENGTH, blank=False, null=False,
                                    verbose_name='Токен безопасности',
                                    default=generate_access_token,
                                    help_text='Токен генерируется автоматически.'
                                              'Он будет содержаться в ссылке на воркшоп, которую получат ученики.', )
    owner = models.ForeignKey('moodle.MoodleUser', blank=True, null=True,
                              on_delete=models.CASCADE, verbose_name='Создатель')

    def add_connection(self, user: 'MoodleUser'):
        wc = WorkshopConnection(user=user,
                                workshop=self,
                                status=WorkshopConnectionStatus.PROMOTED.value)
        wc.save()

    class Meta:
        managed = False
        db_table = 'workshop'

        verbose_name = 'Сбор'
        verbose_name_plural = 'Сборы'

    def __str__(self):
        status = WorkshopStatus(self.status).name if self.status else ''
        return f'#{self.pk} {self.name} ({status})'


class WorkshopConnection(models.Model):
    user = models.ForeignKey('moodle.MoodleUser', blank=True, null=True, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    workshop = models.ForeignKey(Workshop, models.DO_NOTHING, related_name='connections', verbose_name='Сбор')
    status = models.IntegerField(choices=WORKSHOP_CONNECTION_STATUS_CHOICES, verbose_name='Статус приглашения')

    def __str__(self):
        status = WorkshopConnectionStatus(self.status).name if self.status else ''
        return f'{self.user} - {self.workshop.name} ({status})'

    class Meta:
        managed = False
        db_table = 'workshop_connection'
        unique_together = (('user', 'workshop'),)

        verbose_name = 'Приглашение'
        verbose_name_plural = 'Приглашения'


class WorkshopMonitor(models.Model):
    workshop = models.OneToOneField(Workshop, models.DO_NOTHING)
    type = models.IntegerField(choices=WORKSHOP_MONITOR_TYPE_CHOICES,
                               null=False, blank=False,
                               default=WorkshopMonitorType.ACM.value)
    user_visibility = models.IntegerField(choices=WORKSHOP_MONITOR_USER_VISIBILLITY_CHOICES)
    freeze_time = models.DateTimeField(null=True, blank=True)

    # Depricated in favour of 'type'
    # with_penalty_time = models.BooleanField(default=False)

    def __str__(self):
        type = WorkshopMonitorType(self.type).name if self.type else ''
        return f'Монитор {type} ({self.workshop_id}# {self.workshop.name})'

    class Meta:
        managed = False
        db_table = 'contest_monitor'

        verbose_name = 'Монитор'
        verbose_name_plural = 'Мониторы'
