# 🛡️ Devion Guard — Documentação

> **Devion Guard • Segurança em primeiro lugar.**

## 📖 Sobre

O **Devion Guard** é um bot de segurança desenvolvido para proteger, monitorar e manter servidores Discord organizados.

## 🛡️ Sistemas de proteção

### Anti-Raid

Detecta uma quantidade elevada de entradas em um curto período de tempo e ativa temporariamente um modo de proteção.

### Anti-Bot

Bots não autorizados podem ser removidos automaticamente.

Bots autorizados podem ser adicionados à whitelist.

### Anti-Spam

Detecta comportamentos como:

- Flood de mensagens
- Mensagens repetidas
- Envio excessivo de mensagens

Quando o comportamento é identificado, o usuário pode receber uma punição temporária.

### Anti-Link

Bloqueia links não permitidos.

Alguns sites podem ser configurados como permitidos.

### Anti-Invite

Bloqueia convites para outros servidores Discord.

### Anti-Nuke

Monitora ações potencialmente destrutivas realizadas no servidor, incluindo:

- Exclusão de canais
- Exclusão de cargos
- Alterações no servidor
- Banimentos
- Expulsões

### Proteção contra exclusões em massa

Monitora exclusões rápidas de canais e cargos para identificar possíveis ações destrutivas.

## 🚨 Modo de emergência

Permite bloquear temporariamente o envio de mensagens nos canais de texto.

### Comandos

`!emergencia`

Ativa o modo de emergência.

`!emergenciaoff`

Desativa o modo de emergência.

## ✅ Whitelist

Permite autorizar usuários específicos.

### Comandos

`!whitelist`

Adiciona um usuário à whitelist.

`!unwhitelist`

Remove um usuário da whitelist.

`!whitelistlista`

Mostra os usuários autorizados.

## ⚙️ Tecnologias

- Python
- discord.py
- Discord API

## 🔐 Segurança

O token do bot deve ser armazenado como uma variável de ambiente.

**Nunca publique o token do Devion Guard no GitHub.**

## 📁 Estrutura

```text
Devion-Guard/
├── .gitignore
├── README.md
├── DOCUMENTACAO.md
├── bot.py
└── requirements.txt
