from django.db import models


class Author(models.Model):

    name = models.CharField('Name', max_length=100)

    def __str__(self):
        return f'{self.name} ({self.id})'


class Article(models.Model):

    date_created = models.DateTimeField('Created', auto_now_add=True, blank=True)

    author = models.ForeignKey(Author, verbose_name='Author', on_delete=models.CASCADE)

    title = models.CharField('Title', max_length=200, help_text='Short descriptive text')

    to_hide = models.CharField('To hide', max_length=10, help_text='Secret field', default='yes', blank=True)

    formsub1 = models.CharField(
        'Subform', max_length=250, help_text='This part is from subform',
        default='{"first": "f", "second": "s"}', blank=True)

    dummy = models.CharField('Dummy', max_length=100, help_text='This is just a dummy', default='dummy', blank=True)

    email = models.EmailField('Email', help_text='Where to send a message')

    contents = models.TextField('Contents')

    approved = models.BooleanField('Approved', default=False, help_text='Whether it was approved')
    status = models.IntegerField(
        'Status', default=0, choices={0: 'Draft', 1: 'Published'}.items(), help_text='Article status')

    attach = models.FileField(verbose_name='Attachment', help_text='Custom user attachment', null=True, blank=True)
