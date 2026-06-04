from __future__ import annotations

import json
from datetime import date
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator


class SourceType(StrEnum):
    LEGISLATION = "legislation"
    COLLECTIVE_AGREEMENT = "collective_agreement"
    OFFICIAL_GUIDE = "official_guide"
    CASE_LAW = "case_law"
    FAQ = "faq"


class Territory(StrEnum):
    ESTATAL = "estatal"
    AUTONOMICO = "autonomico"
    PROVINCIAL = "provincial"
    MUNICIPAL = "municipal"
    EUROPEO = "europeo"
    OTHER = "other"


class LegalRank(StrEnum):
    LAW = "law"
    ROYAL_DECREE = "royal_decree"
    COLLECTIVE_AGREEMENT = "collective_agreement"
    OFFICIAL_GUIDANCE = "official_guidance"
    CASE_LAW = "case_law"
    OTHER = "other"


class SourceStatus(StrEnum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    PENDING_REVIEW = "pending_review"
    DRAFT = "draft"


class RagSourceMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=300)
    source_type: SourceType
    source_url: HttpUrl
    publisher: str = Field(min_length=1, max_length=200)
    jurisdiction: str = Field(default="Espana", min_length=1, max_length=100)
    territory: Territory
    sector: str = Field(default="general", min_length=1, max_length=120)
    legal_rank: LegalRank
    published_at: date | None = None
    updated_at: date | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    status: SourceStatus
    language: str = Field(default="es", min_length=2, max_length=10)
    content_path: str | None = Field(default=None, min_length=1, max_length=300)
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("source_id")
    @classmethod
    def source_id_must_be_stable_slug(cls, value: str) -> str:
        allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-")
        if any(character not in allowed for character in value):
            raise ValueError("source_id solo puede contener minusculas, numeros y guiones.")
        return value

    @field_validator("language")
    @classmethod
    def language_must_be_lowercase(cls, value: str) -> str:
        return value.lower()

    @model_validator(mode="after")
    def valid_to_must_not_precede_valid_from(self) -> "RagSourceMetadata":
        if self.valid_from is not None and self.valid_to is not None:
            if self.valid_to < self.valid_from:
                raise ValueError("valid_to no puede ser anterior a valid_from.")
        return self

    def to_chunk_metadata(
        self, chunk_id: str, section: str, citation_label: str
    ) -> "RagChunkMetadata":
        return RagChunkMetadata(
            chunk_id=chunk_id,
            source_id=self.source_id,
            section=section,
            citation_label=citation_label,
            source=self,
        )


class RagChunkMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: str = Field(min_length=1, max_length=200)
    source_id: str = Field(min_length=1, max_length=120)
    section: str = Field(min_length=1, max_length=200)
    citation_label: str = Field(min_length=1, max_length=500)
    source: RagSourceMetadata


def load_source_manifest(path: Path) -> list[RagSourceMetadata]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("El manifiesto de corpus debe ser una lista de fuentes.")

    sources = [RagSourceMetadata.model_validate(item) for item in payload]
    source_ids = [source.source_id for source in sources]
    duplicate_ids = sorted(
        {source_id for source_id in source_ids if source_ids.count(source_id) > 1}
    )
    if duplicate_ids:
        raise ValueError(f"source_id duplicado: {', '.join(duplicate_ids)}")

    return sources
