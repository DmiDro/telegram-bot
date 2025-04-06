
"""make subscription_status enum

Revision ID: 0b2756bc53b3
Revises: 
Create Date: 2025-04-03 16:12:21.513986
"""


from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0b2756bc53b3'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'subscription_status_enum'
        ) THEN
            CREATE TYPE subscription_status_enum AS ENUM ('YES', 'NO');
        END IF;
    END
    $$;
    """)
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN subscription_status TYPE subscription_status_enum
        USING subscription_status::subscription_status_enum
    """)


def downgrade():
    op.execute("ALTER TABLE users ALTER COLUMN subscription_status TYPE TEXT")
    op.execute("DROP TYPE subscription_status_enum")
