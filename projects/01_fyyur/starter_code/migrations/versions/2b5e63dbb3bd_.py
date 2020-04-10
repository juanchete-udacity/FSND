"""empty message

Revision ID: 2b5e63dbb3bd
Revises: fe4cb3c88e76
Create Date: 2020-04-09 15:37:35.238151

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b5e63dbb3bd'
down_revision = 'fe4cb3c88e76'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Genre',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=True),
    sa.Column('artist_id', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('artist_genres',
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['Genre.id'], ),
    sa.PrimaryKeyConstraint('artist_id', 'genre_id')
    )
    op.create_table('venue_genres',
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['genre_id'], ['Genre.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('venue_id', 'genre_id')
    )
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=1024), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('website', sa.String(length=500), nullable=True))
    op.alter_column('Artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('Artist', 'genres')
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=1024), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('website', sa.String(length=500), nullable=True))
    op.alter_column('Venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('Venue', 'website')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'seeking_description')
    op.add_column('Artist', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.alter_column('Artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'seeking_description')
    op.drop_table('venue_genres')
    op.drop_table('artist_genres')
    op.drop_table('Show')
    op.drop_table('Genre')
    # ### end Alembic commands ###
