# Generated by Django 3.0.6 on 2020-05-19 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0002_auto_20200518_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created'),
        ),
        migrations.AlterField(
            model_name='article',
            name='formsub1',
            field=models.CharField(blank=True, default='{"first": "f", "second": "s"}', help_text='This part is from subform', max_length=35, verbose_name='Subform'),
        ),
    ]
