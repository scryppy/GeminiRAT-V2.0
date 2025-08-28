# GeminiRAT-V2.0
GeminiRAT by Whxami


GeminiC2 - Plataforma de Simulação de Ameaças (RAT)
Versão: 2.0 (Estável)



⚠️ Aviso Ético e Legal

Este projeto foi desenvolvido para fins estritamente educacionais, como parte de um Trabalho de Conclusão de Curso (TCC) em Cibersegurança. O objetivo é estudar, simular e compreender as táticas, técnicas e procedimentos (TTPs) utilizados por atores de ameaças em um ambiente de laboratório controlado.
A utilização desta ferramenta ou de qualquer um de seus componentes em sistemas ou redes sem consentimento explícito e por escrito do proprietário é ilegal e antiética. O autor não se responsabiliza pelo mau uso deste material. Use seu conhecimento para o bem, para construir defesas mais robustas (Blue Team) e para realizar testes de penetração autorizados (Red Team).





📖 Visão Geral do Projeto
O GeminiC2 é uma plataforma de simulação de ameaças do tipo RAT (Remote Access Trojan), desenvolvida em Python. O projeto evoluiu de um simples InfoStealer para uma ferramenta de Comando e Controle (C2) completa, com um agente multiplataforma (Windows e Linux) e uma interface de gerenciamento web interativa.
A plataforma permite que um operador (Red Team) execute uma variedade de ações de pós-exploração em um sistema comprometido, enquanto serve como um objeto de estudo valioso para equipes de defesa (Blue Team) aprenderem a detectar e mitigar esse tipo de ameaça.




✨ Funcionalidades Principais

A plataforma é dividida em um Servidor C2 com painel web e um Agente furtivo.
Painel de Controle (C2)
Gerenciamento de Múltiplos Agentes: Interface centralizada para visualizar e interagir com todos os agentes.
Status em Tempo Real: Monitoramento do status (Online/Offline) e do último "heartbeat" de cada agente.
Interface com Abas: Painel organizado para Comandos Interativos, Logs do Sistema, Keylogger e Descriptografia.
Fila de Tarefas Visual: Acompanhamento do status de cada comando enviado (Pendente, Executando, Concluído, Erro).
Logging de Operações: Registros detalhados de todas as ações do operador e de todos os eventos de sistema dos agentes.
Ferramenta de Recuperação Integrada: Módulo para descriptografar arquivos afetados pelo ransomware diretamente do painel.
Agente Multiplataforma (Windows & Linux)
Coleta de Dados:
Informações do Sistema: Coleta de hostname, usuário, SO, versão, privilégios e IPs (interno e público).
Credenciais: Extração de senhas salvas do Google Chrome.
Cookies: Captura de cookies de sessão de múltiplos navegadores.
Processos: Listagem dos processos em execução.
Pós-Exploração:
Shell Remoto: Execução de comandos arbitrários no terminal do alvo.
Transferência de Arquivos: Upload e Download de arquivos entre o C2 e o alvo.
Escaneamento de Rede: Mapeamento da rede interna em busca de outros hosts ativos.
Keylogger Interativo: Captura de teclas digitadas que pode ser ativada e desativada remotamente.
Captura de Tela: Screenshot da tela do usuário.
Ação de Impacto (Simulação):
Módulo de Ransomware: Criptografia de arquivos em um diretório específico com AES-256.
Nota de Resgate: Exibição de um pop-up na tela da vítima com uma mensagem customizável.
Descriptografia Remota: Capacidade de reverter a criptografia ao receber o comando e a chave correta.
Persistência e Evasão:
Auto-Instalação Furtiva: O agente se copia para um diretório discreto e se renomeia.
Persistência Multiplataforma: Uso de Chave de Registro (Windows) e Crontab (Linux) para sobreviver a reinicializações.
Técnicas Anti-Análise: Checagens básicas para detectar ambientes de sandbox/VM.
Comunicação Discreta: Uso de User-Agent falso e "jitter" no heartbeat para camuflar o tráfego de C2.
Limpeza de Rastros: Remoção da persistência e autodestruição do executável no sistema alvo.






🏗️ Estrutura do Projeto

GeminiC2/
  │
  ├── C2_Downloads/
  ├── C2_Keylogs/
  ├── C2_System_Logs/
  │
  ├── templates/
  │   └── index.html   │
  ├── agent.py
  ├── c2_server.py
  ├── decryptor.py
  ├── requirements.txt
  │
  ├── agents_db.json
  └── c2_operator_log.txt



🚀 Como Usar
1. Pré-requisitos
Python 3.x
Um túnel para expor seu servidor C2 à internet (ex: cloudflared ou ngrok).
2. Instalação
Clone o repositório e instale as dependências:
git clone [URL_DO_SEU_REPOSITORIO]
cd GeminiC2
pip install -r requirements.txt




3. Configuração
Servidor: O servidor está pronto para ser executado. Ele rodará por padrão na porta 8000.
Agente: Abra o arquivo agent.py e edite a variável SERVER_URL, substituindo o placeholder pela URL do seu túnel (ex: https://meu-tunel.trycloudflare.com).
4. Execução
Inicie o Servidor C2:
python c2_server.py


Inicie o Túnel: Em outro terminal, exponha a porta 8000.
cloudflared tunnel --url localhost:8000


Compile e Execute o Agente: Em uma máquina de teste (preferencialmente uma VM), compile e execute o agente.
# Exemplo de compilação com Nuitka para Windows
python -m nuitka --mingw64 --onefile --noconsole --enable-plugin=tk-inter -o AgenteDiscreto.exe agent.py


Acesse o Painel: Abra seu navegador e acesse http://127.0.0.1:8000. O novo agente deverá aparecer na lista.
🛡️ Perspectiva de Defesa (Blue Team)
Esta ferramenta, embora educacional, simula ameaças reais. A detecção de um agente como este se basearia em:
Análise de Tráfego de Rede: Identificação do padrão de beaconing (conexões periódicas e regulares) para a URL do C2, mesmo com jitter.
Análise de Endpoint (EDR): Um EDR moderno detectaria a cadeia de comportamentos suspeitos: um processo desconhecido (AgenteDiscreto.exe) que estabelece persistência (reg add, crontab), faz conexões de rede, captura teclas (pynput), acessa arquivos de navegadores e executa comandos shell.
Análise de Arquivos: Verificação de arquivos em locais de persistência comuns (%APPDATA%, ~/.config/) e análise de reputação de executáveis não assinados.
Este projeto é um trabalho em andamento. Novas funcionalidades e melhorias são continuamente exploradas com o objetivo de aprofundar o conhecimento em cibersegurança.
