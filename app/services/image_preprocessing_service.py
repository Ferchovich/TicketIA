"""Image preprocessing service for preparing ticket images for OCR."""
import io
import logging
from typing import Tuple, Optional
from app.config import get_settings
from app.utils.exceptions import FileTooLargeError, UnsupportedFileTypeError

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "application/pdf",
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}


def validate_file(filename: str, content_type: str, size: int) -> None:
    """Validate uploaded file before processing."""
    settings = get_settings()

    # Validate size
    if size > settings.max_upload_bytes:
        raise FileTooLargeError(
            f"File exceeds maximum allowed size of {settings.max_upload_mb}MB"
        )

    # Validate content type
    if content_type.lower() not in ALLOWED_MIME_TYPES:
        raise UnsupportedFileTypeError(
            f"File type '{content_type}' is not supported. "
            f"Allowed types: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
        )

    # Validate extension
    import os
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"File extension '{ext}' is not supported. "
            f"Allowed extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )


async def preprocess_image(
    file_bytes: bytes,
    content_type: str,
) -> Tuple[bytes, dict]:
    """
    Preprocess image for OCR: normalize, resize if needed, convert to standard format.
    Returns (processed_bytes, metadata_dict).
    This is a basic preprocessing pipeline that can be enhanced.
    """
    metadata = {
        "original_size": len(file_bytes),
        "content_type": content_type,
        "preprocessed": False,
    }

    if content_type == "application/pdf":
        # PDFs are returned as-is for now
        logger.debug("PDF detected, skipping image preprocessing")
        return file_bytes, metadata

    try:
        from PIL import Image, ImageFilter

        img = Image.open(io.BytesIO(file_bytes))
        original_mode = img.mode

        # Convert to RGB if needed
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Resize if too large (max 4000px in any dimension for OCR)
        max_dim = 4000
        if max(img.size) > max_dim:
            ratio = max_dim / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            logger.debug("Resized image to %s", new_size)

        # Convert greyscale for better OCR if not already
        if img.mode == "RGB":
            # Slight sharpening for better OCR
            img = img.filter(ImageFilter.SHARPEN)

        output = io.BytesIO()
        img.save(output, format="PNG", optimize=True)
        processed_bytes = output.getvalue()

        metadata.update({
            "preprocessed": True,
            "processed_size": len(processed_bytes),
            "dimensions": img.size,
            "mode": img.mode,
        })

        return processed_bytes, metadata

    except ImportError:
        logger.warning("Pillow not available, skipping image preprocessing")
        return file_bytes, metadata
    except Exception as exc:
        logger.warning("Image preprocessing failed: %s", exc)
        return file_bytes, metadata
