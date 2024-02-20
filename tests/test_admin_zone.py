import pytest

from django.conf import settings
from django.contrib import admin


@pytest.mark.parametrize("model", (
    pytest.lazy_fixture("doctor_profile_model"),
    pytest.lazy_fixture("doctor_schedule_model"),
    pytest.lazy_fixture("medical_card_model"),
    pytest.lazy_fixture("patient_profile_model"),
    pytest.lazy_fixture("review_model"),
    pytest.lazy_fixture("specialization_model"),
    pytest.lazy_fixture("telegram_model"),
    pytest.lazy_fixture("user_model")
))
def test_models_registred_in_admin_zone(model):
    assert model in admin.site._registry, (
        f'Убедитесь, что модель `{model.__name__}` зарегистрирована в '
        'админ-зоне Django-проекта.'
    )


def test_ru_language_code_is_used():
    assert settings.LANGUAGE_CODE.lower() in ('ru-ru', 'ru'), (
        'Убедитесь, что подлючили русскую локализацию в `settings.py`.'
    )
