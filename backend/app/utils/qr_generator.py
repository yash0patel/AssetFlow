"""
app/utils/qr_generator.py
──────────────────────────
QR-code generation utility for assets.
Produces PNG bytes using Pillow (no external QR library required via segno).
Install: pip install segno  (add to requirements.txt when implementing)
"""

# TODO: implement QR generation in business-logic phase
# Example usage:
#
#   from app.utils.qr_generator import generate_asset_qr
#   png_bytes = generate_asset_qr(asset_id="AF-2024-001")
#   with open("asset_qr.png", "wb") as f:
#       f.write(png_bytes)


def generate_asset_qr(asset_id: str) -> bytes:
    """
    Generate a QR code PNG for *asset_id* and return raw bytes.
    Placeholder — implement with segno or qrcode library.
    """
    raise NotImplementedError("QR generation not yet implemented.")
