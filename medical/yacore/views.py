from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    AccessMixin,
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View

from users.models import PatientProfile
from yacore.forms import (
    MedicalCardForm,
    TelegramForm,
)

PAGE = 4


def page_not_found(request, exception):
    # Страница для перенаправления статус кода 404
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def page_forbidden(request, exception):
    return render(request, "misc/403.html", {"path": request.path}, status=403)


def server_error(request):
    return render(request, "misc/500.html", status=500)


class IndexView(View):
    template = 'schedindexle.html'

    def get(self, request, *args, **kwargs):
        # тут нужно описать получение всех врачей в поликлинике
        pass


class ScheduleView(LoginRequiredMixin, View):
    template = 'schedule.html'

    def get(self, request, *args, **kwargs):
        # тут нужно описать получение доступных записей у пациента
        pass


class RecordInDoctorView(UserPassesTestMixin, View):
    template = 'new_schedule.html'

    def test_func(self):
        # проверка что страницу может открыть только пациент
        return (
            self.request.user.is_authenticated
            and self.request.user.is_patient()
        )

    def get(self, request, *args, **kwargs):
        # тут нужно описать получение формы для записи к врачу
        pass

    def post(self, request, *args, **kwargs):
        # тут нужно сохранять полученную форму для записи к врачу
        pass


class ReviewView(UserPassesTestMixin, View):
    template = 'add_comment.html'

    def test_func(self):
        # Добавить проверку, что страницу может открыть только пациент
        pass

    def get(self, request, *args, **kwargs):
        # тут нужно описать получение формы для добавления отзыва на врача
        pass

    def post(self, request, *args, **kwargs):
        # тут нужно сохранять полученную форму для добавления отзыва на врача
        pass


class DoctorView(View):
    template = "doctor_detail.html"

    def get(self, request, *args, **kwargs):
        # Детальная страница врача
        pass


class AuthorOrDoctorRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        # Проверка, что страницу может посмотреть только владелец профиля
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        patient_id = kwargs.get("patient_id")
        if request.user.is_patient():
            patient = request.user.patient
            if patient.id != patient_id:
                return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class ProfileView(AuthorOrDoctorRequiredMixin, View):
    template = "profile.html"

    def get(self, request, *args, **kwargs):
        # get запрос для открытия страницы профиля пациента
        patient = get_object_or_404(
            PatientProfile,
            id=kwargs.get("patient_id"),
        )
        form = MedicalCardForm(instance=patient.medical_card)
        form_telegram = TelegramForm(instance=patient.get_telegram())
        return render(
            request,
            self.template,
            {
                "form": form,
                "patient": patient,
                "form_telegram": form_telegram,
            },
        )

    def post(self, request, *args, **kwargs):
        # Post запрос для сохранения медецинской карточки
        patient = get_object_or_404(
            PatientProfile,
            id=kwargs.get("patient_id"),
        )
        form = MedicalCardForm(
            request.POST or None,
            files=request.FILES or None,
            instance=patient.medical_card,
        )
        if not form.is_valid():
            return render(
                request,
                "profile.html",
                {
                    "form": form,
                    "patient": patient,
                    "form_telegram": (
                        TelegramForm(instance=patient.get_telegram())
                    )
                }
            )
        medical_card = form.save(commit=False)
        medical_card.address_permanent = {
            "area": form.cleaned_data.get("area"),
            "district": form.cleaned_data.get("district"),
            "human_settlement": form.cleaned_data.get("human_settlement"),
            "street": form.cleaned_data.get("street"),
            "house": form.cleaned_data.get("house"),
            "corpus": form.cleaned_data.get("corpus"),
            "flat": form.cleaned_data.get("flat"),
        }
        medical_card.address_place_of_stay = medical_card.address_permanent
        medical_card.place_of_work = {
            "name": form.cleaned_data.get("name"),
            "profession": form.cleaned_data.get("profession"),
            "position": form.cleaned_data.get("position"),
            "dependent": form.cleaned_data.get("dependent"),
        }
        medical_card.save()
        patient.medical_card = medical_card
        patient.save()
        return redirect("profile", patient_id=patient.id)


class DoctorPatientsView(LoginRequiredMixin, UserPassesTestMixin, View):
    template = "doctor_patients.html"

    def test_func(self):
        # Добавить проверку, что страницу может открыть только доктор
        pass

    def get(self, request, *args, **kwargs):
        # тут нужно описать получение всех пациентов врача
        pass


@login_required
def add_telegram(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    instance = patient.get_telegram()
    form = TelegramForm(request.POST or None, instance=instance)
    if form.is_valid():
        telegram = form.save(commit=False)
        telegram.patient = patient
        telegram.save()
    return redirect("profile", patient_id=patient.id)
