# Generated by Django 2.2 on 2019-04-19 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statement_id', models.IntegerField(blank=True, null=True)),
                ('author_id', models.IntegerField(blank=True, null=True)),
                ('position', models.IntegerField(blank=True, null=True)),
                ('is_virtual', models.BooleanField(blank=True, default=False, null=True)),
                ('time_start', models.DateTimeField(blank=True, null=True)),
                ('time_stop', models.DateTimeField(blank=True, null=True)),
                ('virtual_duration', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'contest',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ContestConnection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'contest_connection',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RefreshToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(blank=True, max_length=255, null=True)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('valid', models.IntegerField()),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'refresh_token',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Workshop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('status', models.IntegerField(choices=[(1, 'DRAFT'), (2, 'ONGOING')])),
                ('visibility', models.IntegerField(choices=[(1, 'PUBLIC'), (2, 'PRIVATE')])),
            ],
            options={
                'db_table': 'workshop',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='WorkshopConnection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('status', models.IntegerField()),
            ],
            options={
                'db_table': 'workshop_connection',
                'managed': False,
            },
        ),
    ]
