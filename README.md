# GeminiRAT-V2.0  

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)  
![Status](https://img.shields.io/badge/Status-Estável-brightgreen)  
![License](https://img.shields.io/badge/License-Educacional-important)  
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey?logo=linux&logoColor=white)  

---


**GeminiRAT by Whxami**

---

## ⚠️ Aviso Ético e Legal
Este projeto foi desenvolvido **exclusivamente para fins educacionais**, como parte de um Trabalho de Conclusão de Curso (TCC) em Cibersegurança.  

O objetivo é **estudar, simular e compreender** as táticas, técnicas e procedimentos (TTPs) utilizados por atores de ameaças em um ambiente de **laboratório controlado**.  

➡️ **O uso deste software em sistemas ou redes sem consentimento explícito e por escrito do proprietário é ilegal e antiético.**  
O autor **não se responsabiliza** por mau uso. Utilize apenas para aprendizado, Blue Team (defesa) e Red Team (testes autorizados).

---

## 📖 Visão Geral do Projeto
O **GeminiC2** é uma plataforma de simulação de ameaças do tipo **RAT (Remote Access Trojan)**, desenvolvida em Python.  

- Evoluiu de um simples InfoStealer para uma **plataforma de Comando e Controle (C2)** completa.  
- Inclui **agente multiplataforma (Windows e Linux)** e **painel web interativo**.  
- Serve como recurso para Red Team praticar **pós-exploração** e para Blue Team aprender a **detectar e mitigar** essas ameaças.

---

## ✨ Funcionalidades Principais

### 🔹 Painel de Controle (C2)
- **Gerenciamento de múltiplos agentes**
- **Status em tempo real** (Online/Offline + heartbeat)
- **Interface com abas**: comandos, logs, keylogger, descriptografia
- **Fila de tarefas visual**: Pendente / Executando / Concluído / Erro
- **Logging detalhado** de operações
- **Ferramenta de recuperação**: descriptografar arquivos do ransomware pelo painel

### 🔹 Agente Multiplataforma (Windows & Linux)

**Coleta de Dados**
- Hostname, usuário, SO, versão, privilégios e IPs
- Credenciais salvas (ex.: Chrome)
- Cookies de sessão
- Processos em execução

**Pós-Exploração**
- Shell remoto
- Upload/Download de arquivos
- Escaneamento de rede interna
- Keylogger remoto
- Captura de tela

**Ações de Impacto (Simulação)**
- Módulo de ransomware (AES-256 em diretórios específicos)
- Exibição de **nota de resgate** personalizada
- **Descriptografia remota** com chave correta

**Persistência & Evasão**
- Auto-instalação furtiva e renomeação
- Persistência (Registro no Windows / Crontab no Linux)
- Checagem anti-sandbox/VM
- Comunicação discreta (User-Agent falso + jitter)
- Autodestruição e limpeza de rastros

---

## 🏗️ Estrutura do Projeto
```bash
GeminiC2/ 
│ 
├── C2_Downloads/  
├── C2_Keylogs/ 
├── C2_System_Logs/ 
│ 
├── templates/ 
│    └── panel.html 
│    │ 
│ 	 └── login.html
│ 
│ 
├── GeminiV2_2.py 
├── ServidorCNC2.0.py  
├── requirements.txt 
│ 
├── agents_db.json 
└── c2_operator_log.txt
