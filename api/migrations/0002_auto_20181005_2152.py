# Generated by Django 2.1.1 on 2018-10-05 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('quiz', 'number')},
        ),
        migrations.RenameField(
            model_name='question',
            old_name='time',
            new_name='timer',
        ),
        migrations.AlterField(
            model_name='question',
            name='number',
            field=models.IntegerField(db_index=True, help_text='Номер вопроса, начиная с 1.\nСоответствует порядковому номеру в массиве.'),
        ),
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.CharField(choices=[('single', 'Single - один верный ответ'), ('multi', 'Multi - несколько верных ответов'), ('sequence', 'Sequence - правильная последовательность')], help_text='Single - один верный ответ;\nMulti - несколько верных ответов;\nSequence - правильная последовательность.', max_length=10),
        ),
        migrations.AlterUniqueTogether(
            name='question',
            unique_together={('quiz', 'number')},
        ),
    ]
