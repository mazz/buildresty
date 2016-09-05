"""seed db with admin user

Revision ID: 470a2280528d
Revises: a7e25b669ad4
Create Date: 2016-09-04 22:57:54.469907

"""

# revision identifiers, used by Alembic.
revision = '470a2280528d'
down_revision = 'a7e25b669ad4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

from restytest2.models.auth import User

def upgrade():
    """Preseed data into the system."""
    current_context = op.get_context()
    meta = current_context.opts['target_metadata']
    user = sa.Table('users', meta, autoload=True)

    api_key = User.gen_api_key()
    # Add the initial admin user account.
    op.bulk_insert(user, [{
        'username': u'admin',
        'password': u'$2a$10$FK7DVvSYzXNqJRbYD8yAJ..eKosDzYH29ERuKCwlMLdozMWDkySl2',
        'email': u'foo@bar.bar',
        'is_active': True,
        'is_authenticated': False,
        'is_admin': True,
        'invite_ct': 100,
        'api_key': api_key,
        }
    ])


def downgrade():
    current_context = op.get_context()
    meta = current_context.opts['target_metadata']
    user = sa.Table('users', meta, autoload=True)

    # remove all records to undo the preseed.
    op.execute(user.delete())
