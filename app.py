import os
from decimal import Decimal
from pathlib import Path
from datetime import datetime, timezone

# lightweight .env loader to avoid requiring the external 'python-dotenv' package
def load_dotenv(path: str = ".env"):
    env_path = Path(path)
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if val and val[0] == '"' and val[-1] == '"':
            val = val[1:-1]
        if key and key not in os.environ:
            os.environ[key] = val

from flask import (
    Flask, render_template, request, redirect, url_for, flash, session,
    send_from_directory, jsonify, abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user, UserMixin
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import requests
import uuid
import smtplib
import ssl
import threading
import time
from email.utils import parseaddr
import json as _json
import logging
import sys

# Optional modern integrations
REDIS_URL = os.environ.get("REDIS_URL", "")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
USE_RQ = False
if REDIS_URL:
    try:
        import importlib
        redis = importlib.import_module("redis")
        rq = importlib.import_module("rq")
        Queue = getattr(rq, "Queue")
        USE_RQ = True
        _redis_conn = redis.from_url(REDIS_URL)
        _rq_queue = Queue("emails", connection=_redis_conn)
    except Exception:
        USE_RQ = False
from email.message import EmailMessage

# Load env
load_dotenv()

BASE_DIR = Path(__file__).parent
# On Vercel serverless, /var/task is read-only; use /tmp instead for file uploads
if os.environ.get("VERCEL") or os.environ.get("VERCEL_URL"):
    UPLOAD_FOLDER = Path("/tmp") / "images"
else:
    UPLOAD_FOLDER = BASE_DIR / "static" / "images"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Helper function for timezone-aware UTC datetime
def utc_now():
    """Return current UTC time as timezone-aware datetime"""
    return datetime.now(timezone.utc)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me")
# Use a writable temporary DB path when running on Vercel serverless (VERCEL env var present)
_env_db = os.environ.get("SQLALCHEMY_DATABASE_URI", "").strip()
if _env_db:
    app.config["SQLALCHEMY_DATABASE_URI"] = _env_db
else:
    if os.environ.get("VERCEL") or os.environ.get("VERCEL_URL"):
        # Vercel serverless functions have a writable /tmp directory
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/data.db"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR / 'data.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB

# Configure structured logging to stdout so Vercel captures full logs and tracebacks
log_level = logging.DEBUG if os.environ.get("DEBUG", "").lower() in ("1", "true", "yes") else logging.INFO
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(log_level)
stream_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
stream_handler.setFormatter(stream_formatter)
if not any(isinstance(h, logging.StreamHandler) for h in app.logger.handlers):
    app.logger.addHandler(stream_handler)
app.logger.setLevel(log_level)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
PAYSTACK_SECRET = os.environ.get("PAYSTACK_SECRET_KEY", "")
PAYSTACK_PUBLIC = os.environ.get("PAYSTACK_PUBLIC_KEY", "")
# Determine Paystack callback dynamically: prefer explicit env var, then Vercel runtime URL, then fallback
_env_callback = os.environ.get("PAYSTACK_CALLBACK_URL", "").strip()
if _env_callback:
    PAYSTACK_CALLBACK = _env_callback
else:
    # Vercel exposes the deployment hostname in VERCEL_URL (or NOW_URL for legacy)
    vercel_url = os.environ.get("VERCEL_URL") or os.environ.get("NOW_URL")
    if vercel_url:
        PAYSTACK_CALLBACK = f"https://{vercel_url.rstrip('/')}/paystack/callback"
    else:
        # sensible default - update to your real domain if different
        PAYSTACK_CALLBACK = os.environ.get("LIVE_DOMAIN", "https://cyberworld-store-86kt.vercel.app") + "/paystack/callback"

# Email / SMTP settings (optional)
MAIL_SERVER = os.environ.get("MAIL_SERVER", "")
MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes")
MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "false").lower() in ("1", "true", "yes")
_env_mail_sender = os.environ.get("MAIL_DEFAULT_SENDER", "").strip()
# Force sender name to 'CYBER WORLD STORE' while allowing custom address via MAIL_USERNAME or MAIL_DEFAULT_SENDER
sender_email = None
mail_username_env = os.environ.get("MAIL_USERNAME")
if mail_username_env:
    sender_email = mail_username_env.strip()
elif _env_mail_sender:
    # extract address if user provided a full 'Name <email>' or just email
    if '<' in _env_mail_sender and '>' in _env_mail_sender:
        try:
            sender_email = _env_mail_sender.split('<', 1)[1].split('>', 1)[0].strip()
        except Exception:
            sender_email = _env_mail_sender
    else:
        sender_email = _env_mail_sender

if sender_email:
    MAIL_DEFAULT_SENDER = f"CYBER WORLD STORE <{sender_email}>"
else:
    MAIL_DEFAULT_SENDER = "CYBER WORLD STORE <no-reply@cyberworldstore.shop>"
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "cyberworldstore360@gmail.com")

db = SQLAlchemy(app)
# Flask-Migrate (Alembic) setup
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'user_login'  # type: ignore

CURRENCY = "GH\u20B5"  # GH₵

# Initialize database once before first request for Vercel serverless
@app.before_first_request
def init_db_on_first_request():
    """Initialize database on first request (serverless-friendly)."""
    if app.config.get('_db_initialized', False):
        return
    try:
        with app.app_context():
            db.create_all()
            # Ensure Settings table has all expected columns
            _ensure_settings_columns()
            # Ensure default admin user exists
            if not AdminUser.query.filter_by(username="Cyberjnr").first():
                try:
                    admin = AdminUser()
                    admin.username = "Cyberjnr"
                    admin.set_password("GITG360$")
                    db.session.add(admin)
                    db.session.commit()
                    app.logger.info("Created default admin user: Cyberjnr")
                except Exception as e:
                    try:
                        app.logger.exception("Failed to create default admin: %s", e)
                    except Exception:
                        print(f"[db init] Failed to create default admin: {e}")
            # Call optional init_db() if defined in this module
            init_fn = globals().get('init_db')
            if callable(init_fn):
                try:
                    init_fn()
                except Exception as e:
                    app.logger.warning("init_db() raised exception: %s", e)
            app.config['_db_initialized'] = True
    except Exception as e:
        try:
            app.logger.exception("Database initialization failed: %s", e)
        except Exception:
            print(f"[db error] Initialization failed: {e}")
        # Mark as attempted to avoid retry loops
        app.config['_db_initialized'] = True


def _ensure_settings_columns():
    """Add missing Settings columns to the database for backward compatibility."""
    try:
        with db.engine.connect() as conn:
            # Get all column names in settings table
            res = conn.exec_driver_sql("PRAGMA table_info(settings)")
            cols = [r[1] for r in res.fetchall()]
            
            # List of columns that should exist
            required_cols = [
                ('dashboard_layout', "VARCHAR(20) DEFAULT 'grid'"),
                ('seo_visible', "BOOLEAN DEFAULT 1"),
                ('seo_checklist_done', "BOOLEAN DEFAULT 0"),
                ('site_announcement', "TEXT DEFAULT ''"),
                # Image BLOB columns for persistent storage
                ('logo_image_data', 'BLOB'),
                ('banner1_image_data', 'BLOB'),
                ('banner2_image_data', 'BLOB'),
                ('bg_image_data', 'BLOB'),
                # MIME type columns
                ("logo_image_mime", "VARCHAR(100) DEFAULT 'image/svg+xml'"),
                ("banner1_image_mime", "VARCHAR(100) DEFAULT 'image/svg+xml'"),
                ("banner2_image_mime", "VARCHAR(100) DEFAULT 'image/svg+xml'"),
                ("bg_image_mime", "VARCHAR(100) DEFAULT 'image/svg+xml'"),
            ]
            
            # Add missing columns
            for col_name, col_def in required_cols:
                if col_name not in cols:
                    try:
                        conn.exec_driver_sql(f"ALTER TABLE settings ADD COLUMN {col_name} {col_def}")
                        print(f"Added missing column 'settings.{col_name}'")
                    except Exception as e:
                        print(f"Could not add column {col_name}: {e}")
    except Exception as e:
        print(f"Could not ensure Settings columns: {e}")



# Global error handler to catch unhandled exceptions and log full tracebacks
@app.errorhandler(500)
def handle_internal_server_error(e):
    import traceback
    tb = traceback.format_exc()
    try:
        app.logger.error("Unhandled exception: %s\n%s", e, tb)
    except Exception:
        print("[500 error]", e)
        print(tb)
    # Return a friendly error page while logging details
    # Persist last traceback to a temporary file (serverless writable path)
    try:
        last_err_path = '/tmp/last_error.txt'
        with open(last_err_path, 'w', encoding='utf-8') as fh:
            fh.write(f"Time: {utc_now().isoformat()}\n")
            fh.write(str(e) + "\n\n")
            fh.write(tb)
    except Exception:
        try:
            app.logger.exception('Failed to write last_error file')
        except Exception:
            pass

    try:
        return render_template('500.html', error=str(e)), 500
    except Exception:
        return ("Internal Server Error", 500)


# Secure endpoint to fetch the last saved traceback (protected by ERROR_VIEW_TOKEN env var)
@app.route('/__last_error')
def __last_error():
    token = request.args.get('token') or request.headers.get('X-ERROR-TOKEN')
    expected = os.environ.get('ERROR_VIEW_TOKEN')
    if not expected or token != expected:
        abort(403)
    last_err_path = '/tmp/last_error.txt'
    try:
        with open(last_err_path, 'r', encoding='utf-8') as fh:
            content = fh.read()
    except Exception:
        content = ''
    return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}


# Temporary secure admin reset endpoint (protected by ADMIN_RESET_TOKEN env var)
# Use only for emergency resets. Accepts GET or POST with 'username' and 'password' params.
@app.route('/__admin_reset', methods=['POST','GET'])
def __admin_reset():
    token = request.args.get('token') or request.form.get('token') or request.headers.get('X-ADMIN-RESET-TOKEN')
    expected = os.environ.get('ADMIN_RESET_TOKEN')
    if not expected or token != expected:
        abort(403)
    username = request.args.get('username') or request.form.get('username') or 'admin'
    password = request.args.get('password') or request.form.get('password') or 'GITG360'
    try:
        user = AdminUser.query.filter_by(username=username).first()
        if not user:
            user = AdminUser()
            user.username = username
            user.set_password(password)
            db.session.add(user)
        else:
            user.set_password(password)
        db.session.commit()
        return f"Admin user '{username}' set/updated successfully.", 200
    except Exception as e:
        try:
            app.logger.exception('Admin reset failed')
        except Exception:
            pass
        return str(e), 500

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    short = db.Column(db.String(500))
    price_ghc = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    old_price_ghc = db.Column(db.Numeric(10, 2))
    image = db.Column(db.String(300))
    featured = db.Column(db.Boolean, default=False)
    card_size = db.Column(db.String(20), default='medium')

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "short": self.short,
            "price_ghc": float(self.price_ghc),
            "old_price_ghc": float(self.old_price_ghc or 0),
            "image": self.image,
            "featured": self.featured,
        }

class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)
    @property
    def is_admin(self):
        """Explicit admin indicator for permission checks."""
        return True

class User(UserMixin, db.Model):
    """Customer user account for wallet and order history"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    wallet = db.relationship('Wallet', uselist=False, backref='user', cascade='all, delete-orphan')

    def __init__(self, email=None, **kwargs):
        super().__init__(**kwargs)
        self.email = email

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)
    @property
    def is_admin(self):
        """Non-admin customer user."""
        return False

class Wallet(db.Model):
    """User wallet for storing balance"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0.0, nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)


class Order(db.Model):
    """Store orders created by wallet or paystack payments"""
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    city = db.Column(db.String(100))
    subtotal = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    discount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    payment_method = db.Column(db.String(20), default='unknown')  # wallet, paystack, unknown
    payment_reference = db.Column(db.String(200), nullable=True)
    paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(255))
    qty = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(12,2), nullable=False, default=0)
    subtotal = db.Column(db.Numeric(12,2), nullable=False, default=0)
    product = db.relationship('Product', primaryjoin='Product.id==OrderItem.product_id', foreign_keys=[product_id], uselist=False)


class OrderLog(db.Model):
    """Simple audit trail for order status changes and events."""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    changed_by = db.Column(db.String(120))
    old_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20))
    note = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=utc_now)


class Slider(db.Model):
    """Product sliders for homepage"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    products = db.relationship('Product', secondary='slider_product', backref='sliders')
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

slider_product = db.Table('slider_product',
    db.Column('slider_id', db.Integer, db.ForeignKey('slider.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

class Coupon(db.Model):
    """Discount coupons for customers"""
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    discount_type = db.Column(db.String(20), default='percent')  # 'percent' or 'fixed'
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    max_uses = db.Column(db.Integer, default=None)  # None = unlimited
    current_uses = db.Column(db.Integer, default=0)
    min_amount = db.Column(db.Numeric(10, 2), default=0)  # Minimum order amount
    max_discount = db.Column(db.Numeric(10, 2), default=None)  # Max discount cap for percent
    expiry_date = db.Column(db.DateTime, default=None)  # None = no expiry
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)
    # note: `card_size` belongs to Product (card display size), not Coupon

    def is_valid(self):
        """Check if coupon is still valid"""
        if not self.is_active:
            return False, "Coupon is inactive"
        if self.max_uses and self.current_uses >= self.max_uses:
            return False, "Coupon usage limit reached"
        if self.expiry_date and utc_now() > self.expiry_date:
            return False, "Coupon has expired"
        return True, "Valid"
    
    def calculate_discount(self, amount):
        """Calculate discount amount"""
        amount = Decimal(str(amount))
        if self.discount_type == 'percent':
            discount = (amount * Decimal(str(self.discount_value))) / Decimal('100')
            if self.max_discount:
                discount = min(discount, Decimal(str(self.max_discount)))
        else:  # fixed
            discount = Decimal(str(self.discount_value))
        return min(discount, amount)

class Settings(db.Model):
    """Store site-wide settings like logo, banner, fonts, etc"""
    id = db.Column(db.Integer, primary_key=True)
    # Image paths (fallback for old uploads or external URLs)
    logo_image = db.Column(db.String(300), default='/static/images/logo.svg')
    banner1_image = db.Column(db.String(300), default='/static/images/ads1.svg')
    banner2_image = db.Column(db.String(300), default='/static/images/ads2.svg')
    bg_image = db.Column(db.String(300), default='/static/images/product-bg.svg')
    # Base64-encoded image data (for persistent storage on Vercel's ephemeral /tmp)
    logo_image_data = db.Column(db.LargeBinary, nullable=True)  # Base64 or binary
    banner1_image_data = db.Column(db.LargeBinary, nullable=True)
    banner2_image_data = db.Column(db.LargeBinary, nullable=True)
    bg_image_data = db.Column(db.LargeBinary, nullable=True)
    # MIME types for base64 images
    logo_image_mime = db.Column(db.String(20), default='image/svg+xml')
    banner1_image_mime = db.Column(db.String(20), default='image/svg+xml')
    banner2_image_mime = db.Column(db.String(20), default='image/svg+xml')
    bg_image_mime = db.Column(db.String(20), default='image/svg+xml')
    # Font and color settings
    primary_font = db.Column(db.String(100), default='Arial, sans-serif')
    secondary_font = db.Column(db.String(100), default='Verdana, sans-serif')
    primary_color = db.Column(db.String(7), default='#27ae60')
    secondary_color = db.Column(db.String(7), default='#2c3e50')
    dashboard_layout = db.Column(db.String(20), default='grid')  # 'grid' or 'list'
    seo_visible = db.Column(db.Boolean, default=True)  # Search engine visibility toggle
    seo_checklist_done = db.Column(db.Boolean, default=False)  # SEO checklist status
    site_announcement = db.Column(db.Text, default="")  # Editable announcement text
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    def get_logo_url(self):
        """Get logo URL: return /image/logo if data stored in DB, else return logo_image path"""
        if self.logo_image_data:
            return '/image/logo'
        return self.logo_image

    def get_banner1_url(self):
        """Get banner 1 URL: return /image/banner1 if data stored in DB, else return banner1_image path"""
        if self.banner1_image_data:
            return '/image/banner1'
        return self.banner1_image

    def get_banner2_url(self):
        """Get banner 2 URL: return /image/banner2 if data stored in DB, else return banner2_image path"""
        if self.banner2_image_data:
            return '/image/banner2'
        return self.banner2_image

    def get_bg_url(self):
        """Get background URL: return /image/bg if data stored in DB, else return bg_image path"""
        if self.bg_image_data:
            return '/image/bg'
        return self.bg_image


class FailedEmail(db.Model):
    """Store failed email sends for later retry."""
    id = db.Column(db.Integer, primary_key=True)
    to_address = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    attempts = db.Column(db.Integer, default=0)
    last_attempt_at = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.DateTime, default=utc_now)

@login_manager.user_loader
def load_user(user_id):
    """Load user from session - tries AdminUser first, then User (customer)"""
    try:
        user_id = int(user_id)
        # Try to load as AdminUser first
        admin = AdminUser.query.get(user_id)
        if admin:
            return admin
        # If not admin, try as customer User
        customer = User.query.get(user_id)
        if customer:
            return customer
    except Exception:
        pass
    return None


# Utilities
def allowed_file(fname):
    return "." in fname and fname.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_mime_type(filename):
    """Get MIME type from filename extension"""
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    mime_map = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp',
        'svg': 'image/svg+xml'
    }
    return mime_map.get(ext, 'image/jpeg')

def encode_image_to_base64(file_obj):
    """Read file object and encode to base64 bytes"""
    import base64
    file_obj.seek(0)
    file_content = file_obj.read()
    return base64.b64encode(file_content)

def decode_image_from_base64(b64_data, mime_type='image/jpeg'):
    """Create a data URL from base64 image data"""
    import base64
    if isinstance(b64_data, bytes):
        b64_str = b64_data.decode('utf-8')
    else:
        b64_str = b64_data
    return f"data:{mime_type};base64,{b64_str}"


def is_s3_configured():
    """Return True if AWS S3 env vars are present to enable S3 uploads."""
    return bool(os.environ.get('AWS_S3_BUCKET') and os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'))


def upload_to_s3(file_obj, key, mime_type=None):
    """Upload file-like object to S3 and return the public URL. Returns None on failure.

    Expects env vars: AWS_S3_BUCKET, AWS_REGION (optional). Uses boto3 if installed.
    """
    try:
        import boto3
        bucket = os.environ.get('AWS_S3_BUCKET')
        region = os.environ.get('AWS_REGION') or None
        # Build client using env creds
        s3 = boto3.client('s3',
                          aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                          region_name=region)
        # Prepare body
        file_obj.seek(0)
        body = file_obj.read()
        extra_args = {}
        if mime_type:
            extra_args['ContentType'] = mime_type
        # Use a reasonably unique key
        s3.put_object(Bucket=bucket, Key=key, Body=body, ACL='public-read', **extra_args)
        # Construct public URL (standard S3 URL)
        if region and region != 'us-east-1':
            url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
        else:
            url = f"https://{bucket}.s3.amazonaws.com/{key}"
        return url
    except Exception as e:
        try:
            app.logger.warning('S3 upload failed: %s', e)
        except Exception:
            pass
        return None

def get_settings():
    """Get site settings, create defaults if not exist"""
    try:
        settings = Settings.query.first()
    except Exception as e:
        # Database schema may be older (missing new Settings columns). Return
        # a transient Settings object with defaults so templates and login
        # pages can render without failing. This avoids forcing migrations
        # at runtime; admin can run `flask db upgrade` or `python -m` init scripts.
        try:
            app.logger.warning("Could not query Settings (db schema mismatch): %s", e)
        except Exception:
            pass
        return Settings()

    if not settings:
        settings = Settings()
        try:
            db.session.add(settings)
            db.session.commit()
        except Exception:
            # If commit fails (schema), swallow and return transient settings
            try:
                db.session.rollback()
            except Exception:
                pass
            return settings
    return settings

@app.template_filter("money")
def money_filter(value):
    try:
        return f"{CURRENCY}{float(value):.2f}"
    except Exception:
        return f"{CURRENCY}0.00"

@app.context_processor
def inject_now():
    settings = get_settings()
    return {"now": utc_now(), "PAYSTACK_PUBLIC": PAYSTACK_PUBLIC, "settings": settings}


def admin_required(f):
    """Decorator to enforce admin-only access. Checks is_admin property and redirects non-admins."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, 'is_admin', False):
            flash('Admin access required. Please login as admin.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def send_email(to_address: str, subject: str, body: str):
    """Send a simple plain-text email. This is best-effort and will raise on fatal SMTP errors."""
    # If SMTP not configured or password looks like a placeholder, just log to stdout (development)
    placeholder_passwords = ("", "your-app-password-here", "changeme", "password", "your-password")
    if (not MAIL_SERVER) or (not MAIL_USERNAME) or (not MAIL_PASSWORD) or (MAIL_PASSWORD.lower() in placeholder_passwords) or MAIL_PASSWORD.lower().startswith("your"):
        print(f"[email disabled] To: {to_address} Subject: {subject}\n{body}")
        return True

    # Build multipart message with plain text and simple HTML fallback
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = MAIL_DEFAULT_SENDER
    msg["To"] = to_address
    msg.set_content(body)
    # simple HTML alternative
    html_body = "<html><body>" + _json.dumps(body)[1:-1].replace('\\n', '<br>') + "</body></html>"
    try:
        msg.add_alternative(html_body, subtype="html")
    except Exception:
        pass

    # If SendGrid API configured, prefer it for reliability
    if SENDGRID_API_KEY:
        try:
            return _send_via_sendgrid(to_address, subject, body, html_body)
        except Exception:
            try:
                app.logger.exception("SendGrid send failed, falling back to SMTP")
            except Exception:
                print("[sendgrid error] falling back to SMTP")

    context = ssl.create_default_context()
    try:
        if MAIL_USE_SSL:
            with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, context=context) as server:
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
                if MAIL_USE_TLS:
                    server.starttls(context=context)
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
                server.send_message(msg)
        return True
    except Exception as e:
        # Log the exception for visibility and return False so callers can react
        try:
            app.logger.exception("Failed to send email to %s", to_address)
        except Exception:
            print(f"[email error] Failed to send to {to_address}: {e}")
        return False


def _send_via_sendgrid(to_address: str, subject: str, body: str, html_body = None) -> bool:
    """Send email using SendGrid V3 API. Returns True on accepted (202)."""
    if not SENDGRID_API_KEY:
        return False

    # Ensure we send a valid email-only address to SendGrid in the `from` field.
    from_name, from_addr = parseaddr(MAIL_DEFAULT_SENDER or '')
    if not from_addr:
        # fallback to configured username or admin email
        from_addr = MAIL_USERNAME or ADMIN_EMAIL or 'no-reply@cyberworldstore.shop'
        from_name = 'CYBER WORLD STORE'

    payload = {
        "personalizations": [{"to": [{"email": to_address}], "subject": subject}],
        "from": {"email": from_addr, "name": (from_name or 'CYBER WORLD STORE')},
        "content": [{"type": "text/plain", "value": body}],
    }
    if html_body:
        payload["content"].append({"type": "text/html", "value": html_body})

    headers = {"Authorization": f"Bearer {SENDGRID_API_KEY}", "Content-Type": "application/json"}
    try:
        r = requests.post("https://api.sendgrid.com/v3/mail/send", headers=headers, json=payload, timeout=15)
        if r.status_code in (200, 202):
            return True
        try:
            app.logger.warning("SendGrid returned status %s: %s", r.status_code, r.text)
        except Exception:
            print(f"[sendgrid warn] {r.status_code} {r.text}")
        return False
    except Exception as e:
        try:
            app.logger.exception("SendGrid send exception: %s", e)
        except Exception:
            print(f"[sendgrid error] {e}")
        return False


def is_valid_email(addr: str) -> bool:
    """Rudimentary validation for email addresses."""
    if not addr or not isinstance(addr, str):
        return False
    name, email = parseaddr(addr)
    return "@" in email and "." in email.split("@")[-1]


def enqueue_failed_email(to_address: str, subject: str, body: str):
    try:
        fe = FailedEmail(to_address=to_address, subject=subject, body=body)
        db.session.add(fe)
        db.session.commit()
        try:
            app.logger.info("Enqueued failed email to %s (id=%s)", to_address, fe.id)
        except Exception:
            print(f"[email queue] enqueued failed email to {to_address}")
    except Exception as e:
        try:
            app.logger.exception("Failed to enqueue failed email: %s", e)
        except Exception:
            print(f"[email queue error] {e}")


def send_email_async(to_address: str, subject: str, body: str):
    """Fire-and-forget email send. If send fails, persist to DB for retry."""
    # Basic validation
    if not is_valid_email(to_address):
        try:
            app.logger.warning("Invalid email address, skipping send: %s", to_address)
        except Exception:
            print(f"[email validation] Invalid email: {to_address}")
        return False

    # If RQ is configured, enqueue the send job there so it can be executed by workers
    if USE_RQ:
        try:
            _rq_queue.enqueue(send_email, to_address, subject, body)
            return True
        except Exception:
            try:
                app.logger.exception("RQ enqueue failed, falling back to thread")
            except Exception:
                print("[rq error] enqueue failed, using thread")

    def _worker():
        ok = send_email(to_address, subject, body)
        if not ok:
            enqueue_failed_email(to_address, subject, body)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return True


def send_html_email(to_address: str, subject: str, html_body: str, plain_text = None):
    """Send HTML email with optional plain text fallback. If plain_text is None, one is auto-generated."""
    if not is_valid_email(to_address):
        try:
            app.logger.warning("Invalid email address, skipping send: %s", to_address)
        except Exception:
            print(f"[email validation] Invalid email: {to_address}")
        return False

    # Use provided plain text or generate simple version by stripping HTML tags
    if not plain_text:
        import re
        plain_text = re.sub('<[^<]+?>', '', html_body)

    # If SMTP not configured or password looks like a placeholder, just log to stdout (development)
    placeholder_passwords = ("", "your-app-password-here", "changeme", "password", "your-password")
    if (not MAIL_SERVER) or (not MAIL_USERNAME) or (not MAIL_PASSWORD) or (MAIL_PASSWORD.lower() in placeholder_passwords) or MAIL_PASSWORD.lower().startswith("your"):
        print(f"[email disabled] To: {to_address} Subject: {subject}\n{plain_text}")
        try:
            app.logger.info("[email disabled] Would send to: %s (MAIL_SERVER=%s, MAIL_USERNAME=%s, has_password=%s)", 
                          to_address, bool(MAIL_SERVER), bool(MAIL_USERNAME), bool(MAIL_PASSWORD))
        except Exception:
            pass
        return True

    # Build multipart HTML email message
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = MAIL_DEFAULT_SENDER
    msg["To"] = to_address
    msg.set_content(plain_text)
    msg.add_alternative(html_body, subtype="html")

    # If SendGrid API configured, prefer it for reliability
    if SENDGRID_API_KEY:
        try:
            return _send_via_sendgrid(to_address, subject, plain_text, html_body)
        except Exception:
            try:
                app.logger.exception("SendGrid send failed, falling back to SMTP")
            except Exception:
                print("[sendgrid error] falling back to SMTP")

    context = ssl.create_default_context()
    try:
        if MAIL_USE_SSL:
            with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, context=context) as server:
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
                if MAIL_USE_TLS:
                    server.starttls(context=context)
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
                server.send_message(msg)
        return True
    except Exception as e:
        try:
            app.logger.exception("Failed to send HTML email to %s", to_address)
        except Exception:
            print(f"[email error] Failed to send HTML email to {to_address}: {e}")
        return False


def send_html_email_async(to_address: str, subject: str, html_body: str, plain_text = None):
    """Fire-and-forget HTML email send. If send fails, persist to DB for retry."""
    if not is_valid_email(to_address):
        try:
            app.logger.warning("Invalid email address, skipping send: %s", to_address)
        except Exception:
            print(f"[email validation] Invalid email: {to_address}")
        return False

    # If RQ is configured, enqueue the send job there
    if USE_RQ:
        try:
            _rq_queue.enqueue(send_html_email, to_address, subject, html_body, plain_text)
            return True
        except Exception:
            try:
                app.logger.exception("RQ enqueue failed, falling back to thread")
            except Exception:
                print("[rq error] enqueue failed, using thread")

    def _worker():
        ok = send_html_email(to_address, subject, html_body, plain_text)
        if not ok:
            # Store for retry - use plain text body for database retry
            enqueue_failed_email(to_address, subject, plain_text or html_body)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return True


def build_order_items_html(items: list, base_url: str = "http://127.0.0.1:5000") -> str:
    """Build HTML table for order items with product images."""
    html = '<table style="width:100%; border-collapse:collapse; margin:20px 0;">'
    html += '<thead><tr style="background-color:#f5f5f5; border-bottom:2px solid #ccc;">'
    html += '<th style="padding:12px; text-align:left; font-weight:bold;">Product</th>'
    html += '<th style="padding:12px; text-align:center; font-weight:bold;">Qty</th>'
    html += '<th style="padding:12px; text-align:right; font-weight:bold;">Price</th>'
    html += '<th style="padding:12px; text-align:right; font-weight:bold;">Subtotal</th>'
    html += '</tr></thead><tbody>'
    
    for item in items:
        product_name = item.get('product', 'Unknown Product')
        qty = item.get('qty', 1)
        price = item.get('price', 0)
        subtotal = item.get('subtotal', 0)
        image_path = item.get('image_path', '')
        
        # Build image HTML if image path exists
        img_html = ''
        if image_path:
            # Try to resolve image path to absolute URL
            if image_path.startswith('http'):
                img_url = image_path
            else:
                # Remove leading slashes and build URL
                clean_path = image_path.lstrip('/')
                img_url = f"{base_url.rstrip('/')}/{clean_path}"
            img_html = f'<img src="{img_url}" alt="{product_name}" style="max-width:60px; height:auto; border-radius:4px; margin-right:8px; vertical-align:middle;">'
        
        html += '<tr style="border-bottom:1px solid #eee;">'
        html += f'<td style="padding:12px;">{img_html} {product_name}</td>'
        html += f'<td style="padding:12px; text-align:center;">{qty}</td>'
        html += f'<td style="padding:12px; text-align:right;">GH₵{price:.2f}</td>'
        html += f'<td style="padding:12px; text-align:right;"><strong>GH₵{subtotal:.2f}</strong></td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    return html


def build_order_summary_html(order_ref: str, customer_name: str, customer_email: str, 
                             customer_phone: str, customer_city: str, subtotal: Decimal,
                             discount: Decimal, total: Decimal, payment_method: str = "wallet") -> str:
    """Build HTML summary section for order emails."""
    html = '<div style="background-color:#f9f9f9; padding:20px; border-radius:4px; margin:20px 0;">'
    
    # Customer details
    html += '<h3 style="color:#333; margin-top:0; margin-bottom:15px; font-size:18px;">📋 Customer Details</h3>'
    html += '<p style="margin:5px 0; line-height:1.8;">'
    html += f'<strong>Name:</strong> {customer_name or "N/A"}<br>'
    html += f'<strong>Email:</strong> {customer_email or "N/A"}<br>'
    html += f'<strong>Phone:</strong> {customer_phone or "N/A"}<br>'
    html += f'<strong>City:</strong> {customer_city or "N/A"}<br>'
    html += f'<strong>Order Ref:</strong> <span style="font-family:monospace; color:#0066cc;">{order_ref}</span>'
    html += '</p>'
    
    # Payment summary
    html += '<h3 style="color:#333; margin-top:20px; margin-bottom:15px; font-size:18px;">💳 Payment Summary</h3>'
    html += '<p style="margin:5px 0; line-height:1.8;">'
    html += f'Subtotal: <span style="float:right;"><strong>GH₵{subtotal:.2f}</strong></span><br>'
    if discount and discount > 0:
        html += f'Discount Applied: <span style="float:right; color:#d9534f;"><strong>-GH₵{discount:.2f}</strong></span><br>'
    html += f'<div style="border-top:2px solid #ddd; padding-top:10px; margin-top:10px;">'
    html += f'Amount Charged: <span style="float:right; color:#5cb85c;"><strong style="font-size:18px;">GH₵{total:.2f}</strong></span>'
    html += f'</div>'
    html += f'Payment Method: <span style="float:right;"><strong>{payment_method.title()}</strong></span><br>'
    html += '</p>'
    
    html += '</div>'
    return html


def build_email_header_html(title: str = "Order Confirmation") -> str:
    """Build professional HTML email header with Cyber World Store branding."""
    html = '''
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding:30px; text-align:center; color:white; border-radius:4px 4px 0 0;">
        <div style="font-size:24px; font-weight:bold; margin-bottom:5px;">🛍️ CYBER WORLD STORE</div>
        <div style="font-size:14px; opacity:0.9;">Your trusted online marketplace</div>
        <div style="margin-top:15px; font-size:20px; font-weight:bold; color:#fff;">✨ ''' + title + ''' ✨</div>
    </div>
    '''
    return html


def build_email_footer_html() -> str:
    """Build professional HTML email footer."""
    html = '''
    <div style="background-color:#f5f5f5; padding:20px; text-align:center; font-size:12px; color:#666; border-top:1px solid #ddd; margin-top:20px;">
        <p style="margin:5px 0;">
            <strong>Cyber World Store</strong><br>
            📧 <a href="mailto:cyberworldstore360@gmail.com" style="color:#0066cc; text-decoration:none;">cyberworldstore360@gmail.com</a><br>
            Need help? <a href="#" style="color:#0066cc; text-decoration:none;">Contact Support</a>
        </p>
        <p style="margin:10px 0; opacity:0.7;">
            Thank you for shopping with us! Follow us on social media for latest updates.
        </p>
    </div>
    '''
    return html


def _retry_failed_emails_loop(interval: int = 60, max_attempts: int = 5):
    """Background loop that retries failed emails from the DB."""
    while True:
        try:
            with app.app_context():
                pending = FailedEmail.query.filter(FailedEmail.attempts < max_attempts).all()
                for fe in pending:
                    try:
                        ok = send_email(fe.to_address, fe.subject, fe.body)
                        if ok:
                            db.session.delete(fe)
                            db.session.commit()
                            try:
                                app.logger.info("Retried and sent failed email id=%s to %s", fe.id, fe.to_address)
                            except Exception:
                                print(f"[email retry] sent id={fe.id} to {fe.to_address}")
                        else:
                            fe.attempts = (fe.attempts or 0) + 1
                            fe.last_attempt_at = utc_now()
                            db.session.commit()
                    except Exception:
                        db.session.rollback()
                        try:
                            app.logger.exception("Error retrying failed email id=%s", fe.id)
                        except Exception:
                            print(f"[email retry error] id={fe.id}")
        except Exception:
            try:
                app.logger.exception("Error in email retry loop")
            except Exception:
                print("[email retry loop error]")
        time.sleep(interval)

# Initialize DB helper (for CLI)
@app.cli.command("initdb")
def initdb_command():
    # Create tables if they don't exist
    db.create_all()
    # Ensure Settings table has all expected columns
    _ensure_settings_columns()
    # If the database was created before `card_size` existed on Product, try to add the column.
    try:
        # Inspect product table columns (works for SQLite)
        has_card_size = False
        try:
            # Use a connection and exec_driver_sql for compatibility with SQLAlchemy 1.4+
            with db.engine.connect() as conn:
                res = conn.exec_driver_sql("PRAGMA table_info(product)")
                cols = [r[1] for r in res.fetchall()]
                has_card_size = 'card_size' in cols
        except Exception:
            has_card_size = False

        if not has_card_size:
            try:
                with db.engine.connect() as conn:
                    # Use exec_driver_sql to run raw DDL on the underlying DB connection (compatible with SQLAlchemy 1.4+)
                    conn.exec_driver_sql("ALTER TABLE product ADD COLUMN card_size VARCHAR(20) DEFAULT 'medium'")
                print('Added missing `card_size` column to product table')
            except Exception:
                print('Could not add card_size column automatically; please run migrations')
    except Exception:
        # If inspection fails, continue and let subsequent operations handle errors
        pass
    # create default admin
    if not AdminUser.query.filter_by(username="Cyberjnr").first():
        admin = AdminUser()
        admin.username = "Cyberjnr"
        admin.set_password("GITG360$")
        db.session.add(admin)
    # add sample products if none — use raw SQL count to avoid ORM column mapping errors on older schemas
    try:
        cnt = 0
        try:
            res = db.session.execute("SELECT COUNT(*) FROM product")
            cnt = int(res.scalar() or 0)
        except Exception:
            cnt = 0

        if cnt == 0:
            sample = [
                {"title":"Sample Soundbar", "short":"High quality sound bar", "price_ghc":1190.45, "old_price_ghc":1434.00, "image":"/static/images/placeholder.png", "featured":True},
                {"title":"Wireless Modem 4G/5G", "short":"High speed wireless modem", "price_ghc":700.00, "old_price_ghc":780.00, "image":"/static/images/placeholder.png", "featured":True},
            ]
            for s in sample:
                try:
                    p = Product(title=s["title"], short=s["short"], price_ghc=s["price_ghc"], old_price_ghc=s["old_price_ghc"], image=s["image"], featured=s["featured"])
                    db.session.add(p)
                except Exception:
                    # If the ORM insert fails because the DB schema lacks `card_size`, fall back to raw INSERT excluding that column
                    try:
                        db.session.execute(
                            "INSERT INTO product (title, short, price_ghc, old_price_ghc, image, featured) VALUES (:title, :short, :price_ghc, :old_price_ghc, :image, :featured)",
                            dict(title=s["title"], short=s["short"], price_ghc=s["price_ghc"], old_price_ghc=s["old_price_ghc"], image=s["image"], featured=1 if s["featured"] else 0)
                        )
                    except Exception:
                        pass
    except Exception:
        pass

    db.session.commit()
    print("DB initialized and sample data added (if applicable).")


# --- Public pages ---
@app.route("/")
def index():
    prods = Product.query.order_by(Product.id.desc()).all()
    featured = Product.query.filter_by(featured=True).all()
    return render_template("index.html", products=prods, featured=featured)

@app.route("/product/<int:pid>")
def product_detail(pid):
    p = Product.query.get_or_404(pid)
    return render_template("product.html", product=p)

@app.route("/api/products")
def api_products():
    return jsonify([p.to_dict() for p in Product.query.all()])

# --- Cart (session-based) ---
def _cart():
    return session.setdefault("cart", {})

@app.route("/cart")
def view_cart():
    cart = _cart()
    items = []
    total = Decimal("0")
    for pid_str, qty in cart.items():
        try:
            pid = int(pid_str); qty = int(qty)
        except Exception:
            continue
        p = Product.query.get(pid)
        if not p:
            continue
        subtotal = Decimal(p.price_ghc) * qty
        items.append({"product": p, "qty": qty, "subtotal": subtotal})
        total += subtotal
    return render_template("cart.html", items=items, total=total)

@app.route("/cart/add/<int:pid>", methods=["POST"])
def cart_add(pid):
    try:
        qty = int(request.form.get("qty", 1))
    except Exception:
        qty = 1
    if qty < 1:
        qty = 1
    p = Product.query.get_or_404(pid)
    cart = _cart()
    cart[str(pid)] = cart.get(str(pid), 0) + qty
    session.modified = True
    flash(f"Added {qty} × {p.title} to cart.", "success")
    return redirect(request.referrer or url_for("index"))

@app.route("/cart/update", methods=["POST"])
def cart_update():
    cart = _cart()
    for key, val in request.form.items():
        if not key.startswith("qty_"): continue
        pid = key.split("_", 1)[1]
        try:
            qty = int(val)
        except Exception:
            continue
        if qty <= 0:
            cart.pop(pid, None)
        else:
            cart[pid] = qty
    session.modified = True
    flash("Cart updated.", "info")
    return redirect(url_for("view_cart"))

@app.route("/cart/clear")
def cart_clear():
    session.pop("cart", None)
    flash("Cart cleared.", "info")
    return redirect(url_for("index"))

# --- Paystack integration ---
@app.route("/pay/paystack", methods=["POST"])
def paystack_init():
    cart = _cart()
    if not cart:
        flash("Cart is empty.", "warning")
        return redirect(url_for("index"))

    total = Decimal("0")
    items = []
    for pid_str, qty in cart.items():
        pid = int(pid_str); qty = int(qty)
        p = Product.query.get(pid)
        if not p: continue
        subtotal = Decimal(p.price_ghc) * qty
        total += subtotal
        items.append({"product": p.title, "product_id": p.id, "qty": qty, "subtotal": float(subtotal)})

    email = request.form.get("email") or "customer@example.com"
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    city = request.form.get("city", "").strip()
    coupon_id = request.form.get("coupon_id", "").strip()
    
    # Calculate discount if coupon applied (validate properly)
    discount = Decimal('0')
    applied_coupon = None
    if coupon_id:
        try:
            coupon = Coupon.query.get(int(coupon_id))
            if coupon:
                valid, msg = coupon.is_valid()
                if valid:
                    if total >= Decimal(str(coupon.min_amount)):
                        discount = coupon.calculate_discount(total)
                        applied_coupon = coupon
                    else:
                        flash(f"Coupon requires minimum order of GH₵{coupon.min_amount}", "warning")
                        return redirect(url_for('checkout'))
                else:
                    flash(f"Coupon invalid: {msg}", "warning")
                    return redirect(url_for('checkout'))
        except Exception:
            pass

    final_total = max(total - discount, Decimal('0'))
    
    # For demo convert GHS to minor units by *100 (NOT real NGN conversion). Adjust in production.
    amount_minor = int(float(final_total) * 100)

    initialize_url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}", "Content-Type": "application/json"}
    reference = str(uuid.uuid4())
    payload = {
        "email": email,
        "amount": amount_minor,
        "reference": reference,
        "callback_url": PAYSTACK_CALLBACK,
        "metadata": {
            "cart": items,
            "name": name,
            "phone": phone,
            "city": city,
            "discount_amount": str(discount),
            "coupon_applied": coupon_id if coupon_id else "none"
        }
    }

    if not PAYSTACK_SECRET:
        flash("Paystack secret key not configured. Set PAYSTACK_SECRET_KEY in .env.", "danger")
        return redirect(url_for("checkout"))

    try:
        r = requests.post(initialize_url, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        if data.get("status") and data.get("data") and data["data"].get("authorization_url"):
            # store pending payment info (email and items) to verify after redirect
            session["pending_payment"] = {"reference": reference, "amount": amount_minor, "email": email, "items": items, "coupon_id": int(coupon_id) if coupon_id else None, "discount": str(discount)}
            return redirect(data["data"]["authorization_url"])
        else:
            flash("Failed to initialize Paystack payment: " + str(data.get("message", "unknown")), "danger")
            return redirect(url_for("checkout"))
    except Exception as e:
        flash("Paystack initialization error: " + str(e), "danger")
        return redirect(url_for("checkout"))

@app.route("/pay/wallet", methods=["POST"])
def wallet_payment():
    """Pay with wallet balance"""
    if not current_user.is_authenticated or not hasattr(current_user, 'email'):
        flash("Please login first.", "warning")
        return redirect(url_for("user_login"))
    
    cart = _cart()
    if not cart:
        flash("Cart is empty.", "warning")
        return redirect(url_for("index"))

    total = Decimal("0")
    items = []
    for pid_str, qty in cart.items():
        pid = int(pid_str); qty = int(qty)
        p = Product.query.get(pid)
        if not p: continue
        subtotal = Decimal(p.price_ghc) * qty
        total += subtotal
        items.append({"product": p.title, "product_id": p.id, "qty": qty, "subtotal": float(subtotal)})

    # Get wallet balance
    if not current_user.wallet:
        flash("Wallet not found.", "danger")
        return redirect(url_for("checkout"))
    
    # Extract shipping and coupon info
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    city = request.form.get("city", "").strip()
    coupon_id = request.form.get("coupon_id", "").strip()
    email = request.form.get("email") or current_user.email
    
    # Calculate discount if coupon applied (validate coupon properly)
    discount = Decimal('0')
    applied_coupon = None
    if coupon_id:
        try:
            coupon = Coupon.query.get(int(coupon_id))
            if coupon:
                valid, msg = coupon.is_valid()
                if valid:
                    if total >= Decimal(str(coupon.min_amount)):
                        discount = coupon.calculate_discount(total)
                        applied_coupon = coupon
                    else:
                        flash(f"Coupon requires minimum order of GH₵{coupon.min_amount}", "warning")
                        return redirect(url_for('checkout'))
                else:
                    flash(f"Coupon invalid: {msg}", "warning")
                    return redirect(url_for('checkout'))
        except Exception:
            pass
    
    final_total = max(total - discount, Decimal('0'))
    wallet_balance = Decimal(current_user.wallet.balance)
    
    # Check if wallet has enough after discount
    if wallet_balance < final_total:
        # Not enough wallet balance - redirect to Paystack as fallback
        flash(f"Wallet balance (GH₵{wallet_balance:.2f}) insufficient for discounted total (GH₵{final_total:.2f}). Redirecting to Paystack...", "info")
        # Redirect to Paystack payment with coupon_id preserved
        return redirect(url_for("paystack_init"))
    
    # Wallet balance is sufficient - proceed with payment
    try:
        # Deduct wallet balance
        current_user.wallet.balance = wallet_balance - final_total

        # Ensure we have the user's email and a single reference
        user_email = current_user.email
        reference = str(uuid.uuid4())

        # Create order record
        order = Order(
            reference=reference,
            user_id=current_user.id,
            email=user_email,
            name=name,
            phone=phone,
            city=city,
            subtotal=total,
            discount=discount,
            total=final_total,
            status='pending',
            payment_method='wallet',
            payment_reference=reference,
            paid=True
        )
        db.session.add(order)
        db.session.flush()
        for it in items:
            oi = OrderItem(
                order_id=order.id,
                product_id=it.get('product_id') if it.get('product_id') else None,
                title=it.get('product'),
                qty=int(it.get('qty') or 1),
                price=Decimal(str(it.get('subtotal'))) / max(1, int(it.get('qty') or 1)),
                subtotal=Decimal(str(it.get('subtotal')))
            )
            db.session.add(oi)

        # Increment coupon usage if applied
        if applied_coupon:
            try:
                applied_coupon.current_uses = (applied_coupon.current_uses or 0) + 1
            except Exception:
                pass

        # Log order creation
        try:
            changed_by = getattr(current_user, 'username', None) or getattr(current_user, 'email', 'system')
            log = OrderLog(order_id=order.id, changed_by=changed_by, old_status=None, new_status=order.status, note='Order created via wallet')
            db.session.add(log)
        except Exception:
            pass

        db.session.commit()

        # Send to customer (validate email first)
        if is_valid_email(user_email):
            try:
                subject_cust = f"[Cyber World Store] Order confirmation — wallet payment {reference[:8]}"
                
                # Build items list with product images for email
                items_with_images = []
                for it in items:
                    item_dict = dict(it)
                    # Get product to fetch image_path
                    if it.get('product_id'):
                        p = Product.query.get(it.get('product_id'))
                        if p:
                            item_dict['image_path'] = p.image if p.image else ''
                    items_with_images.append(item_dict)
                
                # Build HTML email
                html_cust = '<html><body style="font-family:Arial,sans-serif; line-height:1.6; color:#333;">'
                html_cust += build_email_header_html("Order Confirmation")
                html_cust += '<div style="max-width:600px; margin:0 auto; padding:20px;">'
                html_cust += f'<p>Thank you <strong>{name or "Valued Customer"}</strong>! Your order has been received and payment confirmed via wallet. ✅</p>'
                html_cust += build_order_items_html(items_with_images)
                html_cust += build_order_summary_html(reference, name, user_email, phone, city, total, discount, final_total, "wallet")
                html_cust += '<div style="background-color:#e8f5e9; padding:15px; border-left:4px solid #4caf50; margin:20px 0; border-radius:4px;">'
                html_cust += f'<p style="margin:0;"><strong>💼 Wallet Balance Update</strong><br>'
                html_cust += f'Remaining Balance: <strong style="color:#4caf50;">GH₵{Decimal(current_user.wallet.balance):.2f}</strong></p>'
                html_cust += '</div>'
                html_cust += '<div style="background-color:#e3f2fd; padding:15px; border-left:4px solid #2196f3; margin:20px 0; border-radius:4px;">'
                html_cust += '<p style="margin:0;"><strong>📦 What\'s Next?</strong><br>'
                html_cust += 'We will process and ship your order shortly. You can track your order status in your account dashboard.</p>'
                html_cust += '</div>'
                html_cust += build_email_footer_html()
                html_cust += '</div></body></html>'
                
                plain_text = f"Order Confirmation Receipt\n\nThank you for your order using wallet payment!\n\nOrder Reference: {reference}\nStatus: Pending (Processing)\n\nItems:\n"
                for it in items:
                    plain_text += f"  • {it.get('product')} x{it.get('qty')} — GH₵{it.get('subtotal'):.2f}\n"
                plain_text += f"\nSubtotal: GH₵{total:.2f}\n"
                if discount > 0:
                    plain_text += f"Discount: -GH₵{discount:.2f}\n"
                plain_text += f"Amount Charged: GH₵{final_total:.2f}\nPayment Method: Wallet\n"
                plain_text += f"Wallet Balance After: GH₵{Decimal(current_user.wallet.balance):.2f}\n"
                plain_text += "\nWe will process and ship your order shortly.\nTrack your order in your account dashboard.\nQuestions? Contact: cyberworldstore360@gmail.com"
                
                ok = send_html_email_async(user_email, subject_cust, html_cust, plain_text)
            except Exception as e:
                try:
                    app.logger.exception("Failed to build/send wallet customer email: %s", e)
                except Exception:
                    print(f"[email error] Failed to build/send wallet customer email: {e}")
        else:
            try:
                app.logger.warning("Wallet payment: skipped customer email (invalid address: %s)", user_email)
            except Exception:
                print(f"[wallet] Skipped customer email (invalid: {user_email})")

        # Send to admin
        try:
            subject_admin = f"[Cyber World Store] New wallet order received — {reference[:8]}"
            
            # Build admin email with items and images
            items_with_images = []
            for it in items:
                item_dict = dict(it)
                if it.get('product_id'):
                    p = Product.query.get(it.get('product_id'))
                    if p:
                        item_dict['image_path'] = p.image if p.image else ''
                items_with_images.append(item_dict)
            
            html_admin = '<html><body style="font-family:Arial,sans-serif; line-height:1.6; color:#333;">'
            html_admin += build_email_header_html("New Wallet Order Received")
            html_admin += '<div style="max-width:600px; margin:0 auto; padding:20px;">'
            html_admin += '<p style="font-size:16px;"><strong>⚠️ New wallet payment order received and awaiting processing.</strong></p>'
            html_admin += build_order_items_html(items_with_images)
            html_admin += build_order_summary_html(reference, name, user_email, phone, city, total, discount, final_total, "wallet")
            html_admin += '<div style="background-color:#fff3cd; padding:15px; border-left:4px solid #ff9800; margin:20px 0; border-radius:4px;">'
            html_admin += '<p style="margin:0;"><strong>✋ Action Required</strong><br>'
            html_admin += '1. ✔️ Verify order details in admin dashboard<br>'
            html_admin += '2. 📦 Prepare items for shipment<br>'
            html_admin += '3. 🚚 Update order status to "Completed" when shipped<br>'
            html_admin += '4. 📧 Customer will receive shipment notification</p>'
            html_admin += '</div>'
            html_admin += f'<p><strong>Access order:</strong> <a href="#" style="color:#0066cc; text-decoration:none;">/admin/orders/{reference}</a></p>'
            html_admin += build_email_footer_html()
            html_admin += '</div></body></html>'
            
            plain_text = f"New Wallet Order Notification\n\nOrder Reference: {reference}\nCustomer: {user_email}\nName: {name}\nPhone: {phone}\nCity: {city}\n\nItems:\n"
            for it in items:
                plain_text += f"  • {it.get('product')} x{it.get('qty')} — GH₵{it.get('subtotal'):.2f}\n"
            plain_text += f"\nSubtotal: GH₵{total:.2f}\n"
            if discount > 0:
                plain_text += f"Discount: -GH₵{discount:.2f}\n"
            plain_text += f"Amount Charged: GH₵{final_total:.2f}\nPayment Status: Completed\n\nNext Steps:\n1. Verify order details\n2. Prepare items\n3. Update status\n4. Customer notification sent"
            
            ok2 = send_html_email_async(ADMIN_EMAIL, subject_admin, html_admin, plain_text)
        except Exception as e:
            try:
                app.logger.exception("Failed to build/send wallet admin email: %s", e)
            except Exception:
                print(f"[email error] Failed to build/send wallet admin email: {e}")

        try:
            app.logger.info("Wallet payment successful: ref=%s customer=%s amount=%.2f", reference, user_email, final_total)
        except Exception:
            print(f"[wallet] Order: ref={reference} customer={user_email} amount={final_total}")
        
        session.pop("cart", None)
        flash("Payment successful via wallet. Thank you!", "success")
        return redirect(url_for("checkout_success"))
    except Exception as e:
        db.session.rollback()
        try:
            app.logger.exception("Wallet payment failed: %s", e)
        except Exception:
            print(f"[wallet error] {e}")
        flash(f"Wallet payment error: {str(e)}", "danger")
        return redirect(url_for("checkout"))

@app.route("/paystack/callback")
def paystack_callback():
    ref = request.args.get("reference") or (session.get("pending_payment") or {}).get("reference")
    if not ref:
        flash("No reference found for payment verification.", "danger")
        return redirect(url_for("index"))

    verify_url = f"https://api.paystack.co/transaction/verify/{ref}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}"}
    try:
        r = requests.get(verify_url, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        if data.get("status") and data.get("data") and data["data"].get("status") == "success":
            # Get pending payment details saved earlier
            pending = session.get("pending_payment") or {}
            user_email = pending.get("email") or (data.get("data") or {}).get("customer", {}).get("email") or ""
            amount_minor = pending.get("amount") or data["data"].get("amount")
            amount_display = f"{(int(amount_minor) / 100):.2f}"
            items = pending.get("items") or []

            # Validate customer email before sending
            if is_valid_email(user_email):
                try:
                    # Email to customer
                    subject_cust = f"[Cyber World Store] Order confirmation — Paystack payment {ref[:8]}"
                    
                    # Build items with images for email
                    items_with_images = []
                    for it in items:
                        item_dict = dict(it)
                        if it.get('product_id'):
                            p = Product.query.get(it.get('product_id'))
                            if p:
                                item_dict['image_path'] = p.image if p.image else ''
                        items_with_images.append(item_dict)
                    
                    # Build HTML email
                    html_cust = '<html><body style="font-family:Arial,sans-serif; line-height:1.6; color:#333;">'
                    html_cust += build_email_header_html("Order Confirmation - Payment Verified")
                    html_cust += '<div style="max-width:600px; margin:0 auto; padding:20px;">'
                    html_cust += f'<p><strong>✅ Payment Received!</strong> Thank you for your order via Paystack. Your payment has been verified and your order is now being processed.</p>'
                    html_cust += f'<div style="background-color:#fff; padding:15px; border:2px solid #0066cc; border-radius:4px; margin:15px 0; font-family:monospace; text-align:center;">'
                    html_cust += f'<div style="font-size:12px; color:#666;">ORDER REFERENCE</div>'
                    html_cust += f'<div style="font-size:18px; font-weight:bold; color:#0066cc;">{ref}</div>'
                    html_cust += '</div>'
                    html_cust += build_order_items_html(items_with_images)
                    html_cust += '<div style="background-color:#f5f5f5; padding:15px; border-radius:4px; margin:20px 0;">'
                    html_cust += f'<strong>💳 Amount Paid:</strong> <span style="float:right; color:#2196f3; font-size:18px;"><strong>GH₵{amount_display}</strong></span><br><br>'
                    html_cust += f'<strong>🔒 Payment Status:</strong> <span style="color:#4caf50;"><strong>Verified ✓</strong></span>'
                    html_cust += '</div>'
                    html_cust += '<div style="background-color:#e8f5e9; padding:15px; border-left:4px solid #4caf50; margin:20px 0; border-radius:4px;">'
                    html_cust += '<p style="margin:0;"><strong>📦 What\'s Next?</strong><br>'
                    html_cust += 'We are now processing your order and will notify you when it\'s shipped. You can track your order status in your account dashboard.</p>'
                    html_cust += '</div>'
                    html_cust += build_email_footer_html()
                    html_cust += '</div></body></html>'
                    
                    plain_text = f"Order Confirmation Receipt\n\nThank you for your Paystack payment!\n\nOrder Reference: {ref}\nStatus: Payment Verified ✓\nAmount Paid: GH₵{amount_display}\n\nItems:\n"
                    for it in items:
                        plain_text += f"  • {it.get('product')} x{it.get('qty')} — GH₵{it.get('subtotal'):.2f}\n"
                    plain_text += f"\nYour order is being processed and will be shipped shortly.\nTrack your order: Dashboard\nQuestions? Contact: cyberworldstore360@gmail.com"
                    
                    ok = send_html_email_async(user_email, subject_cust, html_cust, plain_text)
                except Exception as e:
                    try:
                        app.logger.exception("Failed to build/send paystack customer email: %s", e)
                    except Exception:
                        print(f"[email error] Failed to build/send paystack customer email: {e}")
            else:
                try:
                    app.logger.warning("Paystack callback: skipped customer email (invalid address: %s)", user_email)
                except Exception:
                    print(f"[paystack] Skipped customer email (invalid: {user_email})")

            # Always send admin notification
            try:
                # Email to admin
                subject_admin = f"[Cyber World Store] New Paystack order received — {ref[:8]}"
                
                # Build items with images
                items_with_images = []
                for it in items:
                    item_dict = dict(it)
                    if it.get('product_id'):
                        p = Product.query.get(it.get('product_id'))
                        if p:
                            item_dict['image_path'] = p.image if p.image else ''
                    items_with_images.append(item_dict)
                
                html_admin = '<html><body style="font-family:Arial,sans-serif; line-height:1.6; color:#333;">'
                html_admin += build_email_header_html("New Paystack Order Received")
                html_admin += '<div style="max-width:600px; margin:0 auto; padding:20px;">'
                html_admin += '<p style="font-size:16px;"><strong>🎉 New Paystack payment order received and verified!</strong></p>'
                html_admin += f'<div style="background-color:#e3f2fd; padding:12px; border-radius:4px; margin:15px 0;">'
                html_admin += f'<strong>Customer:</strong> {user_email}<br>'
                html_admin += f'<strong>Amount:</strong> <span style="color:#0066cc; font-size:16px;"><strong>GH₵{amount_display}</strong></span>'
                html_admin += '</div>'
                html_admin += build_order_items_html(items_with_images)
                html_admin += '<div style="background-color:#fff3cd; padding:15px; border-left:4px solid #ff9800; margin:20px 0; border-radius:4px;">'
                html_admin += '<p style="margin:0;"><strong>⚡ Action Required</strong><br>'
                html_admin += '✅ Payment Status: <strong style="color:#4caf50;">Verified</strong><br>'
                html_admin += '1. 🔍 Verify order details in admin dashboard<br>'
                html_admin += '2. 📦 Prepare items for shipment<br>'
                html_admin += '3. 🚚 Update order status to "Completed" when shipped<br>'
                html_admin += '4. 📧 Customer will receive shipment notification</p>'
                html_admin += '</div>'
                html_admin += f'<p><strong>Quick Access:</strong> <a href="#" style="color:#0066cc; text-decoration:none;">/admin/orders/{ref}</a></p>'
                html_admin += build_email_footer_html()
                html_admin += '</div></body></html>'
                
                plain_text = f"New Paystack Order Notification\n\nPayment Verified!\nOrder Reference: {ref}\nCustomer: {user_email}\nAmount: GH₵{amount_display}\n\nItems:\n"
                for it in items:
                    plain_text += f"  • {it.get('product')} x{it.get('qty')} — GH₵{it.get('subtotal'):.2f}\n"
                plain_text += f"\nPayment Status: Verified & Completed\n\nNext Steps:\n1. Verify order\n2. Prepare items\n3. Update status\n4. Customer notification"
                
                ok2 = send_html_email_async(ADMIN_EMAIL, subject_admin, html_admin, plain_text)
            except Exception as e:
                try:
                    app.logger.exception("Failed to build/send paystack admin email: %s", e)
                except Exception:
                    print(f"[email error] Failed to build/send paystack admin email: {e}")

            # Log successful payment
            try:
                app.logger.info("Paystack payment successful: ref=%s customer=%s amount=%s", ref, user_email, amount_display)
            except Exception:
                print(f"[paystack] Order: ref={ref} customer={user_email} amount={amount_display}")
            # Persist order in DB (mirror wallet flow)
            try:
                pending = session.get("pending_payment") or {}
                # discount saved as string
                try:
                    discount = Decimal(str(pending.get('discount') or '0'))
                except Exception:
                    discount = Decimal('0')

                # compute subtotal from items
                subtotal = Decimal('0')
                for it in items:
                    try:
                        subtotal += Decimal(str(it.get('subtotal', '0')))
                    except Exception:
                        pass

                # attempt to link to existing user by email
                usr = None
                if user_email:
                    usr = User.query.filter_by(email=user_email).first()

                # metadata may contain name/phone/city
                metadata = (data.get('data') or {}).get('metadata') or {}
                name = metadata.get('name') or ''
                phone = metadata.get('phone') or ''
                city = metadata.get('city') or ''

                order = Order(
                    reference=ref,
                    user_id=usr.id if usr else None,
                    email=user_email or '',
                    name=name,
                    phone=phone,
                    city=city,
                    subtotal=subtotal,
                    discount=discount,
                    total=Decimal(str(int(amount_minor) / 100)) if amount_minor else subtotal - discount,
                    status='pending',
                    payment_method='paystack',
                    payment_reference=ref,
                    paid=True
                )
                db.session.add(order)
                db.session.flush()
                for it in items:
                    try:
                        qty = int(it.get('qty') or 1)
                    except Exception:
                        qty = 1
                    try:
                        subtotal_item = Decimal(str(it.get('subtotal', '0')))
                    except Exception:
                        subtotal_item = Decimal('0')
                    price = subtotal_item / max(1, qty)
                    oi = OrderItem(
                        order_id=order.id,
                        product_id=it.get('product_id') if it.get('product_id') else None,
                        title=it.get('product'),
                        qty=qty,
                        price=price,
                        subtotal=subtotal_item
                    )
                    db.session.add(oi)

                # increment coupon usage if coupon applied
                try:
                    coupon_id = pending.get('coupon_id')
                    if coupon_id:
                        c = Coupon.query.get(int(coupon_id))
                        if c:
                            c.current_uses = (c.current_uses or 0) + 1
                except Exception:
                    pass

                # Log order creation
                try:
                    log = OrderLog(order_id=order.id, changed_by='system', old_status=None, new_status=order.status, note='Order created via paystack')
                    db.session.add(log)
                except Exception:
                    pass

                db.session.commit()
            except Exception:
                try:
                    db.session.rollback()
                    app.logger.exception("Failed to persist paystack order")
                except Exception:
                    print("[paystack order persist error]")

            # Clear session (prevent double-payment if callback is called multiple times)
            session.pop("cart", None)
            session.pop("pending_payment", None)
            flash("Payment successful via Paystack. Thank you!", "success")
            return redirect(url_for("index"))
        else:
            flash("Payment not successful. " + str(data.get("message", "check Paystack dashboard")), "warning")
            return redirect(url_for("index"))
    except Exception as e:
        try:
            app.logger.exception("Paystack verification failed: %s", e)
        except Exception:
            print(f"[paystack error] {e}")
        flash("Paystack verification error: " + str(e), "danger")
        return redirect(url_for("index"))

# --- Checkout page (shows Paystack form) ---
@app.route("/checkout/success")
def checkout_success():
    flash("Payment successful! Thank you for your order.", "success")
    return redirect(url_for("index"))


@app.route('/admin/test-email')
def admin_test_email():
    """Send a test email to the admin address to verify delivery/SMTP setup."""
    subject = "[Test] Admin notification from CyberWorld"
    html_body = """
    <html><body style="font-family:Arial,sans-serif; line-height:1.6; color:#333;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding:20px; text-align:center; color:white; border-radius:4px;">
            <h2 style="margin:0;">✅ Test Email</h2>
        </div>
        <div style="max-width:600px; margin:20px auto; padding:20px;">
            <p>This is a test email to verify admin notifications are working.</p>
            <p><strong>If you received this, email delivery is configured correctly!</strong></p>
            <div style="background-color:#e8f5e9; padding:15px; border-left:4px solid #4caf50; margin:20px 0; border-radius:4px;">
                <p style="margin:0;"><strong>✓ Configuration Status:</strong><br>
                MAIL_SERVER: {}<br>
                MAIL_USERNAME: {}<br>
                ADMIN_EMAIL: {}
                </p>
            </div>
        </div>
    </body></html>
    """.format(
        "✓ Configured" if MAIL_SERVER else "✗ Not configured",
        "✓ Configured" if MAIL_USERNAME else "✗ Not configured",
        ADMIN_EMAIL
    )
    
    body = "This is a test email to verify admin notifications are working.\n\nIf you received this, admin emails are delivering correctly.\n"
    try:
        ok = send_html_email_async(ADMIN_EMAIL, subject, html_body, body)
        if ok:
            return jsonify({"status": "sent", "to": ADMIN_EMAIL, "message": "Test email queued for sending"}), 200
        else:
            return jsonify({"status": "failed", "to": ADMIN_EMAIL}), 500
    except Exception as e:
        try:
            app.logger.exception("Admin test email failed: %s", e)
        except Exception:
            print(f"[email error] Admin test email failed: {e}")
        return jsonify({"status": "error", "detail": str(e)}), 500

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = _cart()
    if not cart:
        flash("Your cart is empty.", "warning"); return redirect(url_for("index"))

    items = []; total = Decimal('0')
    for pid_str, qty in cart.items():
        pid = int(pid_str); qty = int(qty)
        p = Product.query.get(pid)
        if not p: continue
        subtotal = Decimal(p.price_ghc) * qty
        items.append({"product": p, "qty": qty, "subtotal": subtotal})
        total += subtotal

    # Get user wallet balance if logged in
    wallet_balance = Decimal('0')
    if current_user.is_authenticated and hasattr(current_user, 'email'):
        if current_user.wallet:
            wallet_balance = Decimal(current_user.wallet.balance)

    # show page; form POSTS to either /pay/paystack or /pay/wallet based on selection
    return render_template("checkout.html", items=items, total=total, wallet_balance=wallet_balance)

@app.route('/api/validate-coupon', methods=['POST'])
def validate_coupon():
    """API to validate coupon code and return discount"""
    code = request.form.get('code', '').strip().upper()
    total_str = request.form.get('total', '0')
    
    try:
        total = Decimal(total_str)
    except:
        return jsonify({'valid': False, 'message': 'Invalid total amount'})
    
    if not code:
        return jsonify({'valid': False, 'message': 'Please enter a coupon code'})
    
    coupon = Coupon.query.filter_by(code=code).first()
    if not coupon:
        return jsonify({'valid': False, 'message': 'Coupon code not found'})
    
    # Check validity
    valid, message = coupon.is_valid()
    if not valid:
        return jsonify({'valid': False, 'message': message})
    
    # Check minimum amount
    if total < Decimal(str(coupon.min_amount)):
        return jsonify({'valid': False, 'message': f'Minimum order amount: GH₵{coupon.min_amount}'})
    
    # Calculate discount
    discount = coupon.calculate_discount(total)
    final_total = total - discount
    
    return jsonify({
        'valid': True,
        'message': f'Coupon applied! You saved GH₵{discount:.2f}',
        'coupon_id': coupon.id,
        'discount': float(discount),
        'discount_type': coupon.discount_type,
        'discount_value': float(coupon.discount_value),
        'final_total': float(final_total)
    })

# --- Admin (Flask-Login + image upload) ---
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    # If a customer is logged in, redirect them away
    if current_user.is_authenticated and hasattr(current_user, 'email') and not getattr(current_user, 'is_admin', False):
        flash('Please logout before accessing admin panel.', 'warning')
        return redirect(url_for('index'))
    
    # If admin already logged in, redirect to admin panel
    if current_user.is_authenticated and getattr(current_user, 'is_admin', False):
        return redirect(url_for('admin_index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return render_template('admin_login.html')
        
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in as admin.', 'success')
            return redirect(url_for('admin_index'))
        flash('Invalid admin credentials.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('register.html')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')

        try:
            user = User(email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()  # Flush to get the user.id before creating wallet
            wallet = Wallet(user_id=user.id, balance=Decimal('0'))
            db.session.add(wallet)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('user_login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration error: {str(e)}', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    """Customer login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def user_logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_index():
    # Only allow AdminUser, not customer User
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required. Please login as admin.', 'danger')
        return redirect(url_for('index'))

    prods = Product.query.order_by(Product.id.desc()).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    settings = get_settings()
    dashboard_layout = settings.dashboard_layout if settings and hasattr(settings, 'dashboard_layout') else 'grid'
    return render_template('admin_index.html', products=prods, recent_orders=recent_orders, dashboard_layout=dashboard_layout)


@app.route('/admin/order/<int:oid>/invoice')
@login_required
def admin_order_invoice(oid):
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required. Please login as admin.', 'danger')
        return redirect(url_for('index'))
    order = Order.query.get_or_404(oid)
    items = OrderItem.query.filter_by(order_id=order.id).all()
    return render_template('admin_invoice.html', order=order, items=items)

@app.route('/admin/new', methods=['GET','POST'])
@login_required
def admin_new():
    # Only allow AdminUser, not customer User
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required. Please login as admin.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        short = request.form.get('short', '').strip()
        price_str = request.form.get('price', '0').strip()
        old_price_str = request.form.get('old_price', '0').strip()
        featured = bool(request.form.get('featured'))

        # Card size handling
        card_size = request.form.get('card_size', 'medium').strip()
        if card_size not in ('small', 'medium', 'large'):
            card_size = 'medium'

        # Validate inputs
        if not title:
            flash('Product title is required.', 'danger')
            return render_template('admin_edit.html', product=None)
        
        try:
            price = Decimal(price_str) if price_str else Decimal('0')
            old_price = Decimal(old_price_str) if old_price_str else Decimal('0')
            if price < 0 or old_price < 0:
                raise ValueError("Prices cannot be negative")
        except Exception as e:
            flash(f'Invalid price format: {str(e)}', 'danger')
            return render_template('admin_edit.html', product=None)

        image_path = '/static/images/placeholder.png'
        
        # Handle image upload
        file = request.files.get('image_file')
        if file and file.filename and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                # Add timestamp to avoid filename conflicts
                import time
                filename = f"{int(time.time())}_{filename}"
                dest = Path(app.config['UPLOAD_FOLDER']) / filename
                file.save(dest)
                image_path = f'/static/images/{filename}'
            except Exception as e:
                flash(f'Image upload failed: {str(e)}', 'warning')

        try:
            prod = Product(title=title, short=short, price_ghc=price, old_price_ghc=old_price, image=image_path, featured=featured)
            db.session.add(prod)
            db.session.commit()
            flash('Product created successfully.', 'success')
            return redirect(url_for('admin_index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating product: {str(e)}', 'danger')
            return render_template('admin_edit.html', product=None)
    return render_template('admin_edit.html', product=None)

@app.route('/admin/edit/<int:pid>', methods=['GET','POST'])
@login_required
def admin_edit(pid):
    # Only allow AdminUser, not customer User
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required. Please login as admin.', 'danger')
        return redirect(url_for('index'))
    
    p = Product.query.get_or_404(pid)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        short = request.form.get('short', '').strip()
        price_str = request.form.get('price', '0').strip()
        old_price_str = request.form.get('old_price', '0').strip()
        featured = bool(request.form.get('featured'))

        # Card size handling
        card_size = request.form.get('card_size', 'small').strip()
        if card_size not in ('small', 'medium', 'large'):
            card_size = 'small'

        # Validate inputs
        if not title:
            flash('Product title is required.', 'danger')
            return render_template('admin_edit.html', product=p)
        
        try:
            price = Decimal(price_str) if price_str else Decimal('0')
            old_price = Decimal(old_price_str) if old_price_str else Decimal('0')
            if price < 0 or old_price < 0:
                raise ValueError("Prices cannot be negative")
        except Exception as e:
            flash(f'Invalid price format: {str(e)}', 'danger')
            return render_template('admin_edit.html', product=p)

        # Update basic fields
        p.title = title
        p.short = short
        p.price_ghc = price
        p.old_price_ghc = old_price
        p.featured = featured
        p.card_size = card_size

        # Handle image upload
        file = request.files.get('image_file')
        if file and file.filename and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                import time
                filename = f"{int(time.time())}_{filename}"
                dest = Path(app.config['UPLOAD_FOLDER']) / filename
                file.save(dest)
                p.image = f'/static/images/{filename}'
            except Exception as e:
                flash(f'Image upload failed: {str(e)}', 'warning')

        try:
            db.session.commit()
            flash(f'Product "{p.title}" updated successfully!', 'success')
            return redirect(url_for('admin_index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'danger')
            return render_template('admin_edit.html', product=p)
    return render_template('admin_edit.html', product=p)


@app.route('/admin/orders')
@login_required
def admin_orders():
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required. Please login as admin.', 'danger')
        return redirect(url_for('index'))
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin_orders.html', orders=orders)


@app.route('/admin/orders/export')
@login_required
def admin_orders_export():
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required. Please login as admin.', 'danger')
        return redirect(url_for('index'))
    import csv
    from io import StringIO
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['id','reference','email','total','paid','status','created_at'])
    for o in Order.query.order_by(Order.created_at.desc()).all():
        cw.writerow([o.id, o.reference, o.email, float(o.total), 'yes' if o.paid else 'no', o.status, o.created_at.isoformat() if o.created_at else ''])
    output = si.getvalue()
    return app.response_class(output, mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=orders.csv"})


@app.route('/admin/order/<int:oid>')
@login_required
def admin_order_detail(oid):
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required. Please login as admin.', 'danger')
        return redirect(url_for('index'))
    order = Order.query.get_or_404(oid)
    items = OrderItem.query.filter_by(order_id=order.id).all()
    return render_template('admin_order_detail.html', order=order, items=items)


@app.route('/admin/order/<int:oid>/update_status', methods=['POST'])
@login_required
def admin_order_update_status(oid):
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required. Please login as admin.', 'danger')
        return redirect(url_for('index'))
    order = Order.query.get_or_404(oid)
    new_status = request.form.get('status')
    if new_status not in ('pending', 'completed', 'cancelled'):
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin_order_detail', oid=oid))
    try:
        order.status = new_status
        db.session.commit()

        # notify user about status change
        try:
            if is_valid_email(order.email):
                subject = f"[Cyber World Store] Order {order.reference[:8]} — Status: {new_status.upper()}"
                
                # Get order items for display
                order_items = OrderItem.query.filter_by(order_id=order.id).all()
                items_with_images = []
                for oi in order_items:
                    item_dict = {
                        'product': oi.title,
                        'qty': oi.qty,
                        'price': float(oi.price),
                        'subtotal': float(oi.subtotal)
                    }
                    if oi.product_id:
                        p = Product.query.get(oi.product_id)
                        if p:
                            item_dict['image_path'] = p.image if p.image else ''
                    items_with_images.append(item_dict)
                
                # Build HTML based on status
                status_title = f"Order Status Update: {new_status.upper()}"
                status_message = ""
                status_color = "#ffc107"
                status_emoji = "📝"
                
                if new_status == 'completed':
                    status_message = "🎉 Great news! Your order has been processed and is on its way. You can expect delivery shortly. Track your package using the reference number below."
                    status_color = "#4caf50"
                    status_emoji = "✅"
                elif new_status == 'cancelled':
                    status_message = "❌ Your order has been cancelled as requested. If you have questions or need to place a new order, please contact us anytime."
                    status_color = "#f44336"
                    status_emoji = "❌"
                else:  # pending
                    status_message = "⚙️ Your order is being processed and prepared for shipment. We'll notify you as soon as it ships!"
                    status_color = "#2196f3"
                    status_emoji = "⏳"
                
                html = '<html><body style="font-family:Arial,sans-serif; line-height:1.6; color:#333;">'
                html += build_email_header_html(status_title)
                html += '<div style="max-width:600px; margin:0 auto; padding:20px;">'
                html += f'<p style="font-size:16px;"><strong>{status_emoji} Status Update for Your Order</strong></p>'
                html += f'<p>{status_message}</p>'
                html += f'<div style="background-color:#f5f5f5; padding:15px; border-left:4px solid {status_color}; margin:15px 0; border-radius:4px;">'
                html += f'<div style="font-size:12px; color:#666;">ORDER REFERENCE</div>'
                html += f'<div style="font-size:20px; font-weight:bold; color:{status_color};">{order.reference}</div>'
                html += f'<div style="margin-top:10px; font-size:14px;">'
                html += f'<strong>Status:</strong> <span style="color:{status_color}; font-weight:bold;">{new_status.upper()}</span><br>'
                html += f'<strong>Amount:</strong> GH₵{order.total:.2f}<br>'
                html += f'<strong>Payment Method:</strong> {order.payment_method.title()}'
                html += '</div></div>'
                
                # Show order items if available
                if items_with_images:
                    html += '<h3 style="color:#333; margin:20px 0 15px 0; font-size:16px;">📦 Order Items</h3>'
                    html += build_order_items_html(items_with_images)
                
                # Add action based on status
                if new_status == 'completed':
                    html += '<div style="background-color:#e8f5e9; padding:15px; border-radius:4px; margin:20px 0;">'
                    html += '<p style="margin:0;"><strong>🚚 Shipment Information</strong><br>'
                    html += 'Your order is on its way! Track your package in your account dashboard using the order reference above.</p>'
                    html += '</div>'
                elif new_status == 'cancelled':
                    html += '<div style="background-color:#ffebee; padding:15px; border-radius:4px; margin:20px 0;">'
                    html += '<p style="margin:0;"><strong>💬 Need Help?</strong><br>'
                    html += 'If this cancellation was unexpected or you have questions, please contact our support team immediately.</p>'
                    html += '</div>'
                else:
                    html += '<div style="background-color:#e3f2fd; padding:15px; border-radius:4px; margin:20px 0;">'
                    html += '<p style="margin:0;"><strong>⏱️ Processing</strong><br>'
                    html += 'We\'re preparing your items for shipment. You\'ll receive another notification when it ships.</p>'
                    html += '</div>'
                
                html += build_email_footer_html()
                html += '</div></body></html>'
                
                plain_text = f"Order Status Update\n\nHi {order.name or 'Valued Customer'},\n\nYour order status has been updated.\n\nOrder Reference: {order.reference}\nNew Status: {new_status.upper()}\nAmount: GH₵{order.total:.2f}\n\n{status_message}\n\nQuestions? Contact: cyberworldstore360@gmail.com"
                
                send_html_email_async(order.email, subject, html, plain_text)
        except Exception:
            pass

        flash('Order status updated.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to update order status: {e}', 'danger')
    return redirect(url_for('admin_order_detail', oid=oid))

@app.route('/admin/delete/<int:pid>', methods=['POST'])
@login_required
def admin_delete(pid):
    # Only allow AdminUser, not customer User
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required. Please login as admin.', 'danger')
        return redirect(url_for('index'))
    
    p = Product.query.get_or_404(pid)
    product_title = p.title
    try:
        db.session.delete(p)
        db.session.commit()
        flash(f'Product "{product_title}" deleted successfully.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'danger')
    return redirect(url_for('admin_index'))

@app.route('/admin/wallets')
@login_required
def admin_wallets():
    """View and manage user wallets"""
    # Check if user is admin (has username attribute from AdminUser)
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin_wallets.html', users=users)

@app.route('/admin/wallet/credit/<int:user_id>', methods=['POST'])
@login_required
def admin_credit_wallet(user_id):
    """Credit a user's wallet"""
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    amount_str = request.form.get('amount', '0').strip()
    
    try:
        amount = Decimal(amount_str)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if not user.wallet:
            user.wallet = Wallet(user=user, balance=Decimal('0'))
        
        user.wallet.balance = Decimal(user.wallet.balance) + amount
        db.session.commit()
        flash(f'Credited GH₵{amount:.2f} to {user.email}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error crediting wallet: {str(e)}', 'danger')
    
    return redirect(url_for('admin_wallets'))

@app.route('/admin/wallet/debit/<int:user_id>', methods=['POST'])
@login_required
def admin_debit_wallet(user_id):
    """Debit a user's wallet"""
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    amount_str = request.form.get('amount', '0').strip()
    
    try:
        amount = Decimal(amount_str)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if not user.wallet or Decimal(user.wallet.balance) < amount:
            raise ValueError("Insufficient wallet balance")
        
        user.wallet.balance = Decimal(user.wallet.balance) - amount
        db.session.commit()
        flash(f'Debited GH₵{amount:.2f} from {user.email}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error debiting wallet: {str(e)}', 'danger')
    
    return redirect(url_for('admin_wallets'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    """Manage site settings like logo, banners, fonts, colors"""
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required.', 'danger')
        return redirect(url_for('index'))
    
    settings = get_settings()
    
    if request.method == 'POST':
        # Update color and font settings
        settings.primary_color = request.form.get('primary_color', settings.primary_color)
        settings.secondary_color = request.form.get('secondary_color', settings.secondary_color)
        settings.primary_font = request.form.get('primary_font', settings.primary_font)
        settings.secondary_font = request.form.get('secondary_font', settings.secondary_font)

        # Update dashboard layout setting
        settings.dashboard_layout = request.form.get('dashboard_layout', settings.dashboard_layout)
        # SEO visibility and checklist
        settings.seo_visible = bool(request.form.get('seo_visible'))
        # Determine SEO checklist completion from individual boxes
        seo_items = ['site_title','meta_tags','robots_txt','mobile_friendly','page_speed','ssl_enabled']
        try:
            settings.seo_checklist_done = all(bool(request.form.get(item)) for item in seo_items)
        except Exception:
            settings.seo_checklist_done = False
        # Announcement / rich text (HTML allowed)
        if request.form.get('site_announcement') is not None:
            settings.site_announcement = request.form.get('site_announcement')
        
        # Handle logo upload (prefer S3 if configured, otherwise store as base64 in DB)
        if 'logo_file' in request.files and request.files['logo_file']:
            file = request.files['logo_file']
            if file and file.filename and allowed_file(file.filename):
                try:
                    mime_type = get_mime_type(file.filename)
                    # Try S3 first
                    if is_s3_configured():
                        key = f"logo_{int(time.time())}_{secure_filename(file.filename)}"
                        url = upload_to_s3(file, key, mime_type=mime_type)
                        if url:
                            settings.logo_image = url
                            # Clear DB-stored binary if present
                            settings.logo_image_data = None
                            settings.logo_image_mime = mime_type
                            flash('Logo uploaded to S3 successfully!', 'success')
                        else:
                            # fallback to DB storage
                            b64_data = encode_image_to_base64(file)
                            settings.logo_image_data = b64_data
                            settings.logo_image_mime = mime_type
                            settings.logo_image = f"/database/logo_from_{secure_filename(file.filename)}"
                            flash('Logo saved to database (fallback) successfully!', 'success')
                    else:
                        b64_data = encode_image_to_base64(file)
                        settings.logo_image_data = b64_data
                        settings.logo_image_mime = mime_type
                        settings.logo_image = f"/database/logo_from_{secure_filename(file.filename)}"
                        flash('Logo saved to database successfully!', 'success')
                except Exception as e:
                    flash(f'Logo upload failed: {str(e)}', 'warning')
        
        # Handle banner 1 upload (prefer S3 if configured, otherwise store as base64 in DB)
        if 'banner1_file' in request.files and request.files['banner1_file']:
            file = request.files['banner1_file']
            if file and file.filename and allowed_file(file.filename):
                try:
                    mime_type = get_mime_type(file.filename)
                    if is_s3_configured():
                        key = f"banner1_{int(time.time())}_{secure_filename(file.filename)}"
                        url = upload_to_s3(file, key, mime_type=mime_type)
                        if url:
                            settings.banner1_image = url
                            settings.banner1_image_data = None
                            settings.banner1_image_mime = mime_type
                            flash('Banner 1 uploaded to S3 successfully!', 'success')
                        else:
                            b64_data = encode_image_to_base64(file)
                            settings.banner1_image_data = b64_data
                            settings.banner1_image_mime = mime_type
                            settings.banner1_image = f"/database/banner1_from_{secure_filename(file.filename)}"
                            flash('Banner 1 saved to database (fallback) successfully!', 'success')
                    else:
                        b64_data = encode_image_to_base64(file)
                        settings.banner1_image_data = b64_data
                        settings.banner1_image_mime = mime_type
                        settings.banner1_image = f"/database/banner1_from_{secure_filename(file.filename)}"
                        flash('Banner 1 saved to database successfully!', 'success')
                except Exception as e:
                    flash(f'Banner 1 upload failed: {str(e)}', 'warning')
        
        # Handle banner 2 upload (prefer S3 if configured, otherwise store as base64 in DB)
        if 'banner2_file' in request.files and request.files['banner2_file']:
            file = request.files['banner2_file']
            if file and file.filename and allowed_file(file.filename):
                try:
                    mime_type = get_mime_type(file.filename)
                    if is_s3_configured():
                        key = f"banner2_{int(time.time())}_{secure_filename(file.filename)}"
                        url = upload_to_s3(file, key, mime_type=mime_type)
                        if url:
                            settings.banner2_image = url
                            settings.banner2_image_data = None
                            settings.banner2_image_mime = mime_type
                            flash('Banner 2 uploaded to S3 successfully!', 'success')
                        else:
                            b64_data = encode_image_to_base64(file)
                            settings.banner2_image_data = b64_data
                            settings.banner2_image_mime = mime_type
                            settings.banner2_image = f"/database/banner2_from_{secure_filename(file.filename)}"
                            flash('Banner 2 saved to database (fallback) successfully!', 'success')
                    else:
                        b64_data = encode_image_to_base64(file)
                        settings.banner2_image_data = b64_data
                        settings.banner2_image_mime = mime_type
                        settings.banner2_image = f"/database/banner2_from_{secure_filename(file.filename)}"
                        flash('Banner 2 saved to database successfully!', 'success')
                except Exception as e:
                    flash(f'Banner 2 upload failed: {str(e)}', 'warning')
        
        # Handle background upload (prefer S3 if configured, otherwise store as base64 in DB)
        if 'bg_file' in request.files and request.files['bg_file']:
            file = request.files['bg_file']
            if file and file.filename and allowed_file(file.filename):
                try:
                    mime_type = get_mime_type(file.filename)
                    if is_s3_configured():
                        key = f"bg_{int(time.time())}_{secure_filename(file.filename)}"
                        url = upload_to_s3(file, key, mime_type=mime_type)
                        if url:
                            settings.bg_image = url
                            settings.bg_image_data = None
                            settings.bg_image_mime = mime_type
                            flash('Background uploaded to S3 successfully!', 'success')
                        else:
                            b64_data = encode_image_to_base64(file)
                            settings.bg_image_data = b64_data
                            settings.bg_image_mime = mime_type
                            settings.bg_image = f"/database/bg_from_{secure_filename(file.filename)}"
                            flash('Background saved to database (fallback) successfully!', 'success')
                    else:
                        b64_data = encode_image_to_base64(file)
                        settings.bg_image_data = b64_data
                        settings.bg_image_mime = mime_type
                        settings.bg_image = f"/database/bg_from_{secure_filename(file.filename)}"
                        flash('Background saved to database successfully!', 'success')
                except Exception as e:
                    flash(f'Background upload failed: {str(e)}', 'warning')
        
        try:
            settings.updated_at = utc_now()
            db.session.commit()
            flash('Settings saved successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving settings: {str(e)}', 'danger')
    
    return render_template('admin_settings.html', settings=settings)

@app.route('/admin/settings/api', methods=['GET', 'POST'])
def admin_settings_api():
    """JSON API endpoint to read or save admin settings directly (no form complexity).

    Authentication:
    - If request includes header `X-ADMIN-TOKEN` matching env var `ADMIN_API_TOKEN`, the request is allowed.
    - Otherwise, a logged-in admin session (Flask-Login) is required.
    """
    # Token-based access for non-interactive scripts
    token = request.headers.get('X-ADMIN-TOKEN') or request.args.get('token')
    expected_token = os.environ.get('ADMIN_API_TOKEN')
    if expected_token and token and token == expected_token:
        authorized = True
    else:
        # Fall back to session-based admin check
        authorized = getattr(current_user, 'is_admin', False) and getattr(current_user, 'username', None)

    if not authorized:
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403

    settings = get_settings()

    # GET: return current settings
    if request.method == 'GET':
        return jsonify({
            'status': 'success',
            'settings': {
                'dashboard_layout': settings.dashboard_layout,
                'seo_visible': settings.seo_visible,
                'seo_checklist_done': settings.seo_checklist_done,
                'site_announcement': settings.site_announcement,
                'primary_color': settings.primary_color,
                'secondary_color': settings.secondary_color,
                'primary_font': settings.primary_font,
                'secondary_font': settings.secondary_font,
                'logo_image': settings.logo_image,
                'banner1_image': settings.banner1_image,
                'banner2_image': settings.banner2_image,
                'bg_image': settings.bg_image,
                'updated_at': settings.updated_at.isoformat() if settings.updated_at else None
            }
        }), 200

    # POST: update settings from JSON payload
    data = request.get_json() or {}

    try:
        # Update scalar fields from JSON payload
        if 'primary_color' in data:
            settings.primary_color = data.get('primary_color')
        if 'secondary_color' in data:
            settings.secondary_color = data.get('secondary_color')
        if 'primary_font' in data:
            settings.primary_font = data.get('primary_font')
        if 'secondary_font' in data:
            settings.secondary_font = data.get('secondary_font')
        if 'dashboard_layout' in data:
            settings.dashboard_layout = data.get('dashboard_layout')
        if 'seo_visible' in data:
            settings.seo_visible = bool(data.get('seo_visible'))
        if 'seo_checklist_done' in data:
            settings.seo_checklist_done = bool(data.get('seo_checklist_done'))
        if 'site_announcement' in data:
            settings.site_announcement = data.get('site_announcement', '')

        settings.updated_at = utc_now()
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Settings saved successfully',
            'settings': {
                'dashboard_layout': settings.dashboard_layout,
                'seo_visible': settings.seo_visible,
                'seo_checklist_done': settings.seo_checklist_done,
                'site_announcement': settings.site_announcement[:100]
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        try:
            app.logger.exception('Failed to save settings via API: %s', e)
        except Exception:
            pass
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin/coupons')
@login_required
def admin_coupons():
    """List all coupons"""
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required.', 'danger')
        return redirect(url_for('index'))
    
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    return render_template('admin_coupons.html', coupons=coupons)

@app.route('/admin/coupon/new', methods=['GET', 'POST'])
@login_required
def admin_coupon_new():
    """Create new coupon"""
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        discount_type = request.form.get('discount_type', 'percent')
        discount_value = request.form.get('discount_value', '0')
        max_uses = request.form.get('max_uses', '')
        min_amount = request.form.get('min_amount', '0')
        max_discount = request.form.get('max_discount', '')
        expiry_date = request.form.get('expiry_date', '')
        
        try:
            if Coupon.query.filter_by(code=code).first():
                flash('Coupon code already exists.', 'danger')
                return render_template('admin_coupon_edit.html', coupon=None)
            
            coupon = Coupon(
                code=code,
                discount_type=discount_type,
                discount_value=Decimal(discount_value),
                max_uses=int(max_uses) if max_uses else None,
                min_amount=Decimal(min_amount),
                is_active=True
            )
            
            if max_discount:
                coupon.max_discount = Decimal(max_discount)
            
            if expiry_date:
                from datetime import datetime
                coupon.expiry_date = datetime.fromisoformat(expiry_date)
            
            db.session.add(coupon)
            db.session.commit()
            flash(f'Coupon "{code}" created successfully!', 'success')
            return redirect(url_for('admin_coupons'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating coupon: {str(e)}', 'danger')
    
    return render_template('admin_coupon_edit.html', coupon=None)

@app.route('/admin/coupon/edit/<int:cid>', methods=['GET', 'POST'])
@login_required
def admin_coupon_edit(cid):
    """Edit coupon"""
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required.', 'danger')
        return redirect(url_for('index'))
    
    coupon = Coupon.query.get_or_404(cid)
    
    if request.method == 'POST':
        coupon.discount_type = request.form.get('discount_type', 'percent')
        coupon.discount_value = Decimal(request.form.get('discount_value', '0'))
        coupon.max_uses = int(request.form.get('max_uses', '')) if request.form.get('max_uses') else None
        coupon.min_amount = Decimal(request.form.get('min_amount', '0'))
        coupon.is_active = bool(request.form.get('is_active'))
        
        max_discount = request.form.get('max_discount', '')
        if max_discount:
            coupon.max_discount = Decimal(max_discount)
        else:
            coupon.max_discount = None
        
        expiry_date = request.form.get('expiry_date', '')
        if expiry_date:
            from datetime import datetime
            coupon.expiry_date = datetime.fromisoformat(expiry_date)
        else:
            coupon.expiry_date = None
        
        try:
            db.session.commit()
            flash('Coupon updated successfully!', 'success')
            return redirect(url_for('admin_coupons'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating coupon: {str(e)}', 'danger')
    
    return render_template('admin_coupon_edit.html', coupon=coupon)

@app.route('/admin/coupon/delete/<int:cid>', methods=['POST'])
@login_required
def admin_coupon_delete(cid):
    """Delete coupon"""
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required.', 'danger')
        return redirect(url_for('index'))
    
    coupon = Coupon.query.get_or_404(cid)
    code = coupon.code
    
    try:
        db.session.delete(coupon)
        db.session.commit()
        flash(f'Coupon "{code}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting coupon: {str(e)}', 'danger')
    
    return redirect(url_for('admin_coupons'))

@app.route('/admin/sliders')
@login_required
def admin_sliders():
    """List all sliders"""
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required.', 'danger')
        return redirect(url_for('index'))
    
    sliders = Slider.query.order_by(Slider.display_order).all()
    return render_template('admin_sliders.html', sliders=sliders)

@app.route('/admin/slider/new', methods=['GET', 'POST'])
@login_required
def admin_slider_new():
    """Create new slider"""
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        product_ids = request.form.getlist('products')
        
        try:
            slider = Slider(
                name=name,
                title=title,
                description=description,
                is_active=True,
                display_order=Slider.query.count()
            )
            
            for pid in product_ids:
                product = Product.query.get(int(pid))
                if product:
                    slider.products.append(product)
            
            db.session.add(slider)
            db.session.commit()
            flash(f'Slider "{name}" created successfully!', 'success')
            return redirect(url_for('admin_sliders'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating slider: {str(e)}', 'danger')
    
    products = Product.query.all()
    return render_template('admin_slider_edit.html', slider=None, products=products)

@app.route('/admin/slider/edit/<int:sid>', methods=['GET', 'POST'])
@login_required
def admin_slider_edit(sid):
    """Edit slider"""
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required.', 'danger')
        return redirect(url_for('index'))
    
    slider = Slider.query.get_or_404(sid)
    
    if request.method == 'POST':
        slider.title = request.form.get('title', '').strip()
        slider.description = request.form.get('description', '').strip()
        slider.is_active = bool(request.form.get('is_active'))
        product_ids = request.form.getlist('products')
        
        try:
            slider.products.clear()
            for pid in product_ids:
                product = Product.query.get(int(pid))
                if product:
                    slider.products.append(product)
            
            db.session.commit()
            flash('Slider updated successfully!', 'success')
            return redirect(url_for('admin_sliders'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating slider: {str(e)}', 'danger')
    
    products = Product.query.all()
    return render_template('admin_slider_edit.html', slider=slider, products=products)

@app.route('/admin/slider/delete/<int:sid>', methods=['POST'])
@login_required
def admin_slider_delete(sid):
    """Delete slider"""
    if not getattr(current_user, 'is_admin', False):
        flash('Admin access required.', 'danger')
        return redirect(url_for('index'))
    
    slider = Slider.query.get_or_404(sid)
    name = slider.name
    
    try:
        db.session.delete(slider)
        db.session.commit()
        flash(f'Slider "{name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting slider: {str(e)}', 'danger')
    
    return redirect(url_for('admin_sliders'))

# serve uploaded images from UPLOAD_FOLDER (which is /tmp on Vercel or ./static/images locally)
@app.route('/static/images/<path:fname>')
def static_images(fname):
    try:
        return send_from_directory(str(UPLOAD_FOLDER), fname)
    except Exception as e:
        # If image not found, return 404
        app.logger.warning("Image not found: %s (%s)", fname, e)
        abort(404)

@app.route('/image/<image_type>')
def serve_image(image_type):
    """Serve base64-encoded images from database (for persistent storage on Vercel)"""
    try:
        settings = get_settings()
        if not settings:
            abort(404)
        
        # Map image types to database columns
        image_map = {
            'logo': ('logo_image_data', 'logo_image_mime'),
            'banner1': ('banner1_image_data', 'banner1_image_mime'),
            'banner2': ('banner2_image_data', 'banner2_image_mime'),
            'bg': ('bg_image_data', 'bg_image_mime'),
        }
        
        if image_type not in image_map:
            abort(404)
        
        data_col, mime_col = image_map[image_type]
        image_data = getattr(settings, data_col)
        mime_type = getattr(settings, mime_col, 'image/jpeg')
        
        if not image_data:
            # Fallback to static image if no data stored
            abort(404)
        
        # Decode base64 and return as binary with correct mime type
        import base64
        if isinstance(image_data, bytes):
            # If stored as bytes, assume it's already base64-encoded
            try:
                decoded = base64.b64decode(image_data)
            except Exception:
                # If decoding fails, assume it's raw binary
                decoded = image_data
        else:
            # If stored as string, decode it
            decoded = base64.b64decode(image_data.encode('utf-8') if isinstance(image_data, str) else image_data)
        
        return app.response_class(
            response=decoded,
            status=200,
            mimetype=mime_type
        )
    except Exception as e:
        app.logger.warning("Error serving image %s: %s", image_type, e)
        abort(404)

# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Start background retry thread for failed emails
        try:
            t = threading.Thread(target=_retry_failed_emails_loop, kwargs={'interval':60}, daemon=True)
            t.start()
            app.logger.info('Started failed-email retry thread')
        except Exception:
            print('[email retry] failed to start retry thread')
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', '5000')))