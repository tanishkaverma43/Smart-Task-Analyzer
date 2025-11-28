

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('due_date', models.DateField()),
                ('estimated_hours', models.FloatField(help_text='Estimated hours to complete the task', validators=[django.core.validators.MinValueValidator(0.1)])),
                ('importance', models.IntegerField(help_text='Task importance on scale of 1-10', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('dependencies', models.JSONField(blank=True, default=list, help_text='List of task IDs this task depends on')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['due_date'], name='tasks_task_due_dat_0d9bd7_idx'), models.Index(fields=['importance'], name='tasks_task_importa_8a15fe_idx')],
            },
        ),
    ]


