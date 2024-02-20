import pytest
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from tests.model_test_utils import FieldInfo, ValidatorInfo


@pytest.fixture(scope="session")
def specialization_model_info():
    return (
        "Specialization", {
            "title": FieldInfo(
                models.CharField,
                {
                    "max_length": 256,
                    "null": False,
                    "blank": False,
                }
            ),
            "is_valid": FieldInfo(
                models.BooleanField,
                {
                    "default": False,
                    "null": False,
                    "blank": False,
                }
            )
        },
        {
            "verbose_name": "Специализация",
            "verbose_name_plural": "Специализации"
        }
    )


@pytest.fixture(scope="session")
def doctor_profile_model_info():
    return (
        "DoctorProfile", {
            "user": FieldInfo(
                models.OneToOneField,
                {
                    "related_model": "User",
                    "on_delete": "models.CASCADE",
                    "null": False,
                    "blank": False,
                }
            ),
            "specializations": FieldInfo(
                models.ManyToManyField,
                {
                    "related_model": "Specialization",
                    "blank": True,
                }
            ),
            "employment_date": FieldInfo(
                models.DateField,
                {
                    "auto_now": True,
                }
            ),
            "avatar": FieldInfo(
                models.ImageField,
                {
                    "blank": True,
                }
            )
        },
        {
            "verbose_name": "Доктор",
            "verbose_name_plural": "Доктора"
        }
    )


@pytest.fixture(scope="session")
def review_model_info():
    return (
        "Review", {
            "text": FieldInfo(
                models.TextField,
                {
                    "null": False,
                    "blank": False,
                }
            ),
            "author_name": FieldInfo(
                models.CharField,
                {
                    "default": "Аноним",
                }
            ),
            "created_at": FieldInfo(
                models.DateField,
                {
                    "auto_now_add": True,
                }
            ),
            "rating": FieldInfo(
                models.FloatField,
                {'validators': {
                    MinValueValidator: ValidatorInfo(
                        1, 'минимальным значением'),
                    MaxValueValidator: ValidatorInfo(
                        5, 'максимальным значением')
                }}
            ),
            "doctor": FieldInfo(
                models.ForeignKey,
                {
                    "related_model": "DoctorProfile",
                }
            ),
            "is_valid": FieldInfo(
                models.BooleanField,
                {
                    "default": False,
                }
            )
        },
        {
            "verbose_name": "Отзыв",
            "verbose_name_plural": "Отзывы"
        }
    )


@pytest.fixture(scope="session")
def doctor_schedule_model_info():
    return (
        "DoctorSchedule",
        {
            "doctor": FieldInfo(
                models.ForeignKey,
                {
                    "related_model": "DoctorProfile",
                    "null": False,
                    "blank": False,
                }
            ),
            "date_from": FieldInfo(
                models.DateTimeField,
                {
                    "null": False,
                    "blank": False,
                }
            ),
            "date_due": FieldInfo(
                models.DateTimeField,
                {
                    "null": False,
                    "blank": False,
                }
            ),
            "specialization": FieldInfo(
                models.ForeignKey,
                {
                    "related_model": "Specialization",
                    "null": False,
                    "blank": False,
                }
            ),
            "patient": FieldInfo(
                models.ForeignKey,
                {
                    "related_model": "PatientProfile",
                    "null": False,
                    "blank": False,
                }
            ),
            "feedback": FieldInfo(
                models.TextField,
                {
                    "blank": True,
                }
            ),
            "is_complete": FieldInfo(
                models.BooleanField,
                {
                    "default": False,
                }
            ),
            "is_cancelled": FieldInfo(
                models.BooleanField,
                {
                    "default": False,
                }
            )
        },
        {
            "verbose_name": "Запись на прием",
            "verbose_name_plural": "Записи на приемы"
        }
    )
