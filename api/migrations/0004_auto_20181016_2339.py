# Generated by Django 2.1.1 on 2018-10-16 23:39

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20181015_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='state_changed_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, help_text='Дата обновляется при изменении состояния `state` и при изменении вопроса `current_question`.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='game',
            name='state',
            field=models.CharField(choices=[('players_waiting', 'Ожидание игроков'), ('answering', 'Игроки отвечают на вопросы'), ('check', 'Показ правильного ответа'), ('finish', 'Финиш')], db_index=True, default='players_waiting', max_length=15),
        ),
        migrations.AlterField(
            model_name='game',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True, help_text='Дата обновляется при любых обновлениях снапшота игры: изменении модели, присоединение игрока, при новом ответе и т.д.'),
        ),
        migrations.AlterField(
            model_name='player',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='api.Game'),
        ),
    ]
