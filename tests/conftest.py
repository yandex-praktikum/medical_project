from importlib import __import__

import pytest
from django.apps import apps

pytest_plugins = [
    "tests.fixtures.data",
    "tests.fixtures.models_info",
    "tests.fixtures.urls",
]

PAGE_SIZE = 4
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"


@pytest.fixture(scope="session")
def users_app_models():
    return list(apps.get_app_config("users").get_models())


@pytest.fixture(scope="session")
def users_app_model_names(users_app_models):
    return [model.__name__ for model in users_app_models]


@pytest.fixture(scope="session")
def yacore_app_models():
    return list(apps.get_app_config("yacore").get_models())


@pytest.fixture(scope="session")
def yacore_app_model_names(yacore_app_models):
    return [model.__name__ for model in yacore_app_models]


def _import(module, entity_name):
    try:
        return getattr(
            __import__(module, fromlist=(entity_name,)), entity_name
        )
    except Exception as error:
        raise AssertionError(
            f"Убедитесь, что класс `{entity_name}` определен в модуле "
            f"`{module}`. При импорте данного класса возникла ошибка:\n"
            f"{type(error).__name__}: {error}"
        )


@pytest.fixture
def user_model():
    return _import('users.models', 'User')


@pytest.fixture
def specialization_model():
    return _import("users.models", "Specialization")


@pytest.fixture
def doctor_profile_model():
    model = _import("users.models", "DoctorProfile")
    return model


@pytest.fixture
def medical_card_model():
    return _import("users.models", "MedicalCard")


@pytest.fixture
def patient_profile_model():
    return _import("users.models", "PatientProfile")


@pytest.fixture
def review_model():
    return _import("users.models", "Review")


@pytest.fixture
def telegram_model():
    return _import("users.models", "Telegram")


@pytest.fixture
def doctor_schedule_model():
    return _import("yacore.models", "DoctorSchedule")


@pytest.fixture
def genders():
    return _import("users.models", "Gender")


@pytest.fixture
def roles():
    return _import("users.models", "Role")
