from django.db import models


class Article(models.Model):

    date_created = models.DateTimeField('Created', auto_created=True)

    title = models.CharField('Title', max_length=200, help_text='Short descriptive text')

    dummy = models.CharField('Dummy', max_length=100, help_text='This is just a dummy', default='dummy', blank=True)

    email = models.EmailField('Email', help_text='Where to send a message')

    contents = models.TextField('Contents')

    approved = models.BooleanField('Approved', default=False, help_text='Whether it was approved')
    status = models.IntegerField(
        'Status', default=0, choices={0: 'Draft', 1: 'Published'}.items(), help_text='Article status')

    attach = models.FileField(verbose_name='Attachment', help_text='Custom user attachment')
