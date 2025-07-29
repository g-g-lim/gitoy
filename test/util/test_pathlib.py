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

    actual_path = Path.cwd() / path.resolve()  # 현재 디렉토리 기준으로 실제 경로 계산
    assert actual_path.resolve().name == 'repository'

    cwd = Path.cwd()
    assert cwd.is_absolute()
    assert cwd.is_dir()

    path = Path('test.py')
    assert path.resolve() == cwd / 'test.py'

    path = Path('./test.py')
    assert path.resolve() == cwd / 'test.py'
