from django.db import models


class Another(models.Model):

    fsome = models.CharField(max_length=20, verbose_name='fsome_name', help_text='fsome_help')
    fadd = models.ForeignKey(
        'Additional', verbose_name='fadd_name', help_text='fadd_help', null=True, blank=True,
        on_delete=models.CASCADE)

    def __str__(self):
        return self.fsome


class Additional(models.Model):

    fnum = models.CharField(max_length=5, verbose_name='fnum_name', help_text='fnum_help')


class Link(models.Model):

    fadd = models.ForeignKey(Additional, verbose_name='fadd_lnk', on_delete=models.CASCADE)
    fthing = models.ForeignKey('Thing', verbose_name='fthing_lnk', on_delete=models.CASCADE)
    fmore = models.CharField(max_length=5, verbose_name='fmore_name', help_text='fmore_help')


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
    fm2m = models.ManyToManyField(Additional, verbose_name='fm2m_name')


class AnotherThing(models.Model):

    fchar = models.CharField(max_length=50, verbose_name='fchar_name')
    fm2m = models.ManyToManyField(Another, verbose_name='fm2m_name')
