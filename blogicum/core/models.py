from django.db import models


class BaseModel(models.Model):

    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено",
    )

    class Meta:
        abstract = True


class BaseTitle(models.Model):

    title = models.CharField(
        max_length=256,
        verbose_name="Заголовок",
    )

    class Meta:
        abstract = True
