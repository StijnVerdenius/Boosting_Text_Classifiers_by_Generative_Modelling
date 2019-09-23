import os
import h5py

from utils.data_manager import DataManager

from torch.utils.data import Dataset
import torch
import numpy as np

class LyricsDataset(Dataset):

    def __init__(self, folder, set_name, **kwargs):
        super(LyricsDataset, self).__init__()
        
        data_manager = DataManager(folder)
        
        # load the song entries pickle
        self._song_entries = data_manager.load_python_obj(f'song_lyrics.{set_name}')
        self.set_name = set_name
        # assert that the embedding folder exists inside the passed folder
        embeddings_folder_path = os.path.join(folder, 'embeddings')
        assert os.path.exists(embeddings_folder_path)
        
        # assert that the embedding file for this set exists inside the embedding folder
        self._embeddings_file_path = os.path.join(embeddings_folder_path, f'embeddings.{set_name}.hdf5')
        assert os.path.exists(self._embeddings_file_path)

        print('-- Loaded dataset:', self.set_name, '- size:', self.__len__())

    def __len__(self):
        return len(self._song_entries)

    def __getitem__(self, index):
        song_entry = self._song_entries[index]

        embeddings_file = h5py.File(self._embeddings_file_path, 'r')
        embeddings = None

        corrupt = False
        # TODO: Check if we shouldn't have all lines as one ELMO entry
        for index in range(song_entry.start_index, song_entry.start_index + song_entry.number_of_lines):
            if str(index) in embeddings_file.keys():
                sentence_embeddings = torch.Tensor(embeddings_file[str(index)])

                # if the embeddings are not initialized, initialize them,
                # otherwise just cat this line to the previous ones
                if embeddings is None:
                    embeddings = sentence_embeddings
                else:
                    embeddings = torch.cat([embeddings, sentence_embeddings], dim=0)
            else:
                print('Encountered: Unable to open object (object blabla doesnt exist)', index, self.set_name)
                corrupt = True
                break

        embeddings_file.close()
        if corrupt:
            return self.__getitem__(np.random.randint(0, self.__len__()))
        return embeddings, int(song_entry.genre.value)
