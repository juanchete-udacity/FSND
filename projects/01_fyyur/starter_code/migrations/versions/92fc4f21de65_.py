"""empty message

Revision ID: 92fc4f21de65
Revises: 2b5e63dbb3bd
Create Date: 2020-04-10 15:31:25.092591

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '92fc4f21de65'
down_revision = '2b5e63dbb3bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('artist_genres')
    op.drop_table('venue_genres')
    op.drop_table('Genre')
    op.add_column('Artist', sa.Column('genres', postgresql.ARRAY(sa.String()), nullable=False))
    op.add_column('Venue', sa.Column('genres', postgresql.ARRAY(sa.String()), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    op.drop_column('Artist', 'genres')
    op.create_table('venue_genres',
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('genre_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['genre_id'], ['Genre.id'], name='venue_genres_genre_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], name='venue_genres_venue_id_fkey'),
    sa.PrimaryKeyConstraint('venue_id', 'genre_id', name='venue_genres_pkey')
    )
    op.create_table('artist_genres',
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('genre_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], name='artist_genres_artist_id_fkey'),
    sa.ForeignKeyConstraint(['genre_id'], ['Genre.id'], name='artist_genres_genre_id_fkey'),
    sa.PrimaryKeyConstraint('artist_id', 'genre_id', name='artist_genres_pkey')
    )
    op.create_table('Genre',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Genre_id_seq"\'::regclass)'), nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='Genre_pkey')
    )
    # ### end Alembic commands ###
