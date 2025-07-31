from pathlib import Path
import tempfile
from database.database import Database
from repository.convert import Convert
from repository.index_diff import IndexDiff
from repository.repo_path import RepositoryPath
from repository.repository import Repository
from util.file import File
from unittest import mock

class TestIndexDiff:

    def test_diff_added(
        self,
        repository: Repository, 
        repository_path: RepositoryPath,
        index_diff: IndexDiff, 
        convert: Convert, 
        test_file: File
    ):
        repository.init()

        with mock.patch('os.getcwd', return_value=repository_path.worktree_path.as_posix()):
            result = index_diff.diff([test_file.path.parent.name])
            assert len(result['added']) == 1
            assert result['added'][0] == convert.path_to_index_entry(test_file.path)
            assert result['deleted'] == []
            assert result['modified'] == []

    def test_diff_deleted(
        self, 
        repository: Repository, 
        index_diff: IndexDiff, 
        convert: Convert, 
        database: Database,
        test_directory: Path,
    ):
        repository.init()
    
        with mock.patch('os.getcwd', return_value=test_directory.as_posix()):
            _, _path = tempfile.mkstemp(dir=test_directory)
            path = Path(_path)
            index_entry = convert.path_to_index_entry(path)
            database.create_index_entries([index_entry])
        
            path.unlink()

            result = index_diff.diff([_path])
            assert result['added'] == []
            assert len(result['deleted']) == 1
            assert result['deleted'][0] == index_entry
            assert result['modified'] == []

    def test_diff_modified(
        self,
        repository: Repository,
        index_diff: IndexDiff,
        convert: Convert,
        database: Database,
        test_directory: Path,
    ):
        repository.init()   

        with mock.patch('os.getcwd', return_value=test_directory.as_posix()):
            _, _path = tempfile.mkstemp(dir=test_directory)
            path = Path(_path)
            index_entry = convert.path_to_index_entry(path)
            database.create_index_entries([index_entry])
        
            path.write_text('modified')

            result = index_diff.diff([_path])
            assert result['added'] == []
            assert result['deleted'] == []
            assert len(result['modified']) == 1
            assert result['modified'][0] == convert.path_to_index_entry(path)

    def test_diff_mixed(
        self,
        repository: Repository,
        index_diff: IndexDiff,
        convert: Convert,
        database: Database,
        test_directory: Path,
    ):  
        repository.init()

        with mock.patch('os.getcwd', return_value=test_directory.as_posix()):
            _, _path = tempfile.mkstemp(dir=test_directory)
            path = Path(_path)
            index_entry = convert.path_to_index_entry(path)
            database.create_index_entries([index_entry])
            path.write_text('modified')

            _, _path2 = tempfile.mkstemp(dir=test_directory)

            result = index_diff.diff([_path, _path2])
            assert len(result['added']) == 1
            assert result['added'][0] == convert.path_to_index_entry(Path(_path2))
            assert result['deleted'] == []
            assert len(result['modified']) == 1
            assert result['modified'][0] == convert.path_to_index_entry(path)

            path.unlink()

            result = index_diff.diff([_path, _path2])
            assert len(result['added']) == 1
            assert len(result['deleted']) == 1
            assert len(result['modified']) == 0

            path2 = Path(_path2)
            index_entry2 = convert.path_to_index_entry(path2)
            database.create_index_entries([index_entry2])
            path2.write_text('modified')

            result = index_diff.diff([_path, _path2])
            assert len(result['added']) == 0
            assert len(result['deleted']) == 1
            assert len(result['modified']) == 1

            _, _path3 = tempfile.mkstemp(dir=test_directory)

            result = index_diff.diff([_path, _path2, _path3])
            assert len(result['added']) == 1
            assert len(result['deleted']) == 1
            assert len(result['modified']) == 1

            result = index_diff.diff([_path, _path2])
            assert len(result['added']) == 0
            assert len(result['deleted']) == 1
            assert len(result['modified']) == 1

            result = index_diff.diff([_path2, _path3])
            assert len(result['added']) == 1
            assert len(result['deleted']) == 0
            assert len(result['modified']) == 1
                
    def test_diff_path_changed(
        self,
        repository: Repository,
        index_diff: IndexDiff,
        convert: Convert,
        database: Database,
        test_directory: Path,
    ):
        repository.init()   

        with mock.patch('os.getcwd', return_value=test_directory.as_posix()):
            _, _path = tempfile.mkstemp(dir=test_directory)
            path = Path(_path)
            index_entry = convert.path_to_index_entry(path)
            database.create_index_entries([index_entry])
        
            renamed = path.with_name('renamed')
            path.rename(renamed)

            result = index_diff.diff([renamed.name])
            assert len(result['added']) == 1
            assert result['added'][0] == convert.path_to_index_entry(renamed)
            assert result['deleted'] == []
            assert result['modified'] == []

            result = index_diff.diff(['.'])
            assert len(result['added']) == 1
            assert len(result['deleted']) == 1
            assert result['modified'] == []

            result = index_diff.diff([f'../{test_directory.name}'])
            assert len(result['added']) == 1
            assert len(result['deleted']) == 1
            assert result['modified'] == []


    def test_diff_on_check_duplicate_path(
        self,
        repository: Repository,
        index_diff: IndexDiff,
        convert: Convert,
        database: Database,
        test_directory: Path,
    ):
        repository.init()

        with mock.patch('os.getcwd', return_value=test_directory.as_posix()):
            _, _path = tempfile.mkstemp(dir=test_directory)
            path = Path(_path)
            index_entry = convert.path_to_index_entry(path)
            database.create_index_entries([index_entry])
            path.unlink()

            _, _path2 = tempfile.mkstemp(dir=test_directory)

            path2 = Path(_path2)
            index_entry2 = convert.path_to_index_entry(path2)
            database.create_index_entries([index_entry2])
            path2.write_text('modified')

            _, _path3 = tempfile.mkstemp(dir=test_directory)

            result = index_diff.diff([_path, _path2, _path3, './'])
            assert len(result['added']) == 1
            assert len(result['deleted']) == 1
            assert len(result['modified']) == 1