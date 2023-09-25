"""empty message

Revision ID: e77a5046dc8d
Revises: 828455c0573f
Create Date: 2023-09-21 21:40:57.293598

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e77a5046dc8d'
down_revision = '828455c0573f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('foro',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('titulo', sa.String(length=120), nullable=False),
    sa.Column('fecha', sa.DateTime(), nullable=False),
    sa.Column('contenido', sa.String(length=240), nullable=False),
    sa.Column('comentario', sa.String(length=120), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['usuarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('foro')
    # ### end Alembic commands ###