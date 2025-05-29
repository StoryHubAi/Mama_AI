from pytest import fixture

@fixture
def sample_fixture():
    return "Hello, World!"

def test_hello_world(sample_fixture):
    assert sample_fixture == "Hello, World!"