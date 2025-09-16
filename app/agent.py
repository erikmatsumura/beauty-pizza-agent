import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from app.tools.menu_tool import get_menu, get_ingredients, get_price
from app.tools.order_api_tool import create_complete_order,filter_orders,update_order_address,get_client_orders
from app.tools.embeddings import MenuEmbeddings
from app.init_db import initialize_database


# Inicializar base de dados primeiro
initialize_database()

# emb = MenuEmbeddings()
# emb.build_from_sqlite(menu_tool)

SYSTEM_PROMPT = """
Você é o atendente da Beauty Pizza. Seja objetivo e amigável.

REGRAS OBRIGATÓRIAS:
- Para dúvidas de cardápio: use get_menu()
- Para saber ingrediente de alguma pizza get_ingredients(flavor)
- Para montar pedido: SEMPRE peça sabor, tamanho e borda (todos obrigatórios)
- Sempre passe o preço apos o pedido
- Para preços: SEMPRE use get_price() - NUNCA chute valores
- Antes de confirmar: mostre resumo completo do carrinho

Sempre responda em português brasileiro.
"""

SYSTEM_PROMPT2 = """
Você é o atendente da Beauty Pizza. Seu objetivo é executar ações relacionadas a registro, busca e update de pedidos.

REGRAS OBRIGATÓRIAS:
-Quando tiver todas as informações, utilize create_complete_order para criar todo o pedido
-Para atualizar o endereço de um pedido existente, utilize update_order_address
-Para buscar pedidos de um cliente, utilize get_client_orders ou filter_orders
-Para cada ação, utilize os dados fornecidos pelo cliente


PARÂMETROS OBRIGATORIOS DE CADA FUNÇÃO:

update_order_address()
order_id (int) - ID do pedido
delivery_address (Dict) - Endereço de entrega, que deve conter:
street_name (str) - Nome da rua
number (str) - Número

create_complete_order() 
client_name (str) - Nome do cliente
client_document (str) - Documento do cliente
delivery_date (str) - Data de entrega no formato "YYYY-MM-DD"
items (List[Dict]) - Lista de itens ex:     Example:
        items = [
            {"name": "Produto A", "quantity": 2, "unit_price": 10.50},
            {"name": "Produto B", "quantity": 1, "unit_price": 25.00}
        ]

get_client_orders()
client_document (str) - Documento do cliente

Sempre responda em português brasileiro.
"""

information_agent = Agent(
    name="Information Agent",
    role="Procurar informações referentes ao cardapio, pedidos e ingredientes",
    model=OpenAIChat(id="gpt-4.1", temperature=0, max_tokens=6000),
    instructions=SYSTEM_PROMPT,
    tools=[get_menu, get_ingredients, get_price],
    markdown=True,
    debug_mode=True
)

executor_agent = Agent(
    name="Executor Agent",
    role="Executar ações relacionadas a pedidos",
    model=OpenAIChat(id="gpt-4.1", temperature=0, max_tokens=6000),
    tools=[get_price,create_complete_order,filter_orders,update_order_address,get_client_orders],
    instructions="use OrderApiTool (create_order → add_item → set_address → get_total)",
    markdown=True,
    debug_mode=True
)

agent = Team(model=OpenAIChat(id="gpt-4.1", temperature=0, max_tokens=6000),
             members=[information_agent, executor_agent])
