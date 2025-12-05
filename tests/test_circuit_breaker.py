from unittest.mock import MagicMock, patch

import httpx

from main import FAILURE_THRESHOLD, State, circuit_breakers


def test_circuit_breaker_opens_after_failures(client):
    backend_url = list(circuit_breakers.keys())[0]
    circuit_breakers[backend_url]["state"] = State.CLOSED
    circuit_breakers[backend_url]["failures"] = 0

    mock_get = MagicMock()
    mock_get.side_effect = httpx.RequestError("Connection failed")

    with patch("httpx.AsyncClient.get", mock_get):
        for _ in range(FAILURE_THRESHOLD * 3):
            try:
                client.get("/proxy/test")
            except:
                pass

    assert circuit_breakers[backend_url]["state"] == State.OPEN


def test_circuit_breaker_closes_on_success(client):
    backend_url = list(circuit_breakers.keys())[0]
    circuit_breakers[backend_url]["state"] = State.HALF_OPEN
    circuit_breakers[backend_url]["failures"] = 2

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}

    with patch("httpx.AsyncClient.get", return_value=mock_response):
        try:
            client.get("/proxy/test")
        except:
            pass

    assert circuit_breakers[backend_url]["failures"] == 0
