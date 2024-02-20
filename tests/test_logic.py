from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

from conftest import DATETIME_FORMAT

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("another_doctor")
def test_patient_can_create_new_appointment(
        doctor_schedule_model, doctor_profile_model, patient_profile_model,
        patient_client, patient, new_schedule_url, doctor,
        appointment_form_data, index_url
):
    url, _ = new_schedule_url
    patient_profile = patient_profile_model.objects.get(user=patient)
    doctor_profile = doctor_profile_model.objects.get(user=doctor)
    response = patient_client.post(url, data=appointment_form_data)
    assert doctor_schedule_model.objects.count() == 1, (
        "Убедитесь, что при корректном заполнении формы для записи "
        f"к врачу на странице `{url}` создается запись в базе данных."
    )
    new_schedule = doctor_schedule_model.objects.get()
    assert_msg_pattern = (
        "Убедитесь, что после отправки формы для записи к врачу в поле "
        "`{field_name}` создаваемого объекта класса `DoctorSchedule` "
        "добавляется {description}."
    )
    assert new_schedule.doctor == doctor_profile, assert_msg_pattern.format(
        field_name="doctor",
        description=(
            "профиль врача с соответствующей полученной форме "
            "специализацией"
        )
    )
    assert new_schedule.patient == patient_profile, assert_msg_pattern.format(
        field_name="patient",
        description=(
            "профиль пациента отправившего форму"
        )
    )
    assert (
        new_schedule.date_from.strftime(DATETIME_FORMAT)
        == appointment_form_data["date_from"]
    ), assert_msg_pattern.format(
        field_name="date_from",
        description=(
            "дата начала приема из переданной формы"
        )
    )
    assert (
        new_schedule.date_due.strftime(DATETIME_FORMAT)
        == appointment_form_data["date_due"]
    ), assert_msg_pattern.format(
        field_name="date_due",
        description=(
            "дата окончания приема из переданной формы"
        )
    )
    assertRedirects(
        response, index_url[0], fetch_redirect_response=False, msg_prefix=(
            "Убедитесь, что после отправки корректной формы для записи к "
            "врачу пользователь перенаправляется на главную страницу."
        )
    )


def test_patient_cant_create_appointment_if_no_free_doctors(
        another_patient_client, new_schedule_url, appointment_form_data,
        add_appointment
):
    url, _ = new_schedule_url
    appointment_form_data["date_from"] = add_appointment.date_from.strftime(
        DATETIME_FORMAT
    )
    appointment_form_data["date_due"] = add_appointment.date_due.strftime(
        DATETIME_FORMAT
    )
    response = another_patient_client.post(
        url, data=appointment_form_data, follow=True
    )
    assert response.resolver_match.route == url.lstrip("/"), (
        "Убедитесь, что при попытке пациента записаться на прием на "
        "время, когда нет свободного врача, пользователь остается на "
        f"странице для записи к врачу - `{url}`."
    )
    assert response.context["form"].errors, (
        "Убедитесь, что при попытке пациента записаться на прием на время, "
        f"когда нет свободного врача, на странице записи к врачу (`{url}`) "
        "форма содержит сообщение об ошибке."
    )


@pytest.mark.usefixtures("another_doctor_with_specialization")
def test_patient_cant_create_appointment_on_same_time(
        patient_client, new_schedule_url, appointment_form_data,
        add_appointment
):
    url, _ = new_schedule_url
    appointment_form_data["date_from"] = add_appointment.date_from.strftime(
        DATETIME_FORMAT
    )
    appointment_form_data["date_due"] = add_appointment.date_due.strftime(
        DATETIME_FORMAT
    )
    response = patient_client.post(
        url, data=appointment_form_data, follow=True
    )
    assert response.resolver_match.route == url.lstrip("/"), (
        "Убедитесь, что при попытке пациента записаться на прием на "
        "время, которое у него уже занято, пользователь остается на "
        f"странице для записи к врачу - `{url}`."
    )
    assert response.context["form"].errors, (
        "Убедитесь, что при попытке пациента записаться на прием на время, "
        f"которое у него уже занято, на странице записи к врачу (`{url}`) "
        "форма содержит сообщение об ошибке."
    )


@pytest.mark.parametrize(
    "client, user_description, expected_status_code",
    (
        (
            pytest.lazy_fixture("anonymous_client"),
            "незарегистрированного пользователя",
            HTTPStatus.FOUND
        ),
        (
            pytest.lazy_fixture("doctor_client"),
            "врача",
            HTTPStatus.FORBIDDEN
        )
    ),
    ids=("anonymous", "doctor")
)
def test_doctor_and_anonymous_user_can_not_create_new_appointment(
        doctor_schedule_model, client, user_description, expected_status_code,
        new_schedule_url, appointment_form_data
):
    url, _ = new_schedule_url
    response = client.post(url, data=appointment_form_data)
    assert response.status_code == expected_status_code, (
        f"Убедитесь, что при попытке {user_description} отправить форму для "
        "записи к врачу возвращает ответ со статус-кодом "
        f"{expected_status_code.value}."
    )
    assert doctor_schedule_model.objects.count() == 0, (
        f"Убедитесь, что при попытке {user_description} отправить форму для "
        "записи к врачу не создается запись в базе данных."
    )


@pytest.mark.usefixtures("add_old_appointment")
def test_patient_can_create_review(
        review_model, doctor_profile_model, patient_client, doctor,
        review_form_data, add_review_url
):
    url, verbose_url = add_review_url
    doctor_profile = doctor_profile_model.objects.get(user=doctor)
    patient_client.post(url, data=review_form_data)
    assert review_model.objects.count() == 1, (
        "Убедитесь, что корректно заполненная форма для оценки врача, "
        f"отправленная со страницы `{verbose_url}`, создает новую "
        "запись в базе данных с отзывом."
    )
    new_review = review_model.objects.get()
    common_assert_msg = (
        "Убедитесь, что при создании отзыва о враче через форму на старнице "
        "`{verbose_url}`, в поле `{field_name}` создаваемого объекта класса "
        "`Review` добавляется значение из соответствующего поля формы."
    )
    assert new_review.doctor == doctor_profile, (
        "Убедитесь, что при создании отзыва о враче через форму на старнице "
        f"`{verbose_url}`, в поле `doctor` создаваемого объекта класса "
        "`Review` добавляется профиль врача с id полученным из запроса "
        "пользователя."
    )
    assert new_review.text == review_form_data["text"], (
        common_assert_msg.format(verbose_url=verbose_url, field_name="text")
    )
    assert new_review.rating == review_form_data["rating"], (
        common_assert_msg.format(verbose_url=verbose_url, field_name="rating")
    )
    assert new_review.author_name == review_form_data["author_name"], (
        common_assert_msg.format(
            verbose_url=verbose_url, field_name="author_name"
        )
    )


@pytest.mark.usefixtures("add_old_appointment")
def test_invalid_form_cant_create_review(
        review_model, patient_client, review_form_data, add_review_url
):
    url, verbose_url = add_review_url
    review_form_data.pop("rating")
    patient_client.post(url, data=review_form_data)
    assert review_model.objects.count() == 0, (
        "Убедитесь, что некорректно заполненная форма для оценки врача, "
        f"отправленная со страницы `{verbose_url}`, не создает новую "
        "запись в базе данных с отзывом."
    )


def test_patient_can_edit_profile(
        patient_profile_model, patient_client, patient, patient_profile_url,
        patient_profile_form_data
):
    url, _ = patient_profile_url
    patient_client.post(url, data=patient_profile_form_data)
    patient_profile = patient_profile_model.objects.get(user=patient)
    medcard = patient_profile.medical_card
    assert_message = (
        "Убедитесь, что пациент может изменять данные своего профиля через "
        "форму на странице профиля пациента."
    )
    assert medcard.first_name == patient_profile_form_data["first_name"], (
        assert_message
    )
    assert medcard.disability == patient_profile_form_data["disability"], (
        assert_message
    )
    assert medcard.second_name == patient_profile_form_data["second_name"], (
        assert_message
    )


@pytest.mark.usefixtures("add_appointment")
def test_doctor_cat_edit_his_patient_profile(
        patient_profile_model, doctor_client, patient, patient_profile_url,
        patient_profile_form_data
):
    url, _ = patient_profile_url
    doctor_client.post(url, data=patient_profile_form_data)
    patient_profile = patient_profile_model.objects.get(user=patient)
    medcard = patient_profile.medical_card
    assert_message = (
        "Убедитесь, что врач может изменять данные профиля пациента, "
        "записанного на прием, через форму на странице профиля пациента."
    )
    assert medcard.first_name == patient_profile_form_data["first_name"], (
        assert_message
    )
    assert medcard.second_name == patient_profile_form_data["second_name"], (
        assert_message
    )


def test_invalid_form_doesnt_edit_profile(patient_client, patient_profile_url):
    url, _ = patient_profile_url
    response = patient_client.post(url, data={"bitth_date": "string"})
    assert response.resolver_match.route == "profile/<int:patient_id>/", (
        "Убедитесь, что при отправке некорректно заполненной формы на "
        "редактирование медицинской карты, пользователь остается на "
        f"странице для профиля пациента - `{url}`."
    )
    assert response.context["form"].errors, (
        "Убедитесь, что при отправке некорректно заполненной формы на "
        "редактирование медицинской карты со страницы профиля пациента "
        "форма,полученная в ответе, содержит сообщение об ошибке."
    )


def test_doctor_catn_edit_non_scheduled_patient_profile(
        patient_profile_model, medical_card_model, doctor_client, patient,
        patient_profile_url, patient_profile_form_data
):
    url, _ = patient_profile_url
    patient_profile = patient_profile_model.objects.get(user=patient)
    initial_medcard = patient_profile.medical_card
    doctor_client.post(url, data=patient_profile_form_data)
    updated_medcard = medical_card_model.objects.get(pk=initial_medcard.pk)
    assert_message = (
        "Убедитесь, что врач не может изменять данные профиля пациента, "
        "не записанного на прием, через форму на странице профиля пациента."
    )
    assert initial_medcard.first_name == updated_medcard.first_name, (
        assert_message
    )
    assert initial_medcard.second_name == updated_medcard.second_name, (
        assert_message
    )


def test_patient_can_add_telegram(
        patient_profile_model, patient_client, patient, add_telegram_url,
        telegram_form_data
):
    url, _ = add_telegram_url
    patient_client.post(url, data=telegram_form_data)
    patient_profile = patient_profile_model.objects.get(user=patient)
    assert_message = (
        "Убедитесь, что пациент может добавлять Telegram аккаунт через "
        "форму на странице профиля пациента."
    )
    assert patient_profile.get_telegram(), assert_message
    assert (
        patient_profile.telegram.username == telegram_form_data["username"]
    ), assert_message


@pytest.mark.parametrize("client", (
    pytest.lazy_fixture("doctor_client"),
    pytest.lazy_fixture("admin_client"),
    pytest.lazy_fixture("another_patient_client"),
))
def test_other_users_cant_add_telegram_for_patient(
        patient_profile_model, client, patient, add_telegram_url,
        telegram_form_data
):
    url, _ = add_telegram_url
    client.post(url, data=telegram_form_data)
    patient_profile = patient_profile_model.objects.get(user=patient)
    assert_message = (
        "Убедитесь, что только пациент может добавлять Telegram аккаунт через "
        "форму на странице профиля пациента."
    )
    assert not patient_profile.get_telegram(), assert_message
