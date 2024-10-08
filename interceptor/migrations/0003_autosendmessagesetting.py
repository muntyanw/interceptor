# Generated by Django 5.1 on 2024-08-27 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interceptor', '0002_telegrammessage_delete_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoSendMessageSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_enabled', models.BooleanField(default=False, verbose_name='Автоматическая отправка включена')),
                ('auto_sent_count', models.IntegerField(default=0, verbose_name='Количество автоматически отправленных сообщений')),
            ],
        ),
    ]
