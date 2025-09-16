import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from agno.agent import Agent
from app.tools.menu_tool import MenuTool
from app.tools.order_api_tool import OrderApiTool
from app.tools.embeddings import MenuEmbeddings

menu = MenuTool()
order_api = OrderApiTool()
emb = MenuEmbeddings()

emb.build_from_sqlite(menu)

# Debug: Print available tools
print("Available tools:")
print(f"- MenuTool methods: {[method for method in dir(menu) if not method.startswith('_')]}")
print(f"- MenuEmbeddings methods: {[method for method in dir(emb) if not method.startswith('_')]}")
print(f"- OrderApiTool methods: {[method for method in dir(order_api) if not method.startswith('_')]}")

SYSTEM_PROMPT = """
Você é o atendente da Beauty Pizza. Seja objetivo e amigável.

IMPORTANTE: Você DEVE usar as ferramentas disponíveis para obter informações reais. NUNCA invente dados.

REGRAS OBRIGATÓRIAS - USE AS FERRAMENTAS:
1. Para qualquer pergunta sobre cardápio, menu, pizzas disponíveis ou sabores: SEMPRE chame list_pizzas() PRIMEIRO
2. Para ingredientes de um sabor específico: chame get_ingredients(sabor)
3. Para busca de opções especiais: chame semantic_search(query)
4. Para calcular preços: chame get_price(sabor, tamanho, borda)

PALAVRAS-CHAVE QUE EXIGEM list_pizzas():
- "cardápio", "menu", "sabores", "pizzas", "opções", "que vocês têm", "disponível"

PROCESSO OBRIGATÓRIO:
1. Cliente pergunta sobre cardápio → CHAME list_pizzas()
2. Receba os dados → Formate e apresente ao cliente
3. NUNCA responda sem usar a ferramenta

Sempre use as ferramentas ANTES de responder ao cliente.
Respostas em português brasileiro.
"""

agent = Agent(
    instructions=SYSTEM_PROMPT,
    tools=[menu, order_api, emb],
)