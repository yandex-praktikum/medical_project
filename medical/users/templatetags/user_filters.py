from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    # отвечает за добавление css стилей
    return field.as_widget(attrs={"class": css})


@register.filter
def create_range(value, start_index=0):
    # отвечает за создание цикла внутри html шаблонов;
    return range(start_index, value + start_index)


@register.filter
def get_error(errors_dict, error_item):
    # позволяет достать из формы ошибку и красиво вывести ее на экран.
    return errors_dict[error_item]
