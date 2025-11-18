from django.conf import settings
from django.db import models


class SavedCrossword(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_crosswords",
    )
    category = models.CharField(max_length=200)
    grid_state = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} for {self.user.username} (id={self.id})"
