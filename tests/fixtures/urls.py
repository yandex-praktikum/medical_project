import pytest
from django.urls import reverse


@pytest.fixture
def index_url():
    return (reverse("index"), None)


@pytest.fixture
def new_schedule_url():
    return (reverse("new_schedule"), None)


@pytest.fixture
def schedule_url():
    return (reverse("schedule"), None)


@pytest.fixture
def add_review_url(doctor_profile_model, doctor):
    doctor_profile = doctor_profile_model.objects.get(user=doctor)
    return (reverse(
        "add_comment", args=(doctor_profile.id,)), "<doctor_id>/comment/"
    )


@pytest.fixture
def doctor_detail_url(doctor_profile_model, doctor):
    doctor_profile = doctor_profile_model.objects.get(user=doctor)
    return (reverse(
        "doctor_detail", args=(doctor_profile.id,)), "doctor/<doctor_id>/"
    )


@pytest.fixture
def patient_profile_url(patient_profile_model, patient):
    patient_profile = patient_profile_model.objects.get(user=patient)
    return (reverse(
        "profile", args=(patient_profile.id,)), "profile/<patient_id>/"
    )


@pytest.fixture
def patients_url():
    return (reverse("patients"), None)


@pytest.fixture
def add_telegram_url():
    return (reverse("add_telegram"), None)


@pytest.fixture
def login_url():
    return (reverse("login"), None)
