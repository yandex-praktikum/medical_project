import pytest

from tests.model_test_utils import CheckModelsInfo


@pytest.mark.parametrize("model_name", [
    "User",
    "Specialization",
    "DoctorProfile",
    "MedicalCard",
    "PatientProfile",
    "Review",
    "Telegram",
])
def test_models(model_name, users_app_model_names):
    """Test if `users` app has expected models."""
    assert model_name in users_app_model_names, (
        f"Убедитесь, что в приложении `users` есть модель `{model_name}`."
    )


def test_yacore_models(yacore_app_model_names):
    """Test if `yacore` app has expected model."""
    expected_model_name = "DoctorSchedule"
    assert expected_model_name in yacore_app_model_names, (
        "Убедитесь, что в приложении `yacore` есть модель "
        f"`{expected_model_name}`."
    )


@pytest.mark.parametrize("model_info", [
    pytest.lazy_fixture("specialization_model_info"),
    pytest.lazy_fixture("doctor_profile_model_info"),
    pytest.lazy_fixture("review_model_info"),
])
def test_none_precoded_users_app_models(model_info, users_app_models):
    """Test implementation of models in `users` app.

    Non-precoded models check only.
    """
    model_name, fields_map, model_verbose_names = model_info
    try:
        model = [
            model for model in users_app_models if model.__name__ == model_name
        ][0]
    except IndexError:
        raise AssertionError(
            f"В приложении `users` не обнаружена модель `{model_name}`"
        )
    CheckModelsInfo(model, fields_map, model_verbose_names)()


def test_none_precoded_yacore_app_model(doctor_schedule_model_info,
                                        yacore_app_models):
    """Test implementation of models in `yacore` app.

    Non-precoded models check only.
    """
    model_name, fields_map, model_verbose_names = doctor_schedule_model_info
    try:
        model = [
            model for model in yacore_app_models
            if model.__name__ == model_name
        ][0]
    except IndexError:
        raise AssertionError(
            f"В приложении `yacore` не обнаружена модель `{model_name}`"
        )
    CheckModelsInfo(model, fields_map, model_verbose_names)()
