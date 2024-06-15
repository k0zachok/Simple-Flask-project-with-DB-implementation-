"""empty message

Revision ID: 20cdd90cfbce
Revises: eedd5d133eef
Create Date: 2024-06-15 19:12:25.464403

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20cdd90cfbce'
down_revision = 'eedd5d133eef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game_session', schema=None) as batch_op:
        batch_op.add_column(sa.Column('double_down', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game_session', schema=None) as batch_op:
        batch_op.drop_column('double_down')

    # ### end Alembic commands ###
