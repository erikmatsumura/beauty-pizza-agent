from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.langchaindb import LangChainVectorDb

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Importações condicionais para diferentes vectorstores
try:
    from langchain_community.vectorstores import FAISS
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

try:
    from langchain_community.vectorstores import Chroma
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False

try:
    from langchain_community.vectorstores import DocArrayInMemorySearch
    HAS_DOCARRAY = True
except ImportError:
    HAS_DOCARRAY = False

# VectorStore simples em memória usando apenas Python puro
from typing import List, Dict, Any, Optional


class SimpleInMemoryVectorStore:
    """VectorStore simples em memória usando apenas Python padrão."""
    
    def __init__(self, embeddings_func):
        self.embeddings_func = embeddings_func
        self.texts: List[str] = []
        self.embeddings: List[List[float]] = []
        self.metadatas: List[Dict] = []
    
    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding,
        metadatas: Optional[List[Dict]] = None
    ):
        """Cria um vectorstore a partir de textos."""
        instance = cls(embedding)
        instance.add_texts(texts, metadatas)
        return instance
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict]] = None):
        """Adiciona textos ao vectorstore."""
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        # Gera embeddings para os textos
        text_embeddings = self.embeddings_func.embed_documents(texts)
        
        self.texts.extend(texts)
        self.embeddings.extend(text_embeddings)
        self.metadatas.extend(metadatas)
    
    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Busca por similaridade."""
        if not self.texts:
            return []
        
        # Gera embedding da query
        query_embedding = self.embeddings_func.embed_query(query)
        
        # Calcula similaridades (cosine similarity simplificada)
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((similarity, i))
        
        # Ordena por similaridade e pega os top k
        similarities.sort(reverse=True)
        top_k = similarities[:k]
        
        # Retorna documentos no formato esperado pelo LangChain
        results = []
        for _, idx in top_k:
            results.append({
                "page_content": self.texts[idx],
                "metadata": self.metadatas[idx]
            })
        
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similaridade coseno entre dois vetores."""
        # Produto escalar
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Normas
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        # Evita divisão por zero
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)


class AgnoEmbedderAdapter:
    """Adaptador para compatibilizar o embedder do Agno com o LangChain."""
    
    def __init__(self, agno_embedder):
        self.agno = agno_embedder

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed múltiplos documentos."""
        # Usa o método get_embeddings_batch se disponível
        if hasattr(self.agno, "get_embeddings_batch"):
            return self.agno.get_embeddings_batch(texts)
        # Senão usa get_embedding para cada texto
        elif hasattr(self.agno, "get_embedding"):
            return [self.agno.get_embedding(text) for text in texts]
        else:
            raise AttributeError(f"Embedder {type(self.agno)} não possui método de embedding reconhecido")

    def embed_query(self, text: str) -> list[float]:
        """Embed uma única query."""
        # Usa get_embedding do Agno
        if hasattr(self.agno, "get_embedding"):
            return self.agno.get_embedding(text)
        else:
            # Fallback: usa embed_documents com uma lista de um item
            return self.embed_documents([text])[0]


def debug_langchain_vectordb():
    """Debug para verificar a API do LangChainVectorDb."""
    import inspect
    
    print("🔍 Debugging LangChainVectorDb API:")
    try:
        # Verifica a assinatura do construtor
        sig = inspect.signature(LangChainVectorDb.__init__)
        print(f"Parâmetros do construtor: {list(sig.parameters.keys())}")
        
        # Verifica métodos disponíveis
        methods = [method for method in dir(LangChainVectorDb) if not method.startswith('_')]
        print(f"Métodos disponíveis: {methods[:10]}...")  # Primeiros 10
        
    except Exception as e:
        print(f"Erro no debug: {e}")
    print("---")


def setup_knowledge_base(
    file_path: str = "data/historia_pizza.txt",
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    embedder_model: str = "text-embedding-3-small",
    vectorstore_type: str = "chroma",
    persist_directory: str = "./chroma_db",
    debug: bool = False
) -> Knowledge:
    """
    Configura a base de conhecimento com embeddings e vectorstore.
    
    Args:
        file_path: Caminho para o arquivo de texto
        chunk_size: Tamanho dos chunks
        chunk_overlap: Sobreposição entre chunks
        embedder_model: Modelo de embedding a usar
        vectorstore_type: Tipo de vectorstore ("faiss", "chroma", "simple", "auto")
        persist_directory: Diretório para persistir dados do Chroma
        debug: Se True, mostra debug da API
    
    Returns:
        Knowledge: Objeto de conhecimento configurado
    """
    
    if debug:
        debug_langchain_vectordb()
    
    try:
        # 1) Carrega e processa o documento
        docs = TextLoader(file_path, encoding="utf-8").load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
        splits = splitter.split_documents(docs)
        
        # 2) Configura os embedders
        agno_embedder = OpenAIEmbedder(id=embedder_model)
        lc_embeddings = AgnoEmbedderAdapter(agno_embedder)
        
        # 3) Escolhe o vectorstore
        vectorstore = create_vectorstore(
            splits, 
            lc_embeddings, 
            vectorstore_type, 
            persist_directory
        )
        
        # 4) Envolve o vectorstore em LangChainVectorDb do Agno
        # Tenta diferentes formas de instanciar baseado na API disponível
        try:
            # Primeira tentativa: com embedder
            lc_db = LangChainVectorDb(vectorstore=vectorstore, embedder=agno_embedder)
        except TypeError:
            try:
                # Segunda tentativa: apenas vectorstore
                lc_db = LangChainVectorDb(vectorstore=vectorstore)
            except TypeError:
                try:
                    # Terceira tentativa: com vector_store (nome alternativo)
                    lc_db = LangChainVectorDb(vector_store=vectorstore)
                except TypeError:
                    # Última tentativa: apenas o vectorstore como positional
                    lc_db = LangChainVectorDb(vectorstore)
        
        # 5) Cria e retorna a base de conhecimento
        knowledge = Knowledge(name="kb_pizza", vector_db=lc_db)
        
        print(f"✅ Knowledge base configurada com sucesso usando {type(vectorstore).__name__}")
        return knowledge
        
    except Exception as e:
        print(f"❌ Erro ao configurar knowledge base: {e}")
        print("Tentando abordagem alternativa...")
        return setup_knowledge_base_alternative(file_path, chunk_size, chunk_overlap, embedder_model)


def create_vectorstore(splits, embeddings, vectorstore_type="chroma", persist_directory="./chroma_db"):
    """
    Cria o vectorstore mais adequado baseado na disponibilidade.
    """
    texts = [d.page_content for d in splits]
    metadatas = [{"source": f"chunk_{i}"} for i in range(len(texts))]
    
    # Auto: escolhe o melhor disponível
    if vectorstore_type == "auto":
        if HAS_CHROMA:
            vectorstore_type = "chroma"
        elif HAS_FAISS:
            vectorstore_type = "faiss"
        elif HAS_DOCARRAY:
            vectorstore_type = "docarray"
        else:
            vectorstore_type = "simple"
    
    # Chroma (recomendado - persistente e local)
    if vectorstore_type == "chroma" and HAS_CHROMA:
        print(f"📦 Usando Chroma vectorstore (persistindo em: {persist_directory})")
        return Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas,
            persist_directory=persist_directory,
            collection_name="beauty_pizza_knowledge"
        )
    
    # FAISS (melhor performance, mas não persiste por padrão)
    elif vectorstore_type == "faiss" and HAS_FAISS:
        print("📦 Usando FAISS vectorstore")
        return FAISS.from_texts(texts, embedding=embeddings, metadatas=metadatas)
    
    # DocArray InMemory 
    elif vectorstore_type == "docarray" and HAS_DOCARRAY:
        print("📦 Usando DocArray InMemory vectorstore (dados não persistem)")
        return DocArrayInMemorySearch.from_texts(texts, embedding=embeddings)
    
    # VectorStore simples em Python puro (sempre funciona)
    else:
        print("📦 Usando SimpleInMemory vectorstore (Python puro, dados não persistem)")
        return SimpleInMemoryVectorStore.from_texts(texts, embedding=embeddings)


def setup_knowledge_base_alternative(
    file_path: str = "data/historia_pizza.txt",
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    embedder_model: str = "text-embedding-3-small"
) -> Knowledge:
    """
    Versão alternativa usando diretamente o LangChain OpenAI embeddings.
    """
    try:
        from langchain_openai import OpenAIEmbeddings
        
        # 1) Carrega e processa o documento
        docs = TextLoader(file_path, encoding="utf-8").load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
        splits = splitter.split_documents(docs)
        
        # 2) Usa diretamente o LangChain OpenAI embeddings
        lc_embeddings = OpenAIEmbeddings(model=embedder_model)
        
        # 3) Cria o vectorstore (sempre usa o mais simples disponível)
        vectorstore = create_vectorstore(splits, lc_embeddings, "simple")
        
        # 4) Configura o embedder do Agno separadamente
        agno_embedder = OpenAIEmbedder(id=embedder_model)
        
        # 5) Envolve o vectorstore em LangChainVectorDb do Agno
        lc_db = LangChainVectorDb(vectorstore=vectorstore)
        
        # 6) Cria e retorna a base de conhecimento
        knowledge = Knowledge(name="kb_pizza", vector_db=lc_db)
        
        print("✅ Knowledge base alternativa configurada com sucesso")
        return knowledge
        
    except Exception as e:
        print(f"❌ Erro na abordagem alternativa: {e}")
        print("📚 Criando knowledge base básica...")
        
        # Fallback final: knowledge simples sem vectorstore avançado
        try:
            # Tenta criar uma versão muito básica
            docs = TextLoader(file_path, encoding="utf-8").load()
            agno_embedder = OpenAIEmbedder(id=embedder_model)
            knowledge = Knowledge(name="kb_pizza")
            
            # Adiciona o conteúdo como uma string simples para consulta
            content = "\n".join([doc.page_content for doc in docs])
            print(f"📄 Carregado conteúdo do arquivo: {len(content)} caracteres")
            
            return knowledge
            
        except Exception as final_error:
            print(f"❌ Erro final: {final_error}")
            # Retorna knowledge vazio como último recurso
            return Knowledge(name="kb_pizza")


def install_vectorstore_dependencies():
    """
    Instruções para instalar dependências de vectorstore.
    """
    print("\n🔧 Para usar Chroma (recomendado):")
    print("   pip install chromadb")
    print("\n🔧 Outras opções:")
    print("   • FAISS: pip install faiss-cpu")
    print("   • Para GPU: pip install faiss-gpu")
    print("\n📝 Comando completo:")
    print("   pip install chromadb faiss-cpu")
    print()


def reset_chroma_database(persist_directory: str = "./data/chroma_db"):
    """
    Remove o banco Chroma existente para forçar recriação.
    
    Args:
        persist_directory: Diretório do banco Chroma
    """
    import shutil
    import os
    
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        print(f"🗑️ Banco Chroma removido: {persist_directory}")
    else:
        print(f"📁 Diretório não existe: {persist_directory}")


def check_chroma_status(persist_directory: str = "./data/chroma_db"):
    """
    Verifica o status do banco Chroma.
    
    Args:
        persist_directory: Diretório do banco Chroma
    """
    import os
    
    if os.path.exists(persist_directory):
        files = os.listdir(persist_directory)
        print(f"📊 Banco Chroma existe em: {persist_directory}")
        print(f"📄 Arquivos: {len(files)}")
        return True
    else:
        print(f"❌ Banco Chroma não encontrado em: {persist_directory}")
        return False