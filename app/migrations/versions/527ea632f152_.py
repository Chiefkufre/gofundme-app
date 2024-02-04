"""empty message

Revision ID: 527ea632f152
Revises: 595179340ce9
Create Date: 2024-01-21 02:22:10.818181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '527ea632f152'
down_revision = '595179340ce9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('campaigns', schema=None) as batch_op:
        batch_op.drop_column('is_publish')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('campaigns', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_publish', sa.BOOLEAN(), server_default=sa.text("'false'"), nullable=True))

    # ### end Alembic commands ###