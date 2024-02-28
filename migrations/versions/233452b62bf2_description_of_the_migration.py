"""Description of the migration

Revision ID: 233452b62bf2
Revises: 2eb04abe312d
Create Date: 2024-02-09 14:31:28.154559

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '233452b62bf2'
down_revision = '2eb04abe312d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.VARCHAR(length=255), nullable=True))

    # ### end Alembic commands ###
