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
    uzivatelske_jmeno = models.CharField(max_length=200, verbose_name="Uživatelské jméno")
    email = models.EmailField(max_length=300, unique=True)
    is_admin = models.BooleanField(default=False)
    jmeno = models.CharField(max_length=200, verbose_name="Jméno")
    prijmeni = models.CharField(max_length=200, verbose_name="Příjmení")

    class Meta:
        verbose_name = "uživatel"
        verbose_name_plural = "uživatelé"

    objects = UzivatelManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.jmeno + ' ' + self.prijmeni

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
        return f"{self.nazev_zanru}"

class Kniha(models.Model):
    nazev = models.CharField(max_length=200, verbose_name="Název")
    podtitul = models.CharField(max_length=200, verbose_name="Podtitul", blank=True)
    autor = models.CharField(max_length=180, verbose_name="Autor")
    rok_vydani = models.CharField(max_length=180, verbose_name="Publikováno")
    jazyk = models.CharField(max_length=180, verbose_name="Jazyk")
    ISBN10 = models.CharField(max_length=180, blank=True)
    ISBN13 = models.CharField(max_length=180, blank=True)
    zanr = models.ForeignKey(Zanr, on_delete=models.SET_NULL, null=True, verbose_name="Žánr")
    majitel = models.ForeignKey(Uzivatel, on_delete=models.CASCADE, verbose_name="Majitel")

    def __str__(self):
        return f"Název: {self.nazev} | Podtitul: {self.podtitul} | Autor: {self.autor} | Žánr: {self.zanr}"