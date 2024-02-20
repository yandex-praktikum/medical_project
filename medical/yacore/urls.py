from django.urls import path

from yacore.views import (
    DoctorPatientsView,
    DoctorView,
    IndexView,
    ProfileView,
    RecordInDoctorView,
    ReviewView,
    ScheduleView,
    add_telegram,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("new/", RecordInDoctorView.as_view(), name="new_schedule"),
    path("schedule/", ScheduleView.as_view(), name="schedule"),
    path(
        "<int:doctor_id>/comment/",
        ReviewView.as_view(),
        name="add_comment",
    ),
    path(
        "doctor/<int:doctor_id>/",
        DoctorView.as_view(),
        name="doctor_detail",
    ),
    path(
        "profile/<int:patient_id>/",
        ProfileView.as_view(),
        name="profile",
    ),
    path("patients/", DoctorPatientsView.as_view(), name="patients"),
    path("add_telegram/", add_telegram, name="add_telegram"),
]
