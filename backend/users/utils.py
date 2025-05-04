from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    NotFound,
    PermissionDenied,
    MethodNotAllowed
)


def custom_exception_handler(exc, context):
    # Вызов стандартного обработчика исключений DRF
    response = exception_handler(exc, context)

    # Если стандартный обработчик не создал ответ, создаем его вручную
    if response is None:
        if isinstance(exc, ValidationError):
            return Response({'detail': exc.detail},
                            status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(exc, AuthenticationFailed):
            return Response({'detail': 'Неверные учетные данные'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(exc, NotFound):
            return Response({'detail': 'Объект не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        elif isinstance(exc, PermissionDenied):
            return Response(
                {'detail': 'Недостаточно прав'},
                status=status.HTTP_403_FORBIDDEN)
        elif isinstance(exc, MethodNotAllowed):
            return Response({'detail': 'Метод не разрешен'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            return Response({'detail': str(exc)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
