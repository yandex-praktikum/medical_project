from django.db.models import Q

from yacore.models import DoctorSchedule


def is_doctor_schedule(patient, doctor, date_from, date_due, id=None):
    qs = DoctorSchedule.objects.filter(
        Q(
            Q(
                patient=patient,
            )
            | Q(
                doctor=doctor,
            )
        )
        & Q(
            Q(
                date_from__gte=date_from,
                date_due__lte=date_from,
            )
            | Q(
                date_from__gte=date_due,
                date_due__lte=date_due,
            )
        ),
    )
    if id:
        qs = qs.exclude(id=id)
    return qs.exists()
