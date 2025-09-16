from enum import IntEnum, Enum
from pydantic import BaseModel, Field

class Flavor(IntEnum):
    MARGHERITA          = 1
    PEPPERONI           = 2
    QUATRO_QUEIJOS      = 3
    CALABRESA           = 4
    FRANGO_COM_CATUPIRY = 5
    DOCE_DE_LEITE_COCO  = 6

class PizzaFlavor(str, Enum):
    """Enum com todos os sabores de pizza disponíveis."""
    MARGHERITA = "Margherita"
    PEPPERONI = "Pepperoni"
    QUATRO_QUEIJOS = "Quatro Queijos"
    CALABRESA = "Calabresa"
    FRANGO_CATUPIRY = "Frango com Catupiry"
    DOCE_LEITE_COCO = "Doce de Leite com Coco"


class Size(IntEnum):
    PEQUENA = 1
    MEDIA   = 2
    GRANDE  = 3


class Crust(IntEnum):
    SEM_BORDA  = 1
    CHEDDAR    = 2
    CATUPIRY   = 3

class PizzaSpec(BaseModel):
    flavor: Flavor = Field( description="Sabor da pizza, escolha um valor da enum Flavor")
    size: Size = Field(description="Tamanho da pizza, escolha um valor da enum Size")
    crust: Crust = Field(description="Tipo de borda, escolha um valor da enum Crust")


class PizzaIngredients(BaseModel):
    """Modelo para representar os ingredientes de uma pizza."""
    flavor: PizzaFlavor = Field(description="Sabor da pizza")