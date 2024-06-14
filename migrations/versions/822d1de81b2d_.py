"""empty message

Revision ID: 822d1de81b2d
Revises: 
Create Date: 2024-06-14 14:03:14.802649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '822d1de81b2d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.String(length=20), nullable=False))
        batch_op.alter_column('username',
               existing_type=sa.VARCHAR(length=80),
               type_=sa.String(length=20),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=80),
               existing_nullable=False)
        batch_op.drop_column('password')

    # ### end Alembic commands ###