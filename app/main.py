import warnings

from collections import deque
from app.agent import agent

warnings.filterwarnings("ignore")

WINDOW = 8  
chat_window = deque(maxlen=WINDOW)  
def render_transcript():
    if not chat_window:
        return ""
    lines = []
    for m in chat_window:
        role = "Cliente" if m["role"] == "user" else "Atendente"
        lines.append(f"{role}: {m['content']}")
    return "\n".join(lines)

def main():
    print("""
          

        ════════════════════════════════════  
        🍕 Olá! Sou seu atendente virtual da Beauty Pizza!

        Posso te ajudar a:
        ✅ Ver o cardápio completo
        ✅ Entender sobre algum ingrediente
        ✅ Contar um pouco sobre a história da pizza
        ✅ Calcular o preço total
        ✅ Fazer seu pedido 
        ✅ Organizar a entrega

        Digite sua mensagem ou 'sair' para encerrar.
        ════════════════════════════════════
    """)
    while True:
        try:
            user_input = input("Você: ").strip()
            if user_input.lower() in ("sair","exit","quit"):
                print("Até mais! 🍕"); break
            if user_input.lower() in ("limpar","clear","reset"):
                chat_window.clear(); print("Contexto limpo. 🧼"); continue

            chat_window.append({"role":"user","content":user_input})
            print('                            ')
            print('------------------')


            # 2) monta um único prompt com transcript curto + pergunta atual
            transcript = render_transcript()
            composed = (
                "CONVERSA ATÉ AQUI (use para manter continuidade):\n"
                + (transcript if transcript else "—")
                + "\n\nRESPOSTA PARA A ÚLTIMA MENSAGEM DO CLIENTE:"
            )

            # 3) chama o agente passando o composed (mantendo suas instructions originais)
            response = agent.run(composed, stream=False)
            assistant_text = getattr(response, "content", str(response)).strip()
            print(f"Atendente: {assistant_text}\n")

            # 4) guarda a fala do atendente
            chat_window.append({"role":"assistant","content":assistant_text})
            print('------------------')

        except KeyboardInterrupt:
            print("\nAté mais! 🍕"); break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()