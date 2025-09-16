import warnings
import os
import logging

from app.agent import agent

os.environ["TOKENIZERS_PARALLELISM"] = "false"

logging.getLogger().setLevel(logging.WARNING)
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")



def main():
    print("""
🍕 BEAUTY PIZZA — ATENDENTE VIRTUAL INTELIGENTE 🍕
=======================================================
✨ Bem-vindo! Posso ajudar você com:
📋 • Consultar nosso cardápio completo
🌱 • Encontrar opções especiais (sem lactose, veganas, etc.)
🎯 • Montar seu pedido personalizado
💰 • Calcular preços em tempo real
🚚 • Finalizar seu pedido com entrega
=======================================================
💬 Digite sua mensagem ou 'sair' para encerrar.
""")
    
    while True:
        try:
            user_input = input("Você: ")
            
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("Obrigado por escolher a Beauty Pizza! Até mais! 🍕")
                break
            
            response = agent.run(user_input, stream=False)
            
            # Debug detalhado
            print(f"[DEBUG] Tipo de response: {type(response)}")
            print(f"[DEBUG] Atributos do response: {dir(response)}")
            
            tool_called = False
            if hasattr(response, 'messages'):
                print(f"[DEBUG] Número de mensagens: {len(response.messages)}")
                for i, msg in enumerate(response.messages):
                    print(f"[DEBUG] Mensagem {i}: {type(msg)}")
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        tool_called = True
                        for tool_call in msg.tool_calls:
                            print(f"[DEBUG] Tool Call: {tool_call.function.name}")
                            if hasattr(tool_call.function, 'arguments'):
                                print(f"[DEBUG] Arguments: {tool_call.function.arguments}")
                    
                    if hasattr(msg, 'content') and msg.content:
                        print(f"[DEBUG] Message content: {msg.content}")
            
            if not tool_called:
                print("[DEBUG] NENHUMA FERRAMENTA FOI CHAMADA!")
            
            # Print the final response
            if hasattr(response, 'content') and response.content:
                print(f"Atendente: {response.content}\n")
            else:
                print("[DEBUG] No content in response")
                print(f"[DEBUG] Response object: {response}\n")
            
        except KeyboardInterrupt:
            print("\nObrigado por escolher a Beauty Pizza! Até mais! 🍕")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()