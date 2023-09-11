from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.

class UzivatelManager(BaseUserManager):

    def create_user(self, email, password):
        print(self.model)
        if email and password:
            user = self.model(email=self.normalize_email(email))
            user.set_password(password)
            user.save()
            return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_admin = True
        user.save()
        return user
class Uzivatel(AbstractBaseUser):
    username = models.CharField(max_length=200)
    email = models.EmailField(max_length=300, unique=True)
    is_admin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

    class Meta:
        verbose_name = "uživatel"
        verbose_name_plural = "uživatelé"

    objects = UzivatelManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return "email: {}".format(self.email)

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
class Zanr(models.Model):
    nazev_zanru = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.genre_name}"
class Kniha(models.Model):
    nazev = models.CharField(max_length=200, verbose_name="Název")
    autor = models.CharField(max_length=180, verbose_name="Autor")
    rok_vydani = models.CharField(max_length=180, verbose_name="Publikováno")
    jazyk = models.CharField(max_length=180, verbose_name="Jazyk")
    ISBN10 = models.CharField(max_length=180, blank=True)
    ISBN13 = models.CharField(max_length=180, blank=True)
    zanr = models.ForeignKey(Zanr, on_delete=models.SET_NULL, null= True, verbose_name="Žánr")
    majitel = models.CharField(max_length=180, verbose_name="Majitel", blank=True)

    def __str__(self):
        return f"Název: {self.nazev} | Autor: {self.autor} | Žánr: {self.zanr}"