import os
import httpx


import requests
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from datetime import datetime


@contextmanager
def _get_client(base_url: str | None = None, timeout: float = 10.0):
    """Context manager para criar uma sessão HTTP com configurações padrão."""
    if base_url is None:
        base_url = "http://localhost:8000/api"
    
    session = requests.Session()
    session.timeout = timeout
    try:
        # Configurar base URL
        class BaseURLSession(requests.Session):
            def request(self, method, url, *args, **kwargs):
                url = base_url.rstrip('/') + '/' + url.lstrip('/')
                return super().request(method, url, *args, **kwargs)
        
        client = BaseURLSession()
        client.timeout = timeout
        yield client
    finally:
        session.close()


def create_order(client_name: str, client_document: str, delivery_date: str,
                base_url: str | None = None, timeout: float = 10.0) -> int:
    """
    Cria um novo pedido.
    
    Args:
        client_name (str): Nome do cliente (obrigatório).
        client_document (str): Documento do cliente (obrigatório).
        delivery_date (str): Data de entrega do pedido "YYYY-MM-DD" (obrigatório).
        base_url (str | None): URL base da API.
        timeout (float): Timeout para requisições.
        
    Returns:
        int: ID do pedido criado.
        
    Raises:
        ValueError: Se algum campo obrigatório estiver vazio.
    """
    # Validação dos campos obrigatórios
    if not client_name or not client_name.strip():
        raise ValueError("client_name é obrigatório e não pode estar vazio")
    if not client_document or not client_document.strip():
        raise ValueError("client_document é obrigatório e não pode estar vazio")
    if not delivery_date or not delivery_date.strip():
        raise ValueError("delivery_date é obrigatório e não pode estar vazio")
    
    payload = {
        "client_name": client_name.strip(),
        "client_document": client_document.strip(),
        "delivery_date": delivery_date.strip()
    }
    
    with _get_client(base_url, timeout) as client:
        r = client.post("/orders/", json=payload)
        r.raise_for_status()
        return r.json()["id"]


def get_order(order_id: int, base_url: str | None = None, timeout: float = 10.0) -> Dict[str, Any]:
    """
    Busca um pedido pelo ID.
    
    Args:
        order_id (int): ID do pedido (obrigatório).
        base_url (str | None): URL base da API.
        timeout (float): Timeout para requisições.
        
    Returns:
        Dict[str, Any]: Dados do pedido.
        
    Raises:
        ValueError: Se order_id for inválido.
    """
    if not isinstance(order_id, int) or order_id <= 0:
        raise ValueError("order_id deve ser um número inteiro positivo")
        
    with _get_client(base_url, timeout) as client:
        r = client.get(f"/orders/{order_id}/")
        r.raise_for_status()
        return r.json()


def filter_orders(client_document: str, delivery_date: str | None = None,
                 base_url: str | None = None, timeout: float = 10.0) -> List[Dict[str, Any]]:
    """
    Filtra pedidos por documento do cliente e opcionalmente por data de entrega.
    
    Args:
        client_document (str): Documento do cliente (obrigatório).
        delivery_date (str | None): Data de entrega (opcional, formato YYYY-MM-DD).
        base_url (str | None): URL base da API.
        timeout (float): Timeout para requisições.
        
    Returns:
        List[Dict[str, Any]]: Lista de pedidos encontrados.
        
    Raises:
        ValueError: Se client_document estiver vazio.
    """
    # Validação do campo obrigatório conforme API
    if not client_document or not client_document.strip():
        raise ValueError("client_document é obrigatório e não pode estar vazio")
    
    params = {"client_document": client_document.strip()}
    if delivery_date and delivery_date.strip():
        params["delivery_date"] = delivery_date.strip()
    
    with _get_client(base_url, timeout) as client:
        r = client.get("/orders/filter/", params=params)
        r.raise_for_status()
        return r.json()


def add_items_to_order(order_id: int, items: List[Dict[str, Any]],
                      base_url: str | None = None, timeout: float = 10.0) -> Dict[str, Any]:
    """
    Adiciona itens a um pedido existente.
    
    Args:
        order_id (int): ID do pedido (obrigatório).
        items (List[Dict[str, Any]]): Lista de itens para adicionar (obrigatório).
            Cada item deve ter obrigatoriamente:
            - name (str): Nome do item (ex: Pizza margherita grande e borda recheada)
            - quantity (int): Quantidade do item  
            - unit_price (float/decimal): Preço unitário do item
        base_url (str | None): URL base da API.
        timeout (float): Timeout para requisições.
        
    Returns:
        Dict[str, Any]: Resposta da API.
        
    Raises:
        ValueError: Se os campos obrigatórios estiverem inválidos.
        
    Example:
        items = [
            {"name": "Produto A", "quantity": 2, "unit_price": 10.50},
            {"name": "Produto B", "quantity": 1, "unit_price": 25.00}
        ]
        add_items_to_order(1, items)
    """
    # Validações conforme API Swagger
    if not isinstance(order_id, int) or order_id <= 0:
        raise ValueError("order_id deve ser um número inteiro positivo")
    
    if not items:
        raise ValueError("items é obrigatório e não pode estar vazio")
    
    # Validar cada item conforme schema da API
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"Item {i} deve ser um dicionário")
        
        # Campos obrigatórios conforme API
        if not item.get("name") or not str(item["name"]).strip():
            raise ValueError(f"Item {i}: 'name' é obrigatório e não pode estar vazio")
        
        if "quantity" not in item:
            raise ValueError(f"Item {i}: 'quantity' é obrigatório")
        
        if not isinstance(item["quantity"], int) or item["quantity"] < 0:
            raise ValueError(f"Item {i}: 'quantity' deve ser um número inteiro não negativo")
        
        if "unit_price" not in item:
            raise ValueError(f"Item {i}: 'unit_price' é obrigatório")
        
        if not isinstance(item["unit_price"], (int, float)) or item["unit_price"] < 0:
            raise ValueError(f"Item {i}: 'unit_price' deve ser um número não negativo")
    
    payload = {"items": items}
    
    with _get_client(base_url, timeout) as client:
        r = client.patch(f"/orders/{order_id}/add-items/", json=payload)
        r.raise_for_status()
        return r.json() if r.content else {"message": "Itens adicionados com sucesso."}


def delete_item_from_order(order_id: int, item_id: int,
                          base_url: str | None = None, timeout: float = 10.0) -> bool:
    """
    Remove um item específico de um pedido.
    
    Args:
        order_id (int): ID do pedido (obrigatório).
        item_id (int): ID do item a ser removido (obrigatório).
        base_url (str | None): URL base da API.
        timeout (float): Timeout para requisições.
        
    Returns:
        bool: True se o item foi removido com sucesso.
        
    Raises:
        ValueError: Se os IDs forem inválidos.
    """
    if not isinstance(order_id, int) or order_id <= 0:
        raise ValueError("order_id deve ser um número inteiro positivo")
    
    if not isinstance(item_id, int) or item_id <= 0:
        raise ValueError("item_id deve ser um número inteiro positivo")
    
    with _get_client(base_url, timeout) as client:
        r = client.delete(f"/orders/{order_id}/items/{item_id}/")
        r.raise_for_status()
        return r.status_code == 204


def update_order_address(order_id: int, delivery_address: Dict[str, str],
                        base_url: str | None = None, timeout: float = 10.0) -> Dict[str, Any]:
    """
    Atualiza o endereço de entrega de um pedido.
    
    Args:
        order_id (int): ID do pedido (obrigatório).
        delivery_address (Dict[str, str]): Novo endereço de entrega (obrigatório).
            Campos obrigatórios:
            - street_name (str): Nome da rua
            - number (str): Número do endereço
            Campos opcionais:
            - complement (str): Complemento do endereço
            - reference_point (str): Ponto de referência
        base_url (str | None): URL base da API.
        timeout (float): Timeout para requisições.
        
    Returns:
        Dict[str, Any]: Resposta da API.
        
    Raises:
        ValueError: Se os campos obrigatórios estiverem inválidos.
        
    Example:
        address = {
            "street_name": "Rua das Flores",
            "number": "123",
            "complement": "Apt 45",
            "reference_point": "Próximo ao mercado"
        }
        update_order_address(1, address)
    """
    # Validações conforme API Swagger
    if not isinstance(order_id, int) or order_id <= 0:
        raise ValueError("order_id deve ser um número inteiro positivo")
    
    if not delivery_address or not isinstance(delivery_address, dict):
        raise ValueError("delivery_address é obrigatório e deve ser um dicionário")
    
    # Campos obrigatórios conforme API
    if not delivery_address.get("street_name") or not delivery_address["street_name"].strip():
        raise ValueError("'street_name' é obrigatório e não pode estar vazio")
    
    if not delivery_address.get("number") or not delivery_address["number"].strip():
        raise ValueError("'number' é obrigatório e não pode estar vazio")
    
    # Limpar espaços em branco dos campos obrigatórios
    cleaned_address = {
        "street_name": delivery_address["street_name"].strip(),
        "number": delivery_address["number"].strip()
    }
    
    # Adicionar campos opcionais se existirem
    if delivery_address.get("complement"):
        cleaned_address["complement"] = delivery_address["complement"].strip()
    if delivery_address.get("reference_point"):
        cleaned_address["reference_point"] = delivery_address["reference_point"].strip()
    
    payload = {"delivery_address": cleaned_address}
    
    with _get_client(base_url, timeout) as client:
        r = client.patch(f"/orders/{order_id}/update-address/", json=payload)
        r.raise_for_status()
        return r.json() if r.content else {"message": "Endereço atualizado com sucesso."}


# Funções auxiliares para facilitar o uso (mantidas como estavam, pois já usam as validações das funções acima)

def create_complete_order(client_name: str, client_document: str, delivery_date: str,
                         items: List[Dict[str, Any]], delivery_address: Dict[str, str],
                         base_url: str | None = None, timeout: float = 10.0) -> Dict[str, Any]:
    """
    Cria um pedido completo com itens e endereço de entrega.
    
    Args:
        client_name (str): Nome do cliente (obrigatório).
        client_document (str): Documento do cliente (obrigatório).
        delivery_date (str): Data de entrega "YYYY-MM-DD" (obrigatório).
        items (List[Dict[str, Any]]): Lista de itens do pedido (obrigatório).
        delivery_address (Dict[str, str]): Endereço de entrega (obrigatório).
        base_url (str | None): URL base da API.
        timeout (float): Timeout para requisições.
        
    Returns:
        Dict[str, Any]: Dados do pedido criado com todos os itens.
    """
    # Criar o pedido (já valida campos obrigatórios)
    order_id = create_order(client_name, client_document, delivery_date, base_url, timeout)
    
    # Adicionar itens se fornecidos (já valida campos obrigatórios)
    if items:
        add_items_to_order(order_id, items, base_url, timeout)
    
    # Atualizar endereço se fornecido (já valida campos obrigatórios)
    if delivery_address:
        update_order_address(order_id, delivery_address, base_url, timeout)
    
    # Retornar o pedido completo
    return get_order(order_id, base_url, timeout)


def get_client_orders(client_document: str, base_url: str | None = None, timeout: float = 10.0) -> List[Dict[str, Any]]:
    """
    Busca todos os pedidos de um cliente pelo documento.
    
    Args:
        client_document (str): Documento do cliente (obrigatório).
        base_url (str | None): URL base da API.
        timeout (float): Timeout para requisições.
        
    Returns:
        List[Dict[str, Any]]: Lista de todos os pedidos do cliente.
    """
    # Usa filter_orders que já valida o campo obrigatório
    return filter_orders(client_document, None, base_url, timeout)