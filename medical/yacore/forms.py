from django import forms
from medical.settings import DATE_INPUT_FORMATS
from users.models import MedicalCard, Review, Telegram

from yacore.models import DoctorSchedule
from yacore.utils import is_doctor_schedule


class DoctorScheduleAdminForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = (
            "is_complete",
            "is_cancelled",
            "specialization",
            "doctor",
            "patient",
            "date_from",
            "date_due",
            "feedback",
        )

    def clean(self):
        data = super().clean()
        doctor = data.get("doctor")
        if is_doctor_schedule(
            patient=data.get("patient"),
            doctor=doctor,
            date_from=data.get("date_from"),
            date_due=data.get("date_due"),
            id=self.instance.id,
        ):
            exc = forms.ValidationError(
                "Период пересекается с другим объектом",
            )
            self._errors["date_from"] = self.error_class(exc.messages)
            self._errors["date_due"] = self.error_class(exc.messages)
            raise exc
        specialization = data.get("specialization")
        if not doctor.specializations.filter(id=specialization.id).exists():
            exc = forms.ValidationError(
                "У врача нет такой специализации",
            )
            self._errors["specialization"] = self.error_class(exc.messages)
        return data


class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        widgets = {
            "date_from": forms.DateInput(
                attrs={
                    "type": "datetime-local",
                }
            ),
            "date_due": forms.DateInput(
                attrs={
                    "type": "datetime-local",
                }
            ),
        }
        fields = (
            "specialization",
            "date_from",
            "date_due",
        )
        labels = {
            "specialization": "Врач по направлению",
            "date_due": "Период по",
            "date_from": "Период записи с",
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = (
            "author_name",
            "text",
            "rating",
        )


class TelegramForm(forms.ModelForm):
    class Meta:
        model = Telegram
        fields = ("username",)


class MedicalCardForm(forms.ModelForm):
    area = forms.CharField(label="Область проживания")
    district = forms.CharField(
        label="Район проживания",
        required=False,
    )
    human_settlement = forms.CharField(
        label="Населенный пункт проживания",
    )
    street = forms.CharField(label="Улица проживания")
    house = forms.CharField(label="Дом проживания")
    corpus = forms.CharField(
        label="Корпус проживания",
        required=False,
    )
    flat = forms.CharField(label="Квартира проживания")
    name = forms.CharField(
        label="Название фирмы, с места работы",
        required=False,
    )
    profession = forms.CharField(
        label="Профессия",
        required=False,
    )
    position = forms.CharField(
        label="Должность, с места работы",
        required=False,
    )
    dependent = forms.CharField(
        label="Иждивенец",
        required=False,
    )
    birth_date = forms.DateField(
        label="Дата рождения",
        input_formats=DATE_INPUT_FORMATS,
    )

    class Meta:
        model = MedicalCard
        fields = "__all__"
        exclude = (
            "address_permanent",
            "address_place_of_stay",
            "place_of_work",
        )
        widgets = {
            "birth_date": forms.DateInput(
                attrs={
                    "type": "datetime-local",
                }
            )
        }
