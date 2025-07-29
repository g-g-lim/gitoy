from pathlib import Path
from unittest.mock import patch
from database.database import Database
from repository.repository import Repository

from test.factory import random_index_entry


class TestIndexStore:
    """Test cases for Repository class."""

    def test_find_by_paths_with_relative_path(self, repository: Repository, database: Database, test_directory: Path):
        repository.init()

        index_entry_1 = random_index_entry('./file1.txt')
        index_entry_2 = random_index_entry('./test_dir/file2.txt')
        index_entry_3 = random_index_entry('./test_dir/sub_dir/file3.txt')

        database.create_index_entries([index_entry_1, index_entry_2, index_entry_3])

        with patch('os.getcwd', return_value=test_directory.parent.as_posix()):
            result = repository.index_store.find_by_paths(['.'])
            assert len(result) == 3
            assert result[0].file_path == index_entry_1.file_path
            assert result[1].file_path == index_entry_2.file_path
            assert result[2].file_path == index_entry_3.file_path

            result = repository.index_store.find_by_paths(['./'])
            assert len(result) == 3

            result = repository.index_store.find_by_paths(['test_dir'])
            assert len(result) == 2

            result = repository.index_store.find_by_paths(['test_dir/'])
            assert len(result) == 2

            result = repository.index_store.find_by_paths(['./test_dir'])
            assert len(result) == 2

            result = repository.index_store.find_by_paths(['./test_dir/'])
            assert len(result) == 2

            result = repository.index_store.find_by_paths(['./test_dir/sub_dir'])
            assert len(result) == 1

            result = repository.index_store.find_by_paths(['./test_dir/sub_dir/'])
            assert len(result) == 1

            result = repository.index_store.find_by_paths(['file1.txt'])
            assert len(result) == 1
            assert result[0].file_path == index_entry_1.file_path

            result = repository.index_store.find_by_paths(['test_dir/file2.txt'])
            assert len(result) == 1
            assert result[0].file_path == index_entry_2.file_path

            result = repository.index_store.find_by_paths(['test_dir/sub_dir/file3.txt'])
            assert len(result) == 1
            assert result[0].file_path == index_entry_3.file_path

    def test_find_by_paths_with_relative_path_2(self, repository: Repository, database: Database, test_directory: Path):
        repository.init()

        index_entry_1 = random_index_entry('./file1.txt')
        index_entry_2 = random_index_entry('./test_dir/file2.txt')
        index_entry_3 = random_index_entry('./test_dir/sub_dir/file3.txt')

        database.create_index_entries([index_entry_1, index_entry_2, index_entry_3])

        with patch('os.getcwd', return_value=test_directory.as_posix()):
            result = repository.index_store.find_by_paths(['./'])
            assert len(result) == 2

            result = repository.index_store.find_by_paths(['./file1.txt '])
            assert len(result) == 0

            result = repository.index_store.find_by_paths(['./test_dir'])
            assert len(result) == 0

            result = repository.index_store.find_by_paths(['./sub_dir'])
            assert len(result) == 1

    def test_find_by_paths_with_absolute_path(self, repository: Repository, database: Database, test_directory: Path):
        repository.init()

        index_entry_1 = random_index_entry('./file1.txt')
        index_entry_2 = random_index_entry('./test_dir/file2.txt')
        index_entry_3 = random_index_entry('./test_dir/sub_dir/file3.txt')

        database.create_index_entries([index_entry_1, index_entry_2, index_entry_3])

        with patch('os.getcwd', return_value=test_directory.parent.as_posix()):
            result = repository.index_store.find_by_paths([test_directory.parent.as_posix()]) # absolute path
            assert len(result) == 3
            assert result[0].file_path == index_entry_1.file_path
            assert result[1].file_path == index_entry_2.file_path
            assert result[2].file_path == index_entry_3.file_path

            result = repository.index_store.find_by_paths([test_directory.parent.as_posix() + '/']) # absolute path with trailing slash
            assert len(result) == 3
            
            
            