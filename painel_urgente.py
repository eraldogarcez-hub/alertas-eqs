import requests
import time
from twilio.rest import Client

# Credenciais do seu painel Twilio
TWILIO_ACCOUNT_SID = 'AC53cc33ab67e7608f6d634db844df17bc'
TWILIO_AUTH_TOKEN = '8b356423d3899b691f5fa64637a25713'

# Configurações de envio do Sandbox
WHATSAPP_REMETENTE = 'whatsapp:+17372508034' 
WHATSAPP_DESTINATARIO = 'whatsapp:+5551993380687'

# Estados monitorados pela EQS Engenharia
ESTADOS_ALVO = ['PR', 'SC']
EVENTOS_CRITICOS = ['Vento Forte', 'Tempestade', 'Chuva Intensa', 'Granizo', 'Vendaval']

alertas_enviados = set()

# Configuração regional explícita para a Europa (Região IE1 da sua conta)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
client.region = 'ie1'

def enviar_alerta_whatsapp(mensagem):
    try:
        client.messages.create(
            body=mensagem,
            from_=WHATSAPP_REMETENTE,
            to=WHATSAPP_DESTINATARIO
        )
        print("Sucesso! Notificacao enviada para o WhatsApp.")
    except Exception as e:
        print(f"Aviso de Envio: {e}")

def monitorar_clima():
    print("Consultando alertas meteorologicos oficiais...")
    url_api = "https://radarmeteorologico.com.br"
    
    try:
        response = requests.get(url_api, timeout=15)
        if response.status_code == 200:
            dados = response.json()
            if isinstance(dados, list) and len(dados) > 0:
                for info in dados:
                    id_alerta = info.get('id')
                    if not id_alerta or id_alerta in alertas_enviados:
                        continue
                    
                    estados = info.get('uf', [])
                    if isinstance(estados, str): 
                        estados = [estados]
                    
                    if any(uf in ESTADOS_ALVO for uf in estados):
                        evento = info.get('titulo', info.get('evento', 'Alerta'))
                        if any(ev.lower() in evento.lower() for ev in EVENTOS_CRITICOS):
                            severidade = info.get('severidade', 'AVISO').upper()
                            inicio = info.get('inicio', 'Imediato')
                            fim = info.get('fim', 'Nao determinado')
                            descricao = info.get('riscos', info.get('descricao', 'Atencao as estruturas.'))
                            
                            mensagem_alerta = (
                                f"⚠️ ALERTA SEVERO - {', '.join(estados)}\n"
                                f"• Evento: {evento} ({severidade})\n"
                                f"• Inicio: {inicio}\n"
                                f"• Termino Previsto: {fim}\n\n"
                                f"📋 Detalhes: {descricao}\n\n"
                                f"⚡ Atencao com as torres e geradores."
                            )
                            enviar_alerta_whatsapp(mensagem_alerta)
                            alertas_enviados.add(id_alerta)
            else:
                print("Monitoramento rodando. Sem novas ocorrencias climaticas.")
        else:
            print("Monitoramento ativo. Aguardando dados da rede.")
    except Exception:
        print("Monitoramento ativo. Aguardando dados da rede.")

if __name__ == "__main__":
    print("Iniciando o sistema de contingencia...")
    enviar_alerta_whatsapp("🚀 Monitoramento de Clima NUVEM Ativo. Cobertura para PR e SC iniciada.")
    
    while True:
        monitorar_clima()
        time.sleep(900)
