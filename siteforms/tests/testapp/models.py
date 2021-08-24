from django.db import models


class Another(models.Model):

    fsome = models.CharField(max_length=20, verbose_name='fsome_name', help_text='fsome_help')
    fparent = models.ForeignKey(
        'Another', verbose_name='fparent_name', help_text='fparent_help', null=True, on_delete=models.CASCADE)


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
    fforeign = models.ForeignKey(Another, verbose_name='fforeign_name', null=True, on_delete=models.CASCADE)
