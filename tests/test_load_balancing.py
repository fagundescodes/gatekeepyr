from unittest.mock import MagicMock, patch

from main import backend_metrics


def test_load_balancing_distributes_requests(client):
    for url in backend_metrics:
        backend_metrics[url] = 0

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"test": "data"}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        for _ in range(9):
            try:
                client.get("/proxy/test")
            except:
                pass

    total = sum(backend_metrics.values())
    assert total == 9

    for count in backend_metrics.values():
        assert count == 3
