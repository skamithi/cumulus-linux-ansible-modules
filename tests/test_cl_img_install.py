"from mock import MagicMock"
import mock
from nose.tools import set_trace
from dev_modules.cl_img_install import get_sw_version
from asserts import assert_equals


def test_get_sw_version():
    release_file = open('tests/lsb-release.txt')
    with mock.patch('__builtin__.open') as mock_open:
        mock_open.return_value = release_file
        assert_equals(get_sw_version(), '2.0.0')
