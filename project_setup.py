# project_setup.py
# Generate fake data for DR project
# Author: Fiachra O' Donoghue

from faker import Faker
from faker_music import MusicProvider

fake = Faker()
fake.add_provider(MusicProvider)

print(fake.music_genre())
