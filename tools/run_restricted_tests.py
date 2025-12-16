import os
import sys
import io

# Ensure safe test envs (mirror CI)
os.environ['DATABASE_URL'] = 'sqlite:///./data.db'
os.environ['FORCE_EPHEMERAL'] = '1'
os.environ['MAIL_SERVER'] = ''
os.environ['MAIL_USERNAME'] = ''
os.environ['MAIL_PASSWORD'] = ''
os.environ['REDIS_URL'] = ''
os.environ['PAYSTACK_PUBLIC'] = 'test_public'
os.environ['PAYSTACK_SECRET'] = 'test_secret'
os.environ['SENDGRID_API_KEY'] = ''
os.environ['FLASK_ENV'] = 'testing'
os.environ['FLASK_DEBUG'] = '0'

buf = io.StringIO()
old_out, old_err = sys.stdout, sys.stderr
sys.stdout = buf
sys.stderr = buf

import pytest
# Run with no capture so output goes to our redirected stdout
args = ['-k', 'not e2e and not paystack and not email', '-q', '--capture=no']
ret = pytest.main(args)

# Restore
sys.stdout = old_out
sys.stderr = old_err

# Write output to file
with open('ci_test_output.txt', 'w', encoding='utf-8') as f:
    f.write(buf.getvalue())

print('pytest exit code:', ret)
sys.exit(ret)
