import os
import io
import importlib.util
from pathlib import Path
from werkzeug.datastructures import FileStorage

# Import the app module by file path so we can run in CI
spec = importlib.util.spec_from_file_location('app', os.path.join(os.path.dirname(__file__), '..', 'app.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_normalize_db_url_strips_sslmode_and_rewrites_pg8000_if_needed():
    url = 'postgres://user:pass@host:5432/dbname?sslmode=require&other=1'
    normalized = mod._normalize_db_url_for_driver(url)
    # Should not include sslmode
    assert 'sslmode' not in normalized
    # If function rewrites to pg8000 it will include 'pg8000'
    # Accept either rewrite or same value without sslmode
    assert normalized.startswith('postgresql') or normalized.startswith('postgres://')


def test_save_uploaded_file_and_serve_local(tmp_path):
    # Ensure the app upload folder is local for this test
    upload_folder = tmp_path / 'uploads'
    upload_folder.mkdir(parents=True, exist_ok=True)
    mod.app.config['UPLOAD_FOLDER'] = str(upload_folder)

    # Create a dummy file storage
    data = b'hello world'
    stream = io.BytesIO(data)
    fs = FileStorage(stream=stream, filename='test_file.png', content_type='image/png')

    # Save the file using the helper
    saved_path = mod._save_uploaded_file(fs, 'test_file.png', mime_type='image/png')
    assert saved_path.endswith('/uploads/images/test_file.png') or saved_path.startswith('http')

    # If local, ensure file exists and serve via the uploads route
    if saved_path.startswith('/uploads/images'):
        filename = Path(saved_path).name
        file_on_disk = upload_folder / filename
        assert file_on_disk.exists()

        # Use test client to fetch the file
        client = mod.app.test_client()
        resp = client.get(f'/uploads/images/{filename}')
        assert resp.status_code == 200
        assert resp.data == data

        # Cleanup
        file_on_disk.unlink()
