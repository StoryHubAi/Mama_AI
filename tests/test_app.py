def test_africastalking_import():
    try:
        import africastalking
        assert True
    except ImportError:
        assert False, "africastalking module is not installed"