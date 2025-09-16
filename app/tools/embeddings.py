from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

class MenuEmbeddings:
    def __init__(self, collection_name: str = "pizzas"):
        Path("data/chroma").mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(path="data/chroma")
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            ),
        )

    def build_from_sqlite(self, menu_tool):
        """Constrói a base de embeddings a partir dos dados do SQLite"""
        try:
            # Verifica se já temos dados na collection
            if self.collection.count() > 0:
                return
            
            # Obtém todas as pizzas do menu
            pizzas = menu_tool.list_pizzas()
            
            documents = []
            metadatas = []
            ids = []
            
            for i, pizza in enumerate(pizzas):
                sabor = pizza['sabor']
                descricao = pizza['descricao']
                ingredientes = pizza['ingredientes']
                
                # Cria documento descritivo
                doc = f"Pizza {sabor}: {descricao}. Ingredientes: {ingredientes}"
                
                documents.append(doc)
                metadatas.append({
                    "sabor": sabor, 
                    "descricao": descricao,
                    "ingredientes": ingredientes
                })
                ids.append(f"pizza_{i}")
            
            # Adiciona à collection
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
        except Exception as e:
            print(f"Erro ao construir embeddings: {e}")

    def semantic_search(self, query: str, k: int = 5):
        """Busca semântica por pizzas baseada na consulta do usuário. Útil para encontrar opções específicas como 'sem lactose', 'vegana', etc."""
        res = self.collection.query(query_texts=[query], n_results=k)
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
    
        out = []
        for d, m in zip(docs, metas):
            out.append({
                "sabor": (m or {}).get("sabor"), 
                "descricao": (m or {}).get("descricao"),
                "ingredientes": (m or {}).get("ingredientes"),
                "desc": d
            })
        return out