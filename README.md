# Beauty Pizza Agent 🍕

Agente inteligente para atendimento da pizzaria Beauty Pizza desenvolvido com o framework **Agno**. Um sistema completo de atendimento conversacional com busca semântica e integração com API de pedidos.

## 🌟 Características

- 🤖 **Agente conversacional inteligente** para atendimento automatizado
- 📋 **Consulta de cardápio** com busca semântica usando embeddings
- 🛒 **Gerenciamento completo de pedidos** via API REST
- 💾 **Base de conhecimento local** (SQLite) para cardápio e preços
- 🔍 **Busca semântica avançada** com ChromaDB para ingredientes
- 📍 **Coleta automática** de dados do cliente e endereço de entrega
- 📚 **Base de conhecimento histórica** sobre pizza com embeddings
- 🎯 **Sistema multi-agente** com especialização de tarefas

## 🛠️ Pré-requisitos

- **Python 3.10+**
- **pip** para gerenciamento de pacotes
- **API de pedidos** rodando em `http://localhost:8000/api`
- **Chave OpenAI** configurada (para embeddings e LLM)

## 📦 Instalação

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd beauty-pizza-agent
```

2. **Instale as dependências:**
```bash
pip install agno chromadb httpx python-dotenv sqlite3 sentence-transformers
```

3. **Configure as variáveis de ambiente:**
```bash
# Crie um arquivo .env na raiz do projeto
OPENAI_API_KEY=your_openai_api_key_here
ORDER_API_URL=http://localhost:8000/api
```

## 🚀 Como executar

### Execução padrão:

1. **Navegue até o diretório do projeto:**
```bash
cd beauty-pizza-agent
```

2. **Execute o agente:**
```bash
python -m app.main
```

### 🔧 Primeira execução:
- O sistema criará automaticamente:
  - Banco SQLite em [`data/knowledge_base.db`](data/knowledge_base.db)
  - Banco vetorial ChromaDB em [`data/chroma_db/`](data/chroma_db/)
  - Embeddings da base de conhecimento histórica
- Dados de exemplo do cardápio serão inseridos automaticamente
- **Nota**: Warnings do Pydantic são normais e podem ser ignorados

### 💡 Comandos úteis:
- Digite `limpar` para zerar o contexto da conversa
- Digite `sair` para encerrar o programa

## ✨ Funcionalidades

### 🍕 Consultas de Cardápio
- **Listar sabores**: "Quais pizzas vocês têm?"
- **Buscar ingredientes**: "Que ingredientes tem na Margherita?"
- **Busca por características**: "Tem alguma pizza sem lactose?"

### 🛒 Montagem de Pedidos
- **Especificação completa**: Sabor, tamanho e borda
- **Cálculo automático de preços**: Baseado nas especificações
- **Validação de combinações**: Verifica disponibilidade

### 📦 Finalização de Pedidos
- **Coleta de dados**: Nome e documento do cliente
- **Endereço de entrega**: Rua, número, complemento e referência
- **Integração com API**: Criação automática do pedido

### 🔍 Busca Semântica
- **Base de conhecimento histórica**: Informações sobre a história da pizza
- **ChromaDB**: Busca inteligente por similaridade
- **Embeddings OpenAI**: Compreensão contextual avançada

## 📁 Estrutura do projeto

```
beauty-pizza-agent/
├── app/
│   ├── __init__.py
│   ├── agent.py              # Configuração dos agentes (Information + Executor)
│   ├── main.py              # Ponto de entrada da aplicação
│   ├── init_db.py           # Inicialização do banco SQLite
│   ├── tools/               # Ferramentas dos agentes
│   │   ├── __init__.py
│   │   ├── menu_tool.py     # Acesso ao cardápio (SQLite)
│   │   ├── order_api_tool.py # Integração com API de pedidos
│   │   └── schemas.py       # Modelos Pydantic para validação
│   └── embeddings/          # Sistema de embeddings
│       ├── __init__.py
│       └── knowledge_setup.py # Configuração ChromaDB e vectorstore
├── data/
│   ├── .gitkeep
│   ├── knowledge_base.db    # Base de dados do cardápio (auto-criado)
│   ├── historia_pizza.txt   # Arquivo de conhecimento histórico
│   └── chroma_db/          # Banco vetorial ChromaDB (auto-criado)
├── .env.example            # Exemplo de variáveis de ambiente
├── .gitignore
├── pyproject.toml          # Configuração do projeto Python
└── README.md
```

## 🎭 Sistema Multi-Agente

O projeto utiliza um **sistema de agentes especializados**:

### 🔍 Information Agent
- **Função**: Consultas de cardápio, ingredientes e preços
- **Ferramentas**: [`get_menu`](app/tools/menu_tool.py), [`get_ingredients`](app/tools/menu_tool.py), [`get_price`](app/tools/menu_tool.py)
- **Base de conhecimento**: Acesso à história da pizza via ChromaDB

### ⚡ Executor Agent  
- **Função**: Execução de ações relacionadas a pedidos
- **Ferramentas**: [`create_complete_order`](app/tools/order_api_tool.py), [`update_order_address`](app/tools/order_api_tool.py), [`get_client_orders`](app/tools/order_api_tool.py)
- **Integração**: API REST para gerenciamento de pedidos

## 💬 Exemplo de uso

```
🍕 Beauty Pizza — atendente inteligente
Digite 'limpar' para zerar contexto ou 'sair' para encerrar.

Você: Oi, quais pizzas vocês têm?
Atendente: Olá! Bem-vindo à Beauty Pizza! 🍕

Temos os seguintes sabores disponíveis:

**Sabores:**
• Margherita - A clássica pizza italiana
• Pepperoni - A pizza mais pedida nos EUA  
• Quatro Queijos - Combinação de queijos para os amantes de laticínios
• Calabresa - Saborosa pizza de calabresa com cebola
• Frango com Catupiry - Deliciosa pizza de frango desfiado
• Doce de Leite com Coco - Uma opção doce para fechar a refeição

**Tamanhos:** Pequena, Média, Grande
**Bordas:** Tradicional, Recheada com Cheddar, Recheada com Catupiry

Você: Quero uma pizza grande de pepperoni com borda de catupiry
Atendente: Perfeito! 🍕

**Seu pedido:**
- Pizza Grande de Pepperoni com Borda de Catupiry
- **Preço:** R$ 52,00

Para finalizar, preciso de algumas informações:
1. Seu nome completo
2. CPF ou documento
3. Endereço de entrega

Você: João Silva, CPF 123.456.789-00, Rua das Flores 123
Atendente: Pedido criado com sucesso! 🎉
**ID do pedido:** #1001
**Total:** R$ 52,00
**Previsão de entrega:** 30-45 minutos
```

## 🛠️ Tecnologias utilizadas

### 🧠 IA e Agentes
- **[Agno](https://github.com/phidatahq/agno)**: Framework para criação de agentes de IA
- **OpenAI GPT-4**: Modelo de linguagem para conversação
- **OpenAI Embeddings**: text-embedding-3-small para busca semântica

### 💾 Bancos de Dados
- **[ChromaDB](https://docs.trychroma.com/)**: Banco vetorial para busca semântica
- **SQLite**: Base de dados local para cardápio e preços
- **LangChain**: Framework para processamento de documentos

### 🌐 APIs e Integração
- **HTTPX/Requests**: Cliente HTTP para integração com API de pedidos
- **Pydantic**: Validação de dados e schemas
- **Python-dotenv**: Gerenciamento de variáveis de ambiente

## 🔧 Configuração avançada

### 📊 Banco de dados do cardápio

O sistema utiliza SQLite com as seguintes tabelas:
- **pizzas**: Sabores, descrições e ingredientes
- **tamanhos**: Pequena, Média, Grande
- **bordas**: Tradicional, Cheddar, Catupiry  
- **precos**: Matriz de preços por combinação

### 🔍 Base de conhecimento

- **Arquivo fonte**: [`data/historia_pizza.txt`](data/historia_pizza.txt)
- **Processamento**: Chunks de 800 caracteres com overlap de 120
- **Embeddings**: OpenAI text-embedding-3-small
- **Vectorstore**: ChromaDB persistente em [`data/chroma_db/`](data/chroma_db/)

### 🌐 API de pedidos

O sistema espera uma API REST com os seguintes endpoints:
- `POST /orders/` - Criar pedido
- `GET /orders/{id}/` - Buscar pedido  
- `PATCH /orders/{id}/add-items/` - Adicionar itens
- `PATCH /orders/{id}/update-address/` - Atualizar endereço
- `GET /orders/filter/` - Filtrar pedidos

## 🐛 Troubleshooting

### ❌ Problemas comuns:

1. **Erro de API Key**:
   ```bash
   # Verifique se a variável está configurada
   echo $OPENAI_API_KEY
   ```

2. **API de pedidos indisponível**:
   - Certifique-se que está rodando em `http://localhost:8000/api`
   - Teste com: `curl http://localhost:8000/api/orders/`

3. **Banco ChromaDB corrompido**:
   ```bash
   # Remove o banco para recriação
   rm -rf data/chroma_db/
   python -m app.main
   ```

### 🔄 Reset completo:
```bash
# Remove todos os dados gerados
rm -rf data/knowledge_base.db data/chroma_db/
python -m app.main
```

## 📈 Próximas funcionalidades

- [ ] Interface web com Streamlit
- [ ] Suporte a múltiplos idiomas
- [ ] Integração com WhatsApp
- [ ] Analytics de conversas
- [ ] Cache de embeddings
- [ ] Sistema de avaliações

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

**Desenvolvido com ❤️ usando Agno Framework**