from django.db import models

class Institution(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class School(models.Model):
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name="schools"
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('institution', 'name')

    def __str__(self):
        return f"{self.name} ({self.institution.name})"


from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    schools = models.ManyToManyField("School", related_name="profiles", blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
