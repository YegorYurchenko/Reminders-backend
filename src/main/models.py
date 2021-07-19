""" Models """

from django.db import models

class Reminders(models.Model):
    """ Модель Reminders """
    title = models.CharField('Название', max_length=100)
    date = models.DateField('Дата', editable = True)
    time = models.TimeField('Время', editable = True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Reminders'
        verbose_name_plural = 'Reminders'
