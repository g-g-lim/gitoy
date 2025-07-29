from pathlib import Path

current_path = Path(__file__).parent

def test_pathlib():
    path= Path('..')
    assert path.as_posix() == '..'

    path= Path('../test')
    assert path.as_posix() == '../test'
    assert path.name == 'test'

    path= '..' / Path('repository')
    current_dir = path.resolve().name  # 절대 경로로 변환 후 디렉토리명 추출
    assert current_dir == 'repository'

    cwd = Path.cwd()
    assert cwd.is_absolute()
    assert cwd.is_dir()

    path = Path('test.py')
    assert path.resolve() == cwd / 'test.py'

    path = Path('./test.py')
    assert path.resolve() == cwd / 'test.py'

    path = Path('test/util/test_pathlib.py')
    assert path.resolve() == cwd / 'test/util/test_pathlib.py'
    assert path.resolve().relative_to(cwd) == Path('test/util/test_pathlib.py')
    assert path.resolve().relative_to(cwd).exists()
