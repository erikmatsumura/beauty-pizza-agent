# Beauty Pizza Agent

Agente inteligente para atendimento da pizzaria Beauty Pizza desenvolvido com o framework Agno.

## Características

- 🤖 Agente conversacional inteligente para atendimento
- 📋 Consulta de cardápio com busca semântica usando embeddings
- 🛒 Gerenciamento completo de pedidos via API
- 💾 Base de conhecimento local (SQLite) para cardápio
- 🔍 Busca semântica de ingredientes com ChromaDB
- 📍 Coleta de dados do cliente e endereço de entrega

## Pré-requisitos

- Python 3.10+
- pip ou conda
- API de pedidos rodando em `http://localhost:8000/api`

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd beauty-pizza-agent
```

2. Instale as dependências:
```bash
pip install agno chromadb httpx python-dotenv sqlite3
```

3. Configure as variáveis de ambiente (opcional):
```bash
# Crie um arquivo .env na raiz do projeto
ORDER_API_URL=http://localhost:8000/api
```

## Como executar

### Passo a passo para execução:

1. **Navegue até o diretório do projeto:**
```bash
cd /Users/eriktakashimatsumura/Documents/Projetos/beauty-pizza-agent
```

2. **Execute o agente:**
```bash
python -m app.main
```

### Comandos alternativos:

Se estiver no diretório correto, também pode usar:
```bash
python -m app.main
```

### Primeira execução:
- O sistema criará automaticamente o banco SQLite em `data/knowledge_base.db`
- O banco vetorial ChromaDB será criado em `data/chroma/`
- Dados de exemplo do cardápio serão inseridos automaticamente
- **Nota**: Warnings do Pydantic sobre "model_" namespace são normais e podem ser ignorados

### Requisitos do sistema:
- Certifique-se de que a API de pedidos esteja rodando em `http://localhost:8000/api`
- O projeto usará o ambiente Python atual (base conda)

## Funcionalidades

- **Consulta de cardápio**: "Quais pizzas vocês têm?"
- **Busca por ingredientes**: "Tem alguma pizza sem lactose?"
- **Montagem de pedido**: Especificar sabor, tamanho e borda
- **Cálculo de preços**: Preços automáticos baseados nas especificações
- **Finalização de pedido**: Coleta de dados do cliente e endereço
- **Busca semântica**: Encontra pizzas por características dos ingredientes

## Estrutura do projeto

```
beauty-pizza-agent/
├── app/
│   ├── agent.py           # Configuração do agente Agno
│   ├── main.py           # Ponto de entrada da aplicação
│   ├── state/
│   │   └── memory.py     # Gerenciamento de estado da conversa
│   ├── tools/
│   │   ├── menu_tool.py      # Acesso ao cardápio (SQLite)
│   │   ├── order_api_tool.py # Integração com API de pedidos
│   │   └── embeddings.py     # Busca semântica com ChromaDB
│   └── utils/
├── data/
│   ├── knowledge_base.db # Base de dados do cardápio (criado automaticamente)
│   └── chroma/          # Banco vetorial ChromaDB (criado automaticamente)
└── README.md
```

## Exemplo de uso

```
🍕 Beauty Pizza — atendente inteligente
Digite 'sair' para encerrar.

Você: Oi, quais pizzas vocês têm?
Atendente: Olá! Bem-vindo à Beauty Pizza! Temos os seguintes sabores disponíveis:
- Margherita (R$ 25,00)
- Pepperoni (R$ 30,00)
- Quatro Queijos (R$ 35,00)
...

Você: Quero uma pizza grande de pepperoni com borda de catupiry
Atendente: Perfeito! Pizza Grande de Pepperoni com borda de Catupiry.
Preço: R$ 48,00 (base R$ 30,00 + tamanho R$ 10,00 + borda R$ 8,00)
...
```

## Tecnologias utilizadas

- **Agno**: Framework para criação de agentes de IA
- **ChromaDB**: Banco vetorial para busca semântica
- **SQLite**: Base de dados local para cardápio
- **HTTPX**: Cliente HTTP para integração com API
- **SentenceTransformers**: Embeddings para busca semântica
