# Generated by Django 2.2.1 on 2019-07-03 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moodle', '0002_statement'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseModule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instance', models.IntegerField()),
            ],
            options={
                'db_table': 'mdl_course_modules',
                'managed': False,
            },
        ),
    ]
