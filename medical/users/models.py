from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    FileExtensionValidator,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


def address_default_value():
    return {
        "area": "",
        "district": "",
        "human_settlement": "",
        "street": "",
        "house": "",
        "corpus": "",
        "flat": "",
    }


def place_of_work_default_value():
    return {
        "name": "",
        "profession": "",
        "position": "",
        "dependent": "",
    }


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Админ"
    DOCTOR = "DOCTOR", "Доктор"
    PATIENT = "PATIENT", "Пациент"


class Gender(models.TextChoices):
    MALE = "MALE", "Мужской"
    FEMALE = "FEMALE", "Женский"


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        verbose_name=_("Имя пользователя"),
        unique=True,
    )
    first_name = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Имя"),
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("Фамилия"),
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_("Почта"),
    )
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        verbose_name=_("Роль"),
        default=Role.PATIENT,
    )

    def is_doctor(self):
        return self.role == Role.DOCTOR

    def is_patient(self):
        return self.role == Role.PATIENT

    def is_admin(self):
        return self.role == Role.ADMIN


class Specialization(models.Model):
    pass


class DoctorProfile(models.Model):
    pass


class MedicalCard(models.Model):
    cmo = models.CharField(
        verbose_name=_("Cтраховая медицинская организация"),
        max_length=30,
    )
    number_omc = models.IntegerField(
        verbose_name=_("Номер страхового полиса ОМС"),
    )
    code_exemption = models.IntegerField(
        verbose_name=_("Код налоговых льгот"),
    )
    snils = models.IntegerField(
        verbose_name=_("Страховой номер индивидуального лицевого счёта"),
    )
    second_name = models.CharField(
        verbose_name=_("Фамилия"),
        max_length=254,
    )
    first_name = models.CharField(
        verbose_name=_("Имя"),
        max_length=254,
    )
    patronymic_name = models.CharField(
        verbose_name=_("Отчество"),
        max_length=254,
    )
    gender = models.CharField(
        verbose_name=_("Пол"),
        max_length=31,
        choices=Gender.choices,
    )
    birth_date = models.DateField(
        verbose_name=_("Дата рождения"),
    )
    address_permanent = models.JSONField(
        verbose_name=_("Адрес постоянного места жительства"),
        default=address_default_value,
    )
    address_place_of_stay = models.JSONField(
        verbose_name=_("Адрес регистрации по месту пребывания"),
        default=address_default_value,
    )
    home_phone = models.CharField(
        max_length=18,
        blank=True,
        verbose_name=_("Домашний телефон"),
    )
    work_phone = models.CharField(
        max_length=18,
        blank=True,
        verbose_name=_("Служебный телефон"),
    )
    document_exemption = models.FileField(
        verbose_name=_(
            "Документ удостоверяющий право на льготное "
            "обеспечение"
        ),
        upload_to="document_exemption/",
        validators=[
            FileExtensionValidator(
                [
                    "png",
                ]
            ),
        ],
        blank=True,
    )
    place_of_work = models.JSONField(
        verbose_name=_("Место работы"),
        default=place_of_work_default_value,
    )
    disability = models.CharField(
        verbose_name=_("Инвалидность"),
        max_length=254,
    )

    class Meta:
        verbose_name = _("Карточка пациента")
        verbose_name_plural = _("Карточки пациента")


class PatientProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь"),
        related_name="patient",
    )
    avatar = models.ImageField(
        verbose_name=_("Аватар"),
        null=True,
        blank=True,
        upload_to="patient/",
    )
    medical_card = models.OneToOneField(
        MedicalCard,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Карточка пациента"),
        related_name="patient",
    )

    class Meta:
        verbose_name = _("Пациент")
        verbose_name_plural = _("Пациенты")

    def __str__(self):
        return f"Пациент {self.user.first_name} {self.user.last_name}"

    def get_telegram(self):
        try:
            return self.telegram
        except Exception:
            return None


class Review(models.Model):
    pass


class Telegram(models.Model):
    username = models.CharField(
        unique=True,
        max_length=256,
        verbose_name=_("Имя пользователя телеграмма"),
        help_text=_("Только Username"),
    )
    user_id = models.CharField(
        blank=True,
        help_text=_("id телеграмма"),
        max_length=256,
    )
    patient = models.OneToOneField(
        PatientProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Пациент"),
        related_name="telegram",
    )
