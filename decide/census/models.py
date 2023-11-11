from django.db import models


class Census(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()

    class Meta:
        unique_together = (("voting_id", "voter_id"),)

    def __str__(self):
        return f"{self.voting_id} {self.voter_id}"
