from django.db import models


class Thing(models.Model):

    CHOICES1 = {
        'one': '1',
        'two': '2',
    }

    fchar = models.CharField(max_length=50, verbose_name='fchar_name', help_text='fchar_help')
    fchoices = models.CharField(
        max_length=50, verbose_name='fchoices_name', help_text='fchoices_help', choices=CHOICES1.items())
    fbool = models.BooleanField(default=False, verbose_name='fbool_name', help_text='fbool_help')
    ftext = models.TextField(verbose_name='ftext_name', help_text='ftext_help')
    ffile = models.FileField(verbose_name='ffile_name')
