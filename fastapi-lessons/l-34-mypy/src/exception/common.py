from typing import Any, Dict, Optional

from fastapi import HTTPException


class CustomException(HTTPException):
    def __init__(
            self,
            status_code: int,
            detail: str,
            error_code: Optional[str] = None,
            extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra = extra or {}


class UnauthorizedException(CustomException):
    def __init__(self, action: str):
        detail = f"Unauthorized to perform action: {action}"
        super().__init__(
            status_code=401,
            detail=detail,
            error_code="UNAUTHORIZED",
            extra={"action": action}
        )


class AlreadyExistsException(CustomException):
    def __init__(self, obj_name: str):
        detail = f"Such object already exists: {obj_name}"
        super().__init__(
            status_code=400,
            detail=detail,
            error_code="BAD_REQUEST",
            extra={"object_name": obj_name}
        )


class ForbiddenException(CustomException):
    def __init__(self, action: str, reason: Optional[str] = None):
        detail = f"Access denied: {action}"
        if reason:
            detail += f" ({reason})"
        super().__init__(
            status_code=403,
            detail=detail
        )
        self.error_code = "FORBIDDEN"
        self.extra = {"action": action, "reason": reason}


class NotFoundException(CustomException):
    def __init__(self, resource: str, filter: Optional[Dict[str, Any]] = None):
        detail = f"{resource}"
        extra = {"resource": resource}
        if filter is not None:
            extra["resource_filter"] = str(filter)
        super().__init__(
            status_code=404,
            detail=detail,
            error_code="NOT_FOUND",
            extra=extra
        )
