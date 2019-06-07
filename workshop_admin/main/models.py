from django.db import models
from utils.types import DateTimeBasedDuration

from informatics_front.utils.enums import WorkshopStatus, WorkshopVisibility, WorkshopConnectionStatus, \
    WorkshopMonitorType, WorkshopMonitorUserVisibility, ContestProtocolVisibility

WORKSHOP_STATUS_CHOICES = tuple(((e.value, e.name) for e in WorkshopStatus))
WORKSHOP_VISIBILITY_CHOICES = tuple(((e.value, e.name) for e in WorkshopVisibility))
WORKSHOP_CONNECTION_STATUS_CHOICES = tuple(((e.value, e.name) for e in WorkshopConnectionStatus))
MONITOR_TYPE_CHOICES = tuple(((e.value, e.name) for e in WorkshopMonitorType))


monitor_user_visibility_human = {
    WorkshopMonitorUserVisibility.FOR_USER_ONLY: 'Ученик видит свои результаты',
    WorkshopMonitorUserVisibility.FULL: 'Ученик видит все результаты',
    WorkshopMonitorUserVisibility.DISABLED_FOR_STUDENT: 'Ученик не видит результаты'
}


MONITOR_USER_VISIBILITY_CHOICES = tuple(
    (e.value, monitor_user_visibility_human.get(e, e.name)) for e in WorkshopMonitorUserVisibility
)

PROTOCOL_VISIBILITY_CHOICES = tuple(((e.value, e.name) for e in ContestProtocolVisibility))


class Contest(models.Model):
    workshop = models.ForeignKey('Workshop', models.DO_NOTHING, blank=True, null=True)
    statement = models.ForeignKey('moodle.Statement', on_delete=models.DO_NOTHING, blank=True, null=True)
    author = models.ForeignKey('moodle.MoodleUser', blank=True, null=True, on_delete=models.CASCADE, editable=False)
    position = models.IntegerField(blank=True, null=True)
    protocol_visibility = models.IntegerField(choices=PROTOCOL_VISIBILITY_CHOICES,
                                              blank=False, null=False)
    time_start = models.DateTimeField()
    time_stop = models.DateTimeField()
    is_virtual = models.BooleanField(default=False)
    virtual_duration = DateTimeBasedDuration(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contest'


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


class Workshop(models.Model):
    name = models.CharField(max_length=255)
    status = models.IntegerField(choices=WORKSHOP_STATUS_CHOICES)
    visibility = models.IntegerField(choices=WORKSHOP_VISIBILITY_CHOICES)

    class Meta:
        managed = False
        db_table = 'workshop'

    def __str__(self):
        status = WorkshopStatus(self.status).name if self.status else ''
        return f'#{self.pk} {self.name} ({status})'


class WorkshopConnection(models.Model):
    user = models.ForeignKey('moodle.MoodleUser', blank=True, null=True, on_delete=models.CASCADE)
    workshop = models.ForeignKey(Workshop, models.DO_NOTHING)
    status = models.IntegerField(choices=WORKSHOP_CONNECTION_STATUS_CHOICES)

    def __str__(self):
        status = WorkshopConnectionStatus(self.status).name if self.status else ''
        return f'{self.user} - {self.workshop.name} ({status})'

    class Meta:
        managed = False
        db_table = 'workshop_connection'
        unique_together = (('user', 'workshop'),)


class WorkshopMonitor(models.Model):
    workshop = models.OneToOneField(Workshop, models.DO_NOTHING)
    type = models.IntegerField(choices=MONITOR_TYPE_CHOICES,
                               null=False, blank=False,
                               default=WorkshopMonitorType.ACM.value)
    user_visibility = models.IntegerField(choices=MONITOR_USER_VISIBILITY_CHOICES)
    with_penalty_time = models.BooleanField(default=False)
    freeze_time = models.DateField(null=True, blank=True)

    def __str__(self):
        type = WorkshopMonitorType(self.type).name if self.type else ''
        return f'Монитор {type} ({self.workshop_id}# {self.workshop.name})'

    class Meta:
        managed = False
        db_table = 'contest_monitor'
