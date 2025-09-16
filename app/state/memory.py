class ConversationMemory:
    def __init__(self):
        self.reset()

    def reset(self):
        self.history = []  
        self.order_items = []  
        self.client_info = {}  
        self.address = {}  
        self.order_id = None

    def add_message(self, sender: str, message: str):
        self.history.append({"sender": sender, "message": message})

    def add_item(self, item: dict):
        self.order_items.append(item)

    def set_client_info(self, info: dict):
        self.client_info = info

    def set_address(self, address: dict):
        self.address = address

    def set_order_id(self, order_id: int):
        self.order_id = order_id

    def get_summary(self):
        return {
            "itens": self.order_items,
            "cliente": self.client_info,
            "endereco": self.address,
            "order_id": self.order_id,
        }

memory = ConversationMemory()
