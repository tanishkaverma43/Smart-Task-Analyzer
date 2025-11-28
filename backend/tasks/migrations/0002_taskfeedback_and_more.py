

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.IntegerField(help_text='ID of the task that was suggested')),
                ('was_helpful', models.BooleanField(help_text='Whether the suggestion was helpful')),
                ('feedback_notes', models.TextField(blank=True, help_text='Optional feedback notes', null=True)),
                ('suggested_at', models.DateTimeField(auto_now_add=True, help_text='When the suggestion was made')),
                ('feedback_at', models.DateTimeField(auto_now=True, help_text='When feedback was provided')),
            ],
            options={
                'ordering': ['-feedback_at'],
            },
        ),
        migrations.RenameIndex(
            model_name='task',
            new_name='tasks_task_due_dat_bce847_idx',
            old_name='tasks_task_due_dat_0d9bd7_idx',
        ),
        migrations.RenameIndex(
            model_name='task',
            new_name='tasks_task_importa_8cea0f_idx',
            old_name='tasks_task_importa_8a15fe_idx',
        ),
        migrations.AddIndex(
            model_name='taskfeedback',
            index=models.Index(fields=['task_id'], name='tasks_taskf_task_id_c07466_idx'),
        ),
        migrations.AddIndex(
            model_name='taskfeedback',
            index=models.Index(fields=['was_helpful'], name='tasks_taskf_was_hel_d2f981_idx'),
        ),
    ]
