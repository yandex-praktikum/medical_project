import re
from collections import defaultdict
from dataclasses import dataclass
from inspect import getsource
from typing import Callable, Union

from django.core.exceptions import FieldDoesNotExist
from django.core.validators import BaseValidator
from django.db import models


def get_clean_source_code(raw_src: str) -> str:
    comment_pattern = re.compile(r"\s*#[^\n]*")
    return re.sub(comment_pattern, "", raw_src)


@dataclass
class FieldInfo:
    field_type: type[models.Field]
    params: dict[str, Union[str, int, bool]]


@dataclass
class ValidatorInfo:
    limit: int
    verbose_name: str


class CheckModelsInfo:
    """Сheck model field types, field parameters and verbose names (fields
    and models).

    Call the class object to initiate tests.
    """

    COMMON_ASSERT_MESSAGE = (
        "Убедитесь, что параметр `{param_name}` поля `{field_name}` модели "
        "`{model_name}` имеет значение `{expected_value}`."
    )

    def __init__(
            self,
            model: type[models.Model],
            field_map: dict[str, FieldInfo],
            names_map: dict[str, str] = {}
            ) -> None:
        self._model = model
        self._field_map = field_map
        self._names_map = names_map
        SPECIFIC_PARAMS_METHODS_MAP: dict[str, Callable] = {
            "related_model": self.check_related_model,
            "on_delete": self.check_on_delete,
            "related_name": self.check_related_name,
            "validators": self.check_validators
        }
        self.SPECIFIC_PARAMS_METHODS_MAP = (
            defaultdict(
                lambda: self.default_check,
                SPECIFIC_PARAMS_METHODS_MAP
            )
        )

    def check_fields(self) -> None:
        model_name = self._model.__name__
        for field_name, field_info in self._field_map.items():
            try:
                field = self._model._meta.get_field(field_name)
            except FieldDoesNotExist:
                raise AssertionError(
                    f"Убедитесь, что в модели `{model_name}` есть поле "
                    f"`{field_name}`."
                )
            assert isinstance(field, field_info.field_type), (
                f"Убедитесь, что для поля `{field_name}` модели "
                f"`{model_name}` указан тип "
                f"`{field_info.field_type.__name__}`."
            )
            for param_name, expected_value in field_info.params.items():
                test_method = self.SPECIFIC_PARAMS_METHODS_MAP[param_name]
                assert test_method(field, expected_value, param_name), (
                    self.COMMON_ASSERT_MESSAGE.format(
                        field_name=field_name,
                        model_name=model_name,
                        param_name=param_name,
                        expected_value=expected_value
                    )
                )

    def get_param_value(self, field, param_name):
        try:
            return getattr(field, param_name)
        except AttributeError:
            raise AssertionError(
                f"Убедитесь, что для поля `{field.name}` модели "
                f"`{self._model.__name__}` задано значение для параметра "
                f"`{param_name}`"
            )

    def default_check(
            self,
            field: type[models.Field],
            expected_value: Union[int, bool],
            param_name: str,
            ) -> bool:
        field_param_value = self.get_param_value(field, param_name)
        return field_param_value == expected_value

    def check_related_model(
            self,
            field: type[models.Field],
            expected_value: Union[int, bool],
            param_name: str,
            ) -> bool:
        param_value = self.get_param_value(field, param_name)
        assert param_value.__name__ == expected_value, (
            f"Убедитесь, что в поле `{field.name}` модели "
            f"`{self._model.__name__}` задана связь с моделью "
            f"`{expected_value}`."
        )
        return True

    def check_on_delete(
            self,
            field: type[models.Field],
            expected_value: str,
            *_
            ) -> bool:
        _, value = expected_value.split('.')  # type: ignore
        model_src = get_clean_source_code(getsource(self._model))
        on_delete_pattern = re.compile(
            rf"{field.name}[\s\S]+on_delete\s*=\s*(models.)?{value}"
        )
        return bool(re.search(on_delete_pattern, model_src))

    def check_related_name(
            self,
            field: type[models.Field],
            expected_value: str,
            *_
            ) -> bool:
        param_value = field.remote_field.related_name
        return bool(param_value == expected_value)

    def check_model_verbose_names(self):
        for field, name in self._names_map.items():
            assert getattr(self._model._meta, field, None) == name, (
                f"Убедитесь, что для поля `{field}` подкласса `Meta` модели "
                f"`{self._model.__name__}` задано значение `{name}`."
            )

    def check_validators(
            self,
            field: type[models.Field],
            expected_vilidators: dict[type[BaseValidator], ValidatorInfo],
            param_name: str,
            ) -> bool:
        model_name = self._model.__name__
        field_validators = self.get_param_value(field, param_name)
        assert field_validators, (
            f"Убедитесь, что для поля `{field.name}` модели "
            f"`{model_name}` добавлен параметр `validators` для проверки "
            "значений поля в соответствии с заданием."
        )
        for validator in field_validators:
            if type(validator) not in expected_vilidators:
                continue
            expected_limit_info = expected_vilidators.pop(type(validator))
            assert validator.limit_value == expected_limit_info.limit, (
                f"Убедитесь, что для поля `{field.name}` модели "
                f"`{model_name}` {expected_limit_info.verbose_name} является "
                f"{expected_limit_info.limit}."
            )
        assert not expected_vilidators, (
            f"Убедитесь, что для значений поля `{field.name}` модели "
            f"`{model_name}` установлены предусмотренные заданием ограничения."
        )
        return True

    def __call__(self) -> None:
        self.check_fields()
        self.check_model_verbose_names()
