"""Local test for upload persistence (DB base64 and optional S3).

Run with: python tools/test_upload_local.py

This script uses the app context to store a small fake PNG into the Settings
`logo_image_data` column and prints verification output. If S3 env vars are
configured it will also attempt an S3 upload (will require valid AWS creds).
"""
from io import BytesIO
from app import app, db, Settings, encode_image_to_base64, is_s3_configured, upload_to_s3


def run():
    with app.app_context():
        db.create_all()
        settings = Settings.query.first()
        if not settings:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()

        # Create a tiny fake PNG-like payload
        fake_png = BytesIO()
        fake_png.write(b"\x89PNG\r\n\x1a\n")
        fake_png.write(b"FAKEPNGDATA" * 20)
        fake_png.seek(0)

        mime = 'image/png'
        b64 = encode_image_to_base64(fake_png)
        settings.logo_image_data = b64
        settings.logo_image_mime = mime
        settings.logo_image = '/database/test_logo.png'
        db.session.commit()

        print('Wrote logo_image_data (bytes):', len(settings.logo_image_data) if settings.logo_image_data else 0)
        print('settings.get_logo_url():', settings.get_logo_url())

        if is_s3_configured():
            fake_png.seek(0)
            key = f"test/logo_{int(__import__('time').time())}.png"
            url = upload_to_s3(fake_png, key, mime_type=mime)
            print('S3 upload result:', url)
        else:
            print('S3 not configured — skipped S3 test')


if __name__ == '__main__':
    run()
