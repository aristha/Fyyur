"""Initial migrationa.

Revision ID: 372937fee5a3
Revises: 71a4e563141f
Create Date: 2022-11-12 00:41:07.382918

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '372937fee5a3'
down_revision = '71a4e563141f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('genres', sa.ARRAY(sa.String(length=120)), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'genres')
    # ### end Alembic commands ###
