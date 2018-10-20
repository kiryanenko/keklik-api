# Generated by Django 2.1.1 on 2018-10-19 17:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20181016_2339'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='title',
        ),
        migrations.AddField(
            model_name='game',
            name='label',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='generatedquestion',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='generated_questions', to='api.Game'),
        ),
    ]