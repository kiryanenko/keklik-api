# Generated by Django 2.1.1 on 2018-10-31 15:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_auto_20181031_1508'),
        ('api', '0009_auto_20181028_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='games', to='organization.Group'),
        ),
    ]