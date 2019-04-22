from django.db import models

from informatics_front.model.workshop.workshop import WorkshopStatus, WorkshopVisibility
from informatics_front.model.workshop.workshop_connection import WorkshopConnectionStatus
from utils.types import DateTimeBasedDuration


class Contest(models.Model):
    workshop = models.ForeignKey('Workshop', models.DO_NOTHING, blank=True, null=True)
    statement_id = models.IntegerField(blank=True, null=True)
    author = models.ForeignKey('moodle.MoodleUser', blank=True, null=True, on_delete=models.CASCADE)
    position = models.IntegerField(blank=True, null=True)
    is_virtual = models.BooleanField(blank=True, null=True, default=False)
    time_start = models.DateTimeField(blank=True, null=True)
    time_stop = models.DateTimeField(blank=True, null=True)
    virtual_duration = DateTimeBasedDuration(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contest'


class ContestConnection(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    contest = models.ForeignKey(Contest, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contest_connection'
        unique_together = (('user_id', 'contest'),)


class RefreshToken(models.Model):
    token = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    valid = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'refresh_token'


WORKSHOP_STATUS_CHOICES = tuple(((e.value, e.name) for e in WorkshopStatus))
WORKSHOP_VISIBILITY_CHOICES = tuple(((e.value, e.name) for e in WorkshopVisibility))


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


WORKSHOP_CONNECTION_STATUS_CHOICES = tuple(((e.value, e.name) for e in WorkshopConnectionStatus))


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
