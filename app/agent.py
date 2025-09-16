import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from app.tools.menu_tool import get_menu, get_ingredients, get_price
from app.tools.order_api_tool import create_complete_order,filter_orders,update_order_address,get_client_orders
from app.init_db import initialize_database

from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.langchaindb import LangChainVectorDb

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.embeddings.knowledge_setup import setup_knowledge_base


# Inicializa o banco de dados
initialize_database()

# Configura a base de conhecimento com Chroma
knowledge = setup_knowledge_base(
    file_path="data/historia_pizza.txt",
    chunk_size=800,
    chunk_overlap=120,
    vectorstore_type="chroma",  # Força o uso do Chroma
    persist_directory="./data/chroma_db",  # Pasta para persistir os dados
    debug=True  # Mostra debug da API
)


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
order_id (int) - ID do pedido (OBRIGATORIO)
delivery_address (Dict) - Logradouro de entrega, que deve conter:
            {
            "street_name": "Nome da rua" (OBRIGATORIO),
            "number": "Numero do logradouro" (OBRIGATORIO),
            "complement": "Complemento" ,
            "reference_point": "Ponto de referência"
            }

create_complete_order() 
client_name (str) - Nome do cliente
client_document (str) - Documento do cliente
delivery_address (Dict) - Logradouro de entrega, que deve conter:
            {
            "street_name": "Nome da rua" (OBRIGATORIO),
            "number": "Numero do logradouro" (OBRIGATORIO),
            "complement": "Complemento" ,
            "reference_point": "Ponto de referência"
            }
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
debug_mode = False
markdown = False
information_agent = Agent(
    name="Information Agent",
    role="Procurar informações referentes ao cardapio, pedidos e ingredientes",
    model=OpenAIChat(id="gpt-4.1", temperature=0, max_tokens=6000),
    instructions=SYSTEM_PROMPT,
    knowledge=knowledge,
    tools=[get_menu, get_ingredients, get_price],
    markdown=markdown,
    debug_mode=debug_mode
)

executor_agent = Agent(
    name="Executor Agent",
    role="Executar ações relacionadas a pedidos",
    model=OpenAIChat(id="gpt-4.1", temperature=0, max_tokens=6000),
    tools=[get_price,create_complete_order,filter_orders,update_order_address,get_client_orders],
    instructions="use OrderApiTool (create_order → add_item → set_address → get_total)",
    markdown=markdown,
    debug_mode=debug_mode
)

agent = Team(model=OpenAIChat(id="gpt-4.1", temperature=0, max_tokens=6000),
             members=[information_agent, executor_agent])
