from unittest.mock import Mock

import main


def test_args():
    name = 'test'

    req = Mock(get_json=Mock(return_value={}))
    _, status = main.http_handler(req)
    assert status == 400

    data = {'operation': '3x + 1 = 4', 'step': '3x = 3'}
    req = Mock(get_json=Mock(return_value=data))
    assert main.http_handler(req) == {'fake': 'json'}
