import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone
from mixer.backend.django import mixer

from tests.conftest import DATETIME_FORMAT, PAGE_SIZE


User = get_user_model()


def _create_patient(patient_profile_model, medical_card_model, roles):
    patient = mixer.blend(User, role=roles.PATIENT)
    medical_card = mixer.blend(medical_card_model, document_exemption='')
    mixer.blend(patient_profile_model, user=patient, medical_card=medical_card)
    return patient


def _create_doctor(doctor_profile_model, roles, specialization=None,):
    doctor = mixer.blend(User, role=roles.DOCTOR)
    mixer.blend(
        doctor_profile_model, user=doctor, specializations=(specialization,)
    )
    return doctor


def _add_appointment(
        doctor_profile_model, patient_profile_model, doctor_schedule_model,
        patient, doctor, shift=0
):
    tomorrow = timezone.now() + timezone.timedelta(days=1+shift)
    time_due = tomorrow + timezone.timedelta(hours=1)
    doctor_profile = doctor_profile_model.objects.get(user=doctor)
    patient_profile = patient_profile_model.objects.get(user=patient)
    return mixer.blend(
        doctor_schedule_model, doctor=doctor_profile, patient=patient_profile,
        date_from=tomorrow, date_due=time_due,
        is_complete=False, is_cancelled=False
    )


@pytest.fixture
def specialization(specialization_model):
    return mixer.blend(specialization_model)


@pytest.fixture
def admin_user(roles):
    return mixer.blend(User, role=roles.ADMIN, is_staff=True)


@pytest.fixture
def doctor(doctor_profile_model, specialization, roles):
    return _create_doctor(doctor_profile_model, roles, specialization, )


@pytest.fixture
def doctors_pack(doctor_profile_model, roles):
    return [
        _create_doctor(doctor_profile_model, roles)
        for _ in range(PAGE_SIZE + 1)
    ]


@pytest.fixture
def another_doctor(doctor_profile_model, roles):
    return _create_doctor(doctor_profile_model, roles)


@pytest.fixture
def another_doctor_with_specialization(
        doctor_profile_model, specialization, roles
):
    return _create_doctor(doctor_profile_model, roles, specialization)


@pytest.fixture
def patient(patient_profile_model, medical_card_model, roles):
    return _create_patient(patient_profile_model, medical_card_model, roles)


@pytest.fixture
def patients_pack(patient_profile_model, medical_card_model, roles):
    return [
        _create_patient(patient_profile_model, medical_card_model, roles)
        for _ in range(PAGE_SIZE + 1)
    ]


@pytest.fixture
def another_patient(patient_profile_model, medical_card_model, roles):
    return _create_patient(patient_profile_model, medical_card_model, roles)


@pytest.fixture
def add_appointment(
        doctor_profile_model, patient_profile_model, doctor_schedule_model,
        patient, doctor
):
    return _add_appointment(
        doctor_profile_model, patient_profile_model, doctor_schedule_model,
        patient, doctor
    )


@pytest.fixture
def add_old_appointment(
        doctor_profile_model, patient_profile_model, doctor_schedule_model,
        patient, doctor
):
    return _add_appointment(
        doctor_profile_model, patient_profile_model, doctor_schedule_model,
        patient, doctor, shift=-2
    )


@pytest.fixture
def add_telegram_for_patient(patient_profile_model, telegram_model, patient):
    patient_profile = patient_profile_model.objects.get(user=patient)
    return mixer.blend(telegram_model, patient=patient_profile)


@pytest.fixture
def busy_doctor(
        doctor_profile_model, patient_profile_model, doctor_schedule_model,
        doctor, patients_pack
):
    return [
        _add_appointment(
            doctor_profile_model, patient_profile_model, doctor_schedule_model,
            patient, doctor, shift
        ) for shift, patient in enumerate(patients_pack)
    ]


@pytest.fixture
def busy_patient(
        doctor_profile_model, patient_profile_model, doctor_schedule_model,
        patient, doctors_pack
):
    return [
        _add_appointment(
            doctor_profile_model, patient_profile_model, doctor_schedule_model,
            patient, doctor, shift
        ) for shift, doctor in enumerate(doctors_pack)
    ]


@pytest.fixture
def another_busy_patient(
        doctor_profile_model, patient_profile_model, doctor_schedule_model,
        another_patient, doctors_pack
):
    return [
        _add_appointment(
            doctor_profile_model, patient_profile_model, doctor_schedule_model,
            another_patient, doctor, shift
        ) for shift, doctor in enumerate(doctors_pack)
    ]


@pytest.fixture
def another_busy_doctor(
        doctor_profile_model, patient_profile_model, doctor_schedule_model,
        another_doctor, patients_pack
):
    return [
        _add_appointment(
            doctor_profile_model, patient_profile_model, doctor_schedule_model,
            patient, another_doctor, shift
        ) for shift, patient in enumerate(patients_pack)
    ]


@pytest.fixture
def admin_client(admin_user):
    client = Client()
    client.force_login(admin_user)
    return client


@pytest.fixture
def doctor_client(doctor):
    client = Client()
    client.force_login(doctor)
    return client


@pytest.fixture
def another_patient_client(another_patient):
    client = Client()
    client.force_login(another_patient)
    return client


@pytest.fixture
def another_doctor_client(another_doctor):
    client = Client()
    client.force_login(another_doctor)
    return client


@pytest.fixture
def patient_client(patient):
    client = Client()
    client.force_login(patient)
    return client


@pytest.fixture
def anonymous_client():
    return Client()


@pytest.fixture
@pytest.mark.usefixtures("doctor")
def appointment_form_data(specialization):
    date_from = timezone.now() + timezone.timedelta(days=1)
    date_due = date_from + timezone.timedelta(hours=1)
    return {
        "specialization": specialization.id,
        "date_from": date_from.strftime(DATETIME_FORMAT),
        "date_due": date_due.strftime(DATETIME_FORMAT),
    }


@pytest.fixture
def review_form_data():
    return {
        "author_name": "Аноним",
        "rating": 4,
        "text": "Тестовый отзыв",
    }


@pytest.fixture
def patient_profile_form_data(genders):
    return {
        "area": "Приморский край",
        "district": "Уссурийский городской округ",
        "human_settlement": "с. Воздвиженка",
        "street": "ул. Ленина",
        "house": "1",
        "corpus": "А",
        "flat": "1",
        "name": "ООО Рога и копыта",
        "profession": "Инженер",
        "position": "Главный инженер",
        "dependent": "Да",
        "birth_date": "1986-03-06",
        "cmo": "АО Возрождение",
        "number_omc": "1234567",
        "code_exemption": "12345678901",
        "snils": "12345678901",
        "second_name": "Иванов",
        "first_name": "Иван",
        "patronymic_name": "Иванович",
        "gender": genders.MALE,
        "home_phone": "+7 800 999 99 99",
        "work_phone": "+7 999 999 99 99",
        "disability": "Нет",
    }


@pytest.fixture
def telegram_form_data():
    return {
        "username": "@test",
    }
