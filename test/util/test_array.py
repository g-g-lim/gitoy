from datetime import datetime
from database.entity.blob import Blob
from util.array import unique


def test_array_unique():
    unique_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert list(unique(unique_list)) == unique_list

    duplicate_list = [1,2,3,3,4,5,6,7,8,9,10]
    assert list(unique(duplicate_list)) == [1,2,3,4,5,6,7,8,9,10]

    dict_list = [
        {'object_id': '1234'},
        {'object_id': '12345'},
        {'object_id': '12345'},
        {'object_id': '123456'},
    ]

    assert len(list(unique(dict_list, 'object_id'))) == 3

    object_list = [
        Blob(object_id='1234', size=1, data=b'', created_at=datetime.now()),
        Blob(object_id='12345', size=1, data=b'', created_at=datetime.now()),
        Blob(object_id='12345', size=1, data=b'', created_at=datetime.now()),
        Blob(object_id='123456', size=1, data=b'', created_at=datetime.now()),
    ]

    assert len(list(unique(object_list, 'object_id'))) == 3

    empty_list = []

    assert len(list(unique(empty_list))) == 0