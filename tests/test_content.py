from http import HTTPStatus

import pytest
from django.core.paginator import Paginator

from tests.conftest import _import, PAGE_SIZE

pytestmark = pytest.mark.django_db

PAGE_KEY = "page"
PAGINATOR_KEY = "paginator"


@pytest.mark.usefixtures("doctors_pack")
def test_index_has_pagination(client, index_url):
    url = index_url[0]
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        "Убедитесь, что при обращении к главной странице возвращается ответ "
        "со статус-кодом 200."
    )
    assert PAGE_KEY in response.context, (
        f"Убедитесь, что в контексте главной страницы есть ключ `{PAGE_KEY}`."
    )
    assert len(response.context[PAGE_KEY]) == PAGE_SIZE, (
        f"Убедитесь, что на главной странице отображаются {PAGE_SIZE} "
        "карточки с профилями врачей."
    )


def test_index_has_pagination_object_in_context(client, index_url):
    url = index_url[0]
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        "Убедитесь, что при обращении к главной странице возвращается ответ "
        "со статус-кодом 200."
    )
    assert isinstance(response.context.get(PAGINATOR_KEY), Paginator), (
        "Убедитесь, что в контексте главной страницы есть ключ "
        f"{PAGINATOR_KEY}, который содержит объект класса "
        "`django.core.paginator.Paginator`."
    )


@pytest.mark.usefixtures("busy_doctor")
def test_doctor_schedule_has_pagination(doctor_client, schedule_url):
    url, _ = schedule_url
    response = doctor_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f"Убедитесь, что запрос врача к странице с расписанием (`{url}`) "
        "возвращает ответ со статус-кодом 200."
    )
    assert PAGE_KEY in response.context, (
        f"Убедитесь, что в контексте страницы расписания врача есть ключ "
        f"`{PAGE_KEY}`."
    )
    assert len(response.context[PAGE_KEY]) == PAGE_SIZE, (
        "Убедитесь, что на странице расписания врача отображаются "
        f"{PAGE_SIZE} карточки с записанными пациентами."
    )


@pytest.mark.usefixtures("busy_patient")
def test_patient_schedule_has_pagination(patient_client, schedule_url):
    url, _ = schedule_url
    response = patient_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        "Убедитесь, что запрос пациента к странице с расписанием "
        f"(`{url}`) возвращает ответ со статус-кодом 200."
    )
    assert PAGE_KEY in response.context, (
        f"Убедитесь, что в контексте страницы расписания пациента есть ключ "
        f"`{PAGE_KEY}`."
    )
    assert len(response.context[PAGE_KEY]) == PAGE_SIZE, (
        "Убедитесь, что на странице расписания пациента отображаются "
        f"{PAGE_SIZE} карточки с записями к врачу на одной странице."
    )


@pytest.mark.usefixtures("another_busy_patient")
def test_patient_schedule_hasnt_foreign_appointment(
        patient_client, schedule_url
):
    url, _ = schedule_url
    response = patient_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f"Убедитесь, что запрос пациента к странице с расписанием "
        f"(`{url}`) возвращает ответ со статус-кодом 200."
    )
    assert len(response.context[PAGE_KEY]) == 0, (
        "Убедитесь, что на странице расписания пациента не отображаются "
        "чужие записи к врачу."
    )


@pytest.mark.usefixtures("another_busy_doctor")
def test_doctor_schedule_hasnt_foreign_appointment(
        doctor_client, schedule_url
):
    url, _ = schedule_url
    response = doctor_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f"Убедитесь, что запрос врача к странице с расписанием (`{url}`) "
        "возвращает ответ со статус-кодом 200."
    )
    assert len(response.context[PAGE_KEY]) == 0, (
        "Убедитесь, что на странице расписания врача не отображаются "
        "записи к другим врачам."
    )


def test_schedule_has_pagination_object_in_context(
        patient_client, schedule_url
):
    url, _ = schedule_url
    response = patient_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f"Убедитесь, что запрос врача к странице с расписанием (`{url}`) "
        "возвращает ответ со статус-кодом 200."
    )
    assert isinstance(response.context.get(PAGINATOR_KEY), Paginator), (
        "Убедитесь, что в контексте страницы расписания врача есть ключ "
        f"{PAGINATOR_KEY}, который содержит объект класса "
        "`django.core.paginator.Paginator`."
    )


@pytest.mark.parametrize("client, user_description, expected_value", [
    (pytest.lazy_fixture("doctor_client"), "врача", False),
    (pytest.lazy_fixture("patient_client"), "пациента", True),
])
def test_schedule_has_is_patient_attribute(
        client, user_description, expected_value, schedule_url
):
    url, _ = schedule_url
    response = client.get(url)
    expected_attr = "is_patient"
    assert response.status_code == HTTPStatus.OK, (
        f"Убедитесь, что запрос {user_description} к странице с расписанием "
        f"(`{url}`) возвращает ответ со статус-кодом 200."
    )
    assert expected_attr in response.context, (
        "Убедитесь, что в контексте страницы расписания есть атрибут "
        "`is_patient`."
    )
    assert response.context[expected_attr] is expected_value, (
        f"Убедитесь, что при запросе {user_description} к странице с "
        f"расписанием ключ `{expected_attr}` имеет значение "
        f"`{expected_value}`."
    )


def test_new_schedule_page_has_form(patient_client, new_schedule_url):
    url, _ = new_schedule_url
    response = patient_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        "Убедитесь, что запрос пациента к странице для записи к врачу "
        f"(`{url}`) возвращает ответ со статус-кодом 200."
    )
    form_class = _import("yacore.forms", "DoctorScheduleForm")
    assert isinstance(response.context.get("form"), form_class), (
        "Убедитесь, что в контексте страницы для записи к врачу есть ключ "
        "`form`, значением которого является объект класса "
        "`yacore.forms.DoctorScheduleForm`."
    )


@pytest.mark.usefixtures("add_old_appointment")
def test_add_review_page_has_form(patient_client, add_review_url):
    url, verbose_url = add_review_url
    response = patient_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f"Убедитесь, что запрос пациента к странице для добавления отзыва о "
        f"враче (`{verbose_url}`) возвращает ответ со статус-кодом 200."
    )
    form_class = _import("yacore.forms", "ReviewForm")
    assert isinstance(response.context.get("form"), form_class), (
        "Убедитесь, что в контексте страницы для добавления отзыва о враче "
        "есть ключ `form`, значением которого является объект класса "
        "`yacore.forms.ReviewForm`."
    )


def test_doctor_detail_page_has_doctor_object(
        doctor_profile_model, patient_client, doctor, doctor_detail_url
):
    url, verbose_url = doctor_detail_url
    doctor_profile = doctor_profile_model.objects.get(user=doctor)
    response = patient_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f"Убедитесь, что запрос пациента к странице профиля врача "
        f"(`{verbose_url}`) возвращает ответ со статус-кодом 200."
    )
    assert "doctor" in response.context, (
        "Убедитесь, что в контексте страницы профиля врача есть ключ "
        "`doctor`."
    )
    assert response.context["doctor"] == doctor_profile, (
        "Убедитесь, что при запросе пациента к странице профиля врача "
        "ключ `doctor` содержит объект класса `DoctorProfile` с "
        "соответствующим запросу id."
    )


def test_patient_profile_page_has_patient_object(
        patient_profile_model, patient_client, patient, patient_profile_url
):
    url, verbose_url = patient_profile_url
    patient_profile = patient_profile_model.objects.get(user=patient)
    response = patient_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        "Убедитесь, что запрос пациента к странице профиля пациента "
        f"(`{verbose_url}`) возвращает ответ со статус-кодом 200."
    )
    assert "patient" in response.context, (
        "Убедитесь, что в контексте страницы профиля пациента есть ключ "
        "`patient`."
    )
    assert response.context["patient"] == patient_profile, (
        "Убедитесь, что при запросе пациента к странице профиля пациента "
        "ключ `patient` содержит объект класса `PatientProfile` с "
        "соответствующим запросу id."
    )


def test_patient_profile_page_has_medcard_form(
        patient_profile_model, patient_client, patient, patient_profile_url
):
    url, verbose_url = patient_profile_url
    patient_profile = patient_profile_model.objects.get(user=patient)
    response = patient_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f"Убедитесь, что запрос пациента к странице профиля пациента "
        f"(`{verbose_url}`) возвращает ответ со статус-кодом 200."
    )
    medcard_form = response.context.get("form")
    form_class = _import("yacore.forms", "MedicalCardForm")
    assert isinstance(medcard_form, form_class), (
        "Убедитесь, что в контексте страницы профиля пациента есть ключ "
        "`form`, значением которого является объект класса "
        "`yacore.forms.MedicalCardForm`."
    )
    assert medcard_form.instance == patient_profile.medical_card, (
        "Убедитесь, что форма медицинской карты пациента на странице профиля "
        "пациента в атрибуте `instance` содержит объект модели `MedicalCard`, "
        "связанный с проифилем пациента."
    )


@pytest.mark.usefixtures("add_telegram_for_patient")
def test_patient_profile_page_has_telegram_form(
        patient_profile_model, patient_client, patient, patient_profile_url
):
    url, verbose_url = patient_profile_url
    patient_profile = patient_profile_model.objects.get(user=patient)
    response = patient_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f"Убедитесь, что запрос пациента к странице профиля пациента "
        f"(`{verbose_url}`) возвращает ответ со статус-кодом 200."
    )
    teltegram_form = response.context.get("form_telegram")
    form_class = _import("yacore.forms", "TelegramForm")
    assert isinstance(teltegram_form, form_class), (
        "Убедитесь, что в контексте страницы профиля пациента есть ключ "
        "`form_telegram`, значением которого является объект класса "
        "`yacore.forms.TelegramForm`."
    )
    assert teltegram_form.instance == patient_profile.telegram, (
        "Убедитесь, что форма для добавления Telegram-аккаунта на странице "
        "профиля пациента в атрибуте `instance` содержит объект модели "
        "`Telegram`, связанный с проифилем пациента, если таковой имеется."
    )


@pytest.mark.parametrize(
    "client, expected_result, assert_msg",
    (
        (
            pytest.lazy_fixture("another_doctor_client"),
            False,
            ("Убедитесь, что на страницу со списком пациентов врача "
             "не попадают пациенты, не записанные и ранее не посещавшие "
             "врача.")
        ),
        (
            pytest.lazy_fixture("doctor_client"),
            True,
            ("Убедитесь, что на страницу со списком пациентов врача "
             "попадают пациенты, записанные иои ранее не посещавшие врача.")
        )
    ),
    ids=("another_doctor", "doctor")
)
@pytest.mark.usefixtures("add_appointment")
def test_doctor_patients_page_has_correct_pacients(
        patient_profile_model, client, expected_result, assert_msg, patient,
        patients_url
):
    url, _ = patients_url
    response = client.get(url)
    patient_profile = patient_profile_model.objects.get(user=patient)
    assert response.status_code == HTTPStatus.OK, (
        "Убедитесь, что запрос врача к странице со списком своих "
        f"пациентов (`{url}`) возвращает ответ со статус-кодом 200."
    )
    assert "patients" in response.context, (
        "Убедитесь, что в контексте страницы со списком пациентов врача "
        f"(`{url}`) есть ключ `patients`."
    )
    assert (
        (patient_profile in response.context["patients"]) is expected_result
    ), assert_msg


def test_doctor_patients_page_has_doctor_object(
        doctor_profile_model, doctor_client, doctor, patients_url
):
    url, _ = patients_url
    doctor_profile = doctor_profile_model.objects.get(user=doctor)
    response = doctor_client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        "Убедитесь, что запрос врача к странице со списком пациентов "
        f"(`{url}`) возвращает ответ со статус-кодом 200."
    )
    assert "doctor" in response.context, (
        "Убедитесь, что в контексте страницы со списком пациентов врача "
        f"(`{url}`) есть ключ `doctor`."
    )
    assert response.context["doctor"] == doctor_profile, (
        "Убедитесь, что при запросе врача к странице со списком пациентов "
        "ключ `doctor` содержит объект класса `DoctorProfile` с "
        "c id, соответствующим пользователю, сделавшему запрос."
    )
