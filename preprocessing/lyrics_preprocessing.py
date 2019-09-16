import os
import csv
import numpy as np
import sys
import re

sys.path.append('..')

from utils.data_manager import DataManager
from utils.system_utils import ensure_current_directory
from models.entities.Song import Song

def save_dataset_text(dataset, embeddings_folder_path, filename):
    embeddings_filename = os.path.join(embeddings_folder_path, filename)
    with open(embeddings_filename, 'w', encoding='utf8') as embeddings_file:
        for _, song_entries in dataset.items():
            for song_entry in song_entries:
                embeddings_file.write(song_entry[1])

ensure_current_directory()
main_path = os.path.join('local_data', 'data')

dataset_folder_path = os.path.join(main_path, '380000-lyrics-from-metrolyrics')
if not os.path.exists(dataset_folder_path):
    raise Exception('Dataset folder does not exist')

dataset_file_path = os.path.join(dataset_folder_path, 'lyrics.csv')
if not os.path.exists(dataset_file_path):
    raise Exception('Dataset file does not exist')

with open(dataset_file_path, 'r', encoding="utf8") as dataset_file:
    next(dataset_file)  # skip the first line - headers
    dataset_reader = csv.reader(dataset_file, delimiter=',')

    classes_to_skip = ['Other', 'Not Available']

    song_entries_by_genre = {}

    lines_counter = 0

    for _, row in enumerate(dataset_reader):
        if row[4] in classes_to_skip:
            continue

        # Cut off songs which have lyrics with less than 30 characters
        if len(row[5]) < 100:
            continue
        
        if not any(c.isalpha() for c in row[5]):
            continue

        song_entry = Song(row[4], row[5], lines_counter)
        lines_counter += song_entry.number_of_lines

        if row[4] not in song_entries_by_genre.keys():
            song_entries_by_genre[row[4]] = [song_entry]
        else:
            song_entries_by_genre[row[4]].append(song_entry)

genres = list(song_entries_by_genre.keys())
songs_limit = 13000
for genre in genres:
    if len(song_entries_by_genre[genre]) < songs_limit:
        del song_entries_by_genre[genre]
    else:
        song_entries_by_genre[genre] = song_entries_by_genre[genre][:songs_limit]

train_data, validation_data, test_data = {}, {}, {}

embeddings_folder_path = os.path.join(main_path, 'embeddings')
if not os.path.exists(embeddings_folder_path):
    os.mkdir(embeddings_folder_path)

for genre, song_entries in song_entries_by_genre.items():
    # split data into train, validation and test sets
    train_data[genre] = song_entries[:int(len(song_entries)*0.7)]
    validation_data[genre] = song_entries[int(len(song_entries)*0.7):int(len(song_entries)*0.8)]
    test_data[genre] = song_entries[int(len(song_entries)*0.8):]

    # # print statistics
    min_length = min([len(song_entry.lyrics) for song_entry in song_entries])
    max_length = max([len(song_entry.lyrics) for song_entry in song_entries])
    avg_length = np.mean([len(song_entry.lyrics) for song_entry in song_entries])
    print(f'{genre} - min: {min_length} | max: {max_length} | mean: {avg_length} | all: {len(song_entries)} | train: {len(train_data[genre])} | validation: {len(validation_data[genre])} | test: {len(test_data[genre])}')

train_song_entries = [item for value in train_data.values() for item in value]
validation_song_entries = [item for value in validation_data.values() for item in value]
test_song_entries = [item for value in test_data.values() for item in value]

data_manager = DataManager(main_path)
print(data_manager.directory)
data_manager.save_python_obj(train_song_entries, 'song_lyrics.train')
data_manager.save_python_obj(validation_song_entries, 'song_lyrics.validation')
data_manager.save_python_obj(test_song_entries, 'song_lyrics.test')

# save_dataset_text(train_data, embeddings_folder_path, 'embeddings.train.txt')
# save_dataset_text(validation_data, embeddings_folder_path, 'embeddings.validation.txt')
# save_dataset_text(test_data, embeddings_folder_path, 'embeddings.test.txt')