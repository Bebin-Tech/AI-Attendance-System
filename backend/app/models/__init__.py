"""Database metadata and the explicitly protected biometric ORM mapping."""

from sqlalchemy.orm import deferred, registry

from app.models.schema import biometric_templates, metadata

mapper_registry = registry(metadata=metadata)


class BiometricTemplate:
    """Encrypted bytes require an explicit biometric-service query; never lazy-load them."""


mapper_registry.map_imperatively(
    BiometricTemplate,
    biometric_templates,
    properties={
        field: deferred(biometric_templates.c[field], raiseload=True)
        for field in ("ciphertext", "wrapped_key", "nonce")
    },
)

__all__ = ["BiometricTemplate", "metadata"]
