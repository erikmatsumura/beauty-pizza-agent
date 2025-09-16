import httpx
import os

class OrderApiTool:
    def __init__(self, base_url: str | None = None, timeout: float = 10.0):
        self.base_url = base_url or os.getenv("ORDER_API_URL", "http://localhost:8000/api")
        self.client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def create_order(self, client_name: str, client_document: str, delivery_date: str | None = None) -> int:
        payload = {"client_name": client_name, "client_document": client_document}
        if delivery_date:
            payload["delivery_date"] = delivery_date
        r = self.client.post("/orders/", json=payload)
        r.raise_for_status()
        return r.json()["id"]

    def add_items(self, order_id: int, items: list[dict]) -> dict:
        """Adiciona múltiplos itens ao pedido usando o endpoint correto"""
        payload = {"items": items}
        r = self.client.patch(f"/orders/{order_id}/add-items/", json=payload)
        r.raise_for_status()
        return r.json()

    def add_item(self, order_id: int, name: str, quantity: int, unit_price: float) -> dict:
        """Adiciona um único item ao pedido"""
        items = [{"name": name, "quantity": quantity, "unit_price": unit_price}]
        return self.add_items(order_id, items)

    def set_address(self, order_id: int, street_name: str, number: str, complement: str | None = None,
                    reference_point: str | None = None) -> dict:
        payload = {
            "delivery_address": {
                "street_name": street_name, 
                "number": number, 
                "complement": complement,
                "reference_point": reference_point
            }
        }
        r = self.client.patch(f"/orders/{order_id}/update-address/", json=payload)
        r.raise_for_status()
        return r.json()

    def get_total(self, order_id: int) -> float:
        r = self.client.get(f"/orders/{order_id}/")
        r.raise_for_status()
        data = r.json()
        return float(data.get("total_price", 0.0))