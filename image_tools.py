"""
image_tools.py - image conversion helpers used by the converter pages.

Quality rules used here:
  * Image -> PDF: JPEG photos are put inside the PDF exactly as they are
    (no re-compression = zero quality loss). Other formats (PNG, WEBP, BMP...)
    are stored losslessly. This is done with the `img2pdf` library.
  * Image -> JPEG: saved at quality 100 with 4:4:4 colour (no colour
    sub-sampling), original resolution, colour profile kept. That is the
    highest quality a JPEG file can have.
"""

import io
import zipfile

import img2pdf
from PIL import Image, ImageOps

# iPhone photos (.heic) work if the optional pillow-heif package is installed
try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False

INPUT_TYPES = ["jpg", "jpeg", "png", "webp", "bmp", "tif", "tiff", "gif"]
if HEIC_SUPPORTED:
    INPUT_TYPES += ["heic", "heif"]

PAGE_SIZES_MM = {
    "A4": (210, 297),
    "Letter": (215.9, 279.4),
    "A3": (297, 420),
}


# ---------------------------------------------------------------- helpers
def open_image(data: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(data))
    if getattr(img, "n_frames", 1) > 1:  # animated GIF/WebP -> first frame
        img.seek(0)
    return img


def flatten(img: Image.Image, background=(255, 255, 255)) -> Image.Image:
    """Replace transparent areas with a solid colour (JPEG and PDF pages have no transparency)."""
    has_alpha = img.mode in ("RGBA", "LA", "PA") or (
        img.mode == "P" and "transparency" in img.info
    )
    if has_alpha:
        rgba = img.convert("RGBA")
        base = Image.new("RGB", rgba.size, background)
        base.paste(rgba, mask=rgba.getchannel("A"))
        return base
    if img.mode in ("RGB", "L"):
        return img
    if img.mode == "CMYK":
        return img.convert("RGB")
    return img.convert("RGB")


def image_info(data: bytes) -> dict:
    img = open_image(data)
    return {"format": img.format, "width": img.width, "height": img.height, "mode": img.mode}


def human_size(n_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n_bytes < 1024 or unit == "GB":
            return f"{n_bytes:.0f} {unit}" if unit == "B" else f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024


# ---------------------------------------------------------------- image -> PDF
def _pdf_ready_bytes(data: bytes) -> bytes:
    """
    Return bytes that img2pdf can embed.
    JPEGs are returned untouched (embedded with zero quality loss).
    Everything else is converted to lossless PNG.
    """
    img = open_image(data)
    if img.format == "JPEG" and img.mode in ("RGB", "L", "CMYK"):
        return data
    img = ImageOps.exif_transpose(img)
    img = flatten(img)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=False)
    return buf.getvalue()


def images_to_pdf(images: list[bytes], page_size: str = "Original",
                  margin_mm: float = 0, dpi: int = 300) -> bytes:
    """
    images    - list of image file bytes, in page order
    page_size - "Original" (page = image size at `dpi`), "A4", "Letter" or "A3"
    margin_mm - white border around each image (for A4/Letter/A3)
    """
    if not images:
        raise ValueError("No images given.")
    prepared = [_pdf_ready_bytes(d) for d in images]

    if page_size == "Original":
        layout = img2pdf.get_fixed_dpi_layout_fun((dpi, dpi))
    else:
        w_mm, h_mm = PAGE_SIZES_MM[page_size]
        border = img2pdf.mm_to_pt(margin_mm)
        layout = img2pdf.get_layout_fun(
            pagesize=(img2pdf.mm_to_pt(w_mm), img2pdf.mm_to_pt(h_mm)),
            border=(border, border),
            fit=img2pdf.FitMode.into,  # fit inside the page, keep proportions
            auto_orient=True,          # landscape photo -> landscape page
        )

    return img2pdf.convert(
        prepared,
        layout_fun=layout,
        rotation=img2pdf.Rotation.ifvalid,  # respect phone photo rotation
    )


# ---------------------------------------------------------------- image -> JPEG
def to_jpeg(data: bytes, quality: int = 100, background=(255, 255, 255),
            max_side: int | None = None) -> bytes:
    """
    Convert any image to JPEG.
    quality  - 1..100 (100 = best)
    max_side - shrink so the longest side is at most this many pixels (None = keep size)
    """
    img = open_image(data)
    icc = img.info.get("icc_profile")
    dpi = img.info.get("dpi")
    img = ImageOps.exif_transpose(img)  # fix sideways phone photos
    img = flatten(img, background)

    if max_side and max(img.size) > max_side:
        img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

    save_args = {
        "format": "JPEG",
        "quality": int(quality),
        "subsampling": 0 if quality >= 90 else 2,  # 0 = 4:4:4 full colour detail
        "optimize": True,
    }
    if icc:
        save_args["icc_profile"] = icc
    if dpi:
        save_args["dpi"] = tuple(int(round(v)) for v in dpi)

    buf = io.BytesIO()
    img.save(buf, **save_args)
    return buf.getvalue()


def make_zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as z:  # JPEGs are already compressed
        for name, content in files.items():
            z.writestr(name, content)
    return buf.getvalue()


def unique_name(name: str, used: set) -> str:
    base, ext = (name.rsplit(".", 1) + [""])[:2]
    candidate, i = name, 2
    while candidate in used:
        candidate = f"{base}_{i}.{ext}" if ext else f"{base}_{i}"
        i += 1
    used.add(candidate)
    return candidate
