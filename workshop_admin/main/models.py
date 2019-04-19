from django.db import models

from informatics_front.model.workshop.workshop import WorkshopStatus, WorkshopVisibility


class Contest(models.Model):
    workshop = models.ForeignKey('Workshop', models.DO_NOTHING, blank=True, null=True)
    statement_id = models.IntegerField(blank=True, null=True)
    author_id = models.IntegerField(blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)
    is_virtual = models.BooleanField(blank=True, null=True, default=False)
    time_start = models.DateTimeField(blank=True, null=True)
    time_stop = models.DateTimeField(blank=True, null=True)
    # Datetime?
    virtual_duration = models.DateTimeField(blank=True, null=True)
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


WORKSHOP_STATUS_CHOICES = ((e.value, e.name) for e in WorkshopStatus)
WORKSHOP_VISIBILITY_CHOICES = ((e.value, e.name) for e in WorkshopVisibility)


class Workshop(models.Model):
    name = models.CharField(max_length=255)
    status = models.IntegerField(choices=WORKSHOP_STATUS_CHOICES)
    visibility = models.IntegerField(choices=WORKSHOP_VISIBILITY_CHOICES)

    class Meta:
        managed = False
        db_table = 'workshop'

    def __str__(self):
        visible_status = WorkshopStatus(self.visibility).name if self.visibility else ''
        return f'#{self.pk} {self.name} ({visible_status})'


class WorkshopConnection(models.Model):
    user_id = models.IntegerField()
    workshop = models.ForeignKey(Workshop, models.DO_NOTHING)
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'workshop_connection'
        unique_together = (('user_id', 'workshop'),)
