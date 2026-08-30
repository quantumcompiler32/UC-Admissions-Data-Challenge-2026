import os

from unittest.mock import patch

from gemini import GeminiClient, client_from_environment


def test_client_reads_a_local_dotenv_without_overriding_process_environment(tmp_path):
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "GEMINI_API_KEY='key-from-local-file'\n"
        "GEMINI_MODEL='model-from-local-file'\n",
        encoding="utf-8",
    )

    with patch.dict(os.environ, {}, clear=True):
        client = client_from_environment(dotenv_path=dotenv)

    assert isinstance(client, GeminiClient)
    assert client.api_key == "key-from-local-file"
    assert client.model == "model-from-local-file"


def test_process_environment_wins_over_local_dotenv(tmp_path):
    dotenv = tmp_path / ".env"
    dotenv.write_text("GEMINI_API_KEY='key-from-file'\n", encoding="utf-8")

    with patch.dict(os.environ, {"GEMINI_API_KEY": "key-from-process"}, clear=True):
        client = client_from_environment(dotenv_path=dotenv)

    assert client.api_key == "key-from-process"
