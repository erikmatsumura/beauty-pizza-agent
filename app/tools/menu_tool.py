import sqlite3
import logging
from pathlib import Path
from .schemas import PizzaSpec

import sqlite3
import logging
from pathlib import Path
from .schemas import PizzaIngredients,Flavor

def _get_connection(db_path: str = "data/knowledge_base.db"):
    """Cria conexão com o banco de dados."""
    db_path_obj = Path(db_path)
    db_path_obj.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path_obj)

def get_menu(db_path: str = "data/knowledge_base.db") -> dict:
    """Lista pizzas, tamanhos e bordas disponíveis."""
    with _get_connection(db_path) as con:
        # Pizzas
        pizzas_cur = con.execute("SELECT sabor, descricao FROM pizzas ORDER BY sabor")
        pizzas = [{"flavor": f, "description": d} for (f, d) in pizzas_cur.fetchall()]
        
        # Tamanhos  
        sizes_cur = con.execute("SELECT tamanho FROM tamanhos ORDER BY id")
        sizes = [row[0] for row in sizes_cur.fetchall()]
        
        # Bordas
        crusts_cur = con.execute("SELECT tipo FROM bordas ORDER BY id") 
        crusts = [row[0] for row in crusts_cur.fetchall()]
        
        return {
            "sabores": pizzas,
            "tamanhos": sizes, 
            "bordas": crusts
        }

def get_ingredients(flavor: PizzaIngredients, db_path: str = "data/knowledge_base.db") -> list[str]:
    """Obtém os ingredientes de uma pizza específica."""
    with _get_connection(db_path) as con:
        cur = con.execute("SELECT ingredientes FROM pizzas WHERE sabor = ?", (flavor.flavor,))
        result = cur.fetchone()
        
        if result:
            ingredients = result[0].split(', ')
            return ingredients
        else:
            return []

def get_price(pizza_spec: PizzaSpec, db_path: str = "data/knowledge_base.db") -> float:
    """Busca por NOME → mapeia para IDs → lê preço da combinação exata em `precos`."""
    return get_price_by_ids(pizza_spec.flavor, pizza_spec.size, pizza_spec.crust, db_path)

def get_price_by_ids(pizza_id: int, tamanho_id: int, borda_id: int, db_path: str = "data/knowledge_base.db") -> float:
    """Busca DIRETO por IDs na tabela `precos`."""
    with _get_connection(db_path) as con:
        row = con.execute(
            """
            SELECT preco
            FROM precos
            WHERE pizza_id = ? AND tamanho_id = ? AND borda_id = ?;
            """,
            (pizza_id, tamanho_id, borda_id)
        ).fetchone()
        
        if not row:
            raise LookupError(
                f"Preço não cadastrado para combinação "
                f"(pizza_id={pizza_id}, tamanho_id={tamanho_id}, borda_id={borda_id})."
            )
        
        price = float(row[0])
        return price