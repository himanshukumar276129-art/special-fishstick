import qrcode
import os
import base64
from io import BytesIO

class QRService:
    def __init__(self, output_dir="static/generated/qr"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_qr(self, data, filename=None):
        """
        Generates a QR code and returns the base64 encoded image or saves to file.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO for base64 or conversion
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Return as data URL
        return f"data:image/png;base64,{img_str}"

qr_service = QRService()
