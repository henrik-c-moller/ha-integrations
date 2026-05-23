import pytest
from unittest.mock import patch

@pytest.fixture
def mock_api():
    with patch("custom_components.aflas_dk.api.AflasAPI") as api:
        yield api

