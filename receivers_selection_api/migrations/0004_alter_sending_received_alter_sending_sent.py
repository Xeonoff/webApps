# Generated by Django 4.2.5 on 2023-11-20 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receivers_selection_api', '0003_remove_receiver_file_extension_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sending',
            name='received',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Получен'),
        ),
        migrations.AlterField(
            model_name='sending',
            name='sent',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Отправлен'),
        ),
    ]
