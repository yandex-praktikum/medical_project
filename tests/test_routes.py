from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db

INDEX_URL = pytest.lazy_fixture("index_url")
NEW_SCHEDULE_URL = pytest.lazy_fixture("new_schedule_url")
SHEDULE_URL = pytest.lazy_fixture("schedule_url")
ADD_REVIEW_URL = pytest.lazy_fixture("add_review_url")
DOCTOR_DETAIL_URL = pytest.lazy_fixture("doctor_detail_url")
PATIENT_PROFILE_URL = pytest.lazy_fixture("patient_profile_url")
PATIENTS_URL = pytest.lazy_fixture("patients_url")
ADD_TELEGRAM_URL = pytest.lazy_fixture("add_telegram_url")
LOGIN_URL = pytest.lazy_fixture("login_url")
ADMIN_PAGE_URL = "/admin/"


@pytest.mark.parametrize("url_info, expected_status", [
    (INDEX_URL, HTTPStatus.OK),
    (NEW_SCHEDULE_URL, HTTPStatus.FOUND),
    (SHEDULE_URL, HTTPStatus.FOUND),
    (ADD_REVIEW_URL, HTTPStatus.FOUND),
    (DOCTOR_DETAIL_URL, HTTPStatus.OK),
    (PATIENT_PROFILE_URL, HTTPStatus.FOUND),
    (PATIENTS_URL, HTTPStatus.FOUND),
    (ADD_TELEGRAM_URL, HTTPStatus.FOUND),
    (LOGIN_URL, HTTPStatus.OK),
])
def test_pages_availability_for_unauthorized_users(
        url_info, expected_status, client, login_url
):
    url, verbose_url = url_info
    verbose_url = verbose_url or url
    response = client.get(url)
    assert response.status_code == expected_status, (
        "Убедитесь, что на запрос незарегистрированного пользователя к "
        f"странице с адресом `{verbose_url}` возвращается ответ со "
        f"статус-кодом {expected_status.value}."
    )
    if expected_status == HTTPStatus.FOUND:
        url_to_redirect = f'{login_url[0]}?next={url}'
        assertRedirects(response, url_to_redirect), (
            "Убедитесь, что запрос незарегистрированного пользователя "
            f"странице с адресом к `{verbose_url}` перенаправляется на "
            f"страницу входа на сайт (`{url_to_redirect}`)."
        )


@pytest.mark.parametrize("url_info, expected_status, redirect_to", [
    (INDEX_URL, HTTPStatus.OK, None),
    (NEW_SCHEDULE_URL, HTTPStatus.OK, None),
    (SHEDULE_URL, HTTPStatus.OK, None),
    (ADD_REVIEW_URL, HTTPStatus.OK, None),
    (DOCTOR_DETAIL_URL, HTTPStatus.OK, None),
    (PATIENT_PROFILE_URL, HTTPStatus.OK, None),
    (PATIENTS_URL, HTTPStatus.FORBIDDEN, None),
    (ADD_TELEGRAM_URL, HTTPStatus.FOUND, PATIENT_PROFILE_URL),
])
def test_pages_availability_for_patient(
        url_info, expected_status, redirect_to, patient_client
):
    url, verbose_url = url_info
    verbose_url = verbose_url or url
    response = patient_client.get(url)
    assert response.status_code == expected_status, (
        "Убедитесь, что на запрос пациента к странице с адресом "
        f"`{verbose_url}` возвращается ответ со статус-кодом "
        f"{expected_status.value}."
    )
    if redirect_to:
        assertRedirects(response, redirect_to[0]), (
            "Убедитесь, что запрос пациента к странице с адресом "
            f"`{verbose_url}` после обработки перенаправляется на страницу "
            f"профиля пациента (`{redirect_to[1]}`)."
        )


@pytest.mark.parametrize("url_info, expected_status", [
    (INDEX_URL, HTTPStatus.OK),
    (NEW_SCHEDULE_URL, HTTPStatus.FORBIDDEN),
    (SHEDULE_URL, HTTPStatus.OK),
    (ADD_REVIEW_URL, HTTPStatus.FORBIDDEN),
    (DOCTOR_DETAIL_URL, HTTPStatus.OK),
    (PATIENTS_URL, HTTPStatus.OK),
    (ADD_TELEGRAM_URL, HTTPStatus.NOT_FOUND),
])
def test_pages_availability_for_doctor(
        url_info, expected_status, doctor_client
):
    url, verbose_url = url_info
    verbose_url = verbose_url or url
    response = doctor_client.get(url)
    assert response.status_code == expected_status, (
        "Убедитесь, что на запрос врача к странице с адресом "
        f"`{verbose_url}` возвращается ответ со статус-кодом "
        f"{expected_status.value}."
    )


@pytest.mark.parametrize(
    "url_info, expected_status, additional_fixture",
    [
        (PATIENT_PROFILE_URL, HTTPStatus.FORBIDDEN, None),
        (PATIENT_PROFILE_URL, HTTPStatus.OK,
            pytest.lazy_fixture("add_appointment")),
    ]
)
def test_patient_profile_availability_for_doctor(
        url_info, expected_status, doctor_client, additional_fixture
):
    url, verbose_url = url_info
    verbose_url = verbose_url or url
    response = doctor_client.get(url)
    if additional_fixture:
        assert_message = (
            "Убедитесь, что профиль пациента доступен врачу, к которому "
            "записан пациент.\n"
            f"Заспрос врача к странице с адресом `{verbose_url}` должен "
            f"вернуть ответ со статус-кодом {expected_status.value}."
        )
    else:
        assert_message = (
            "Убедитесь, что профиль пациента, не записанного к врачу и не "
            "посещавшего его ранее, не доступен для такого врача.\n"
            f"Заспрос врача к странице с адресом `{verbose_url}` должен "
            f"вернуть ответ со статус-кодом {expected_status.value}."
        )
    assert response.status_code == expected_status, assert_message


def test_admin_page_availability_for_admin(admin_client):
    response = admin_client.get(ADMIN_PAGE_URL)
    assert response.status_code == HTTPStatus.OK, (
        "Убедитесь, что администратору доступна админ-панель.\n"
        "Запрос администратора к странице с адресом `admin/` должен вернуть "
        "ответ со статус-кодом 200."
    )
