# app/schemas_secure.py
import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SecureEntryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(
        min_length=1,
        max_length=255,
        pattern=r'^[\w\s\-\.,!?@#$%^&*()+=:;"' "<>/\\|\\[\\]{}~`]+$",
    )
    kind: str = Field(pattern=r"^(book|article|paper|video)$")
    link: Optional[str] = Field(None, pattern=r"^https?://[^\s]+$")
    status: str = Field(pattern=r"^(todo|reading|done|archived)$")

    @field_validator("title")
    @classmethod
    def validate_title_content(cls, v: str) -> str:
        # Защита от потенциальных XSS векторов
        dangerous_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"expression\s*\(",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Potentially dangerous content detected")

        return v

    @field_validator("link")
    @classmethod
    def validate_url_scheme(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("URL must use http or https scheme")
        return v
