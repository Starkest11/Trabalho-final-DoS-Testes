import pytest
import requests

# Endpoints do servidor vulnerável
BASE_URL = "http://127.0.0.1:5001"
UPLOAD_ENDPOINT = f"{BASE_URL}/upload"
HEALTH_ENDPOINT = f"{BASE_URL}/health"

# Função auxiliar para verificar se o servidor está online
def check_server():
    response = requests.get(HEALTH_ENDPOINT, timeout=5)
    assert response.status_code == 200, "Servidor não está respondendo corretamente!"

# Teste 1: Envio rápido de múltiplas requisições (Flood)
def test_flood_requests():
    """Teste: Explorar ausência de limitação de taxa enviando múltiplas requisições rapidamente."""
    responses = []
    for _ in range(100):  # Simula 100 requisições rápidas
        response = requests.post(UPLOAD_ENDPOINT, data=b"Flood Test")
        responses.append(response.status_code)
    assert all(status == 200 for status in responses), "ERRO: O servidor não processou todas as requisições de flood."

# Teste 2: Explorar ausência de validação ao enviar dados inválidos
def test_invalid_data():
    """Teste: Enviar dados maliciosos ou inválidos que o servidor não valida."""
    invalid_data = "This is not binary or JSON data"  # Dados inválidos
    response = requests.post(UPLOAD_ENDPOINT, data=invalid_data)
    assert response.status_code == 200, (
        f"ERRO: O servidor rejeitou dados inválidos com código {response.status_code}."
    )

# Teste 3: Explorar acúmulo de dados em memória
def test_memory_accumulation():
    """Teste: Enviar múltiplos dados para explorar o acúmulo na memória do servidor."""
    for i in range(200):  # Simula 200 requisições
        requests.post(UPLOAD_ENDPOINT, data=f"Data {i}".encode())

    # O servidor não tem controle de limpeza, logo, deve continuar aceitando dados
    response = requests.post(UPLOAD_ENDPOINT, data=b"Final Check")
    assert response.status_code == 200, "ERRO: O servidor não conseguiu processar devido à exaustão de memória."

# Teste 4: Enviar carga maliciosa dentro do limite permitido
def test_malicious_payload_within_limit():
    """Teste: Enviar carga maliciosa dentro do limite de 10 MB permitido."""
    payload = b"A" * (10 * 1024 * 1024 - 1)  # 1 byte a menos que o limite
    response = requests.post(UPLOAD_ENDPOINT, data=payload)
    assert response.status_code == 200, (
        f"ERRO: O servidor não aceitou uma carga maliciosa válida com código {response.status_code}."
    )
