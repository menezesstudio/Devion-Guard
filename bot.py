import discord
from discord.ext import commands
import asyncio
import time
from datetime import timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1547347069918904401

# ==============================
# DEVION GUARD — ANTI-RAID
# ==============================


RAID_LIMITE = 5
RAID_JANELA = 10
TEMPO_PROTECAO = 60

entradas_recentes = []
modo_raid_ativo = False


async def ativar_modo_raid(guild):
    global modo_raid_ativo

    if modo_raid_ativo:
        return

    modo_raid_ativo = True

    print(f"[ANTI-RAID] Possível raid detectado em {guild.name}")

    for canal in guild.text_channels:
        try:
            await canal.set_permissions(
                guild.default_role,
                send_messages=False
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

    await asyncio.sleep(TEMPO_PROTECAO)

    for canal in guild.text_channels:
        try:
            await canal.set_permissions(
                guild.default_role,
                send_messages=None
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

    modo_raid_ativo = False

    print(f"[ANTI-RAID] Proteção encerrada em {guild.name}")

# ==============================
# DEVION GUARD — ANTI-NUKE
# ==============================

ACOES_PROTEGIDAS = {
    discord.AuditLogAction.channel_delete,
    discord.AuditLogAction.role_delete,
    discord.AuditLogAction.guild_update,
    discord.AuditLogAction.ban,
    discord.AuditLogAction.kick,
}

LIMITE_ACOES = 3
JANELA_ACOES = 10

acoes_recentes = {}


async def verificar_anti_nuke(guild, action):
    agora = time.time()

    if guild.id not in acoes_recentes:
        acoes_recentes[guild.id] = []

    acoes_recentes[guild.id].append(agora)

    limite = agora - JANELA_ACOES

    acoes_recentes[guild.id] = [
        tempo
        for tempo in acoes_recentes[guild.id]
        if tempo >= limite
    ]

    if len(acoes_recentes[guild.id]) >= LIMITE_ACOES:
        print(
            f"[ANTI-NUKE] Possível ataque detectado em {guild.name}"
        )

        try:
            await guild.edit(
                reason="Devion Guard — possível ataque Anti-Nuke"
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

        acoes_recentes[guild.id].clear()


@bot.event
async def on_audit_log_entry_create(entry):
    if entry.action not in ACOES_PROTEGIDAS:
        return

    guild = entry.guild

    if entry.user is None:
        return

    # Nunca proteger contra o próprio Devion Guard
    if entry.user.id == bot.user.id:
        return

    print(
        f"[ANTI-NUKE] Ação detectada: "
        f"{entry.action.name} por {entry.user}"
    )

    await verificar_anti_nuke(guild, entry.action)
# ==============================
# DEVION GUARD — ANTI-SPAM
# + ANTI-LINK / ANTI-INVITE
# ==============================

SPAM_LIMITE = 5
SPAM_JANELA = 30
SPAM_REPETIDO_LIMITE = 3
SPAM_REPETIDO_JANELA = 30
SPAM_PUNICAO = 60

BLOQUEAR_LINKS = True
BLOQUEAR_CONVITES = True

mensagens_recentes = {}
mensagens_repetidas = {}

LINKS_PERMITIDOS = [
    "youtube.com",
    "youtu.be",
    "discord.com",
    "discord.gg"
]


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    conteudo = message.content.lower().strip()
    usuario_id = message.author.id
    agora = time.time()

    # ==============================
    # ANTI-LINK / ANTI-INVITE
    # ==============================

    if BLOQUEAR_CONVITES and (
        "discord.gg/" in conteudo
        or "discord.com/invite/" in conteudo
    ):
        try:
            await message.delete()

            await message.channel.send(
                f"{message.author.mention}, convites de outros "
                "servidores não são permitidos.",
                delete_after=5
            )

            print(
                f"[ANTI-INVITE] Convite removido de "
                f"{message.author}"
            )

        except (discord.Forbidden, discord.HTTPException):
            pass

        return

    if BLOQUEAR_LINKS and (
        "http://" in conteudo
        or "https://" in conteudo
    ):
        link_permitido = any(
            site in conteudo
            for site in LINKS_PERMITIDOS
        )

        if not link_permitido:
            try:
                await message.delete()

                print(
                    f"[ANTI-LINK] Link removido de "
                    f"{message.author}"
                )

            except (discord.Forbidden, discord.HTTPException):
                pass

            return

    # ==============================
    # ANTI-SPAM — FLOOD
    # ==============================

    if usuario_id not in mensagens_recentes:
        mensagens_recentes[usuario_id] = []

    mensagens_recentes[usuario_id].append(agora)

    limite_spam = agora - SPAM_JANELA

    mensagens_recentes[usuario_id] = [
        tempo
        for tempo in mensagens_recentes[usuario_id]
        if tempo >= limite_spam
    ]

    flood_detectado = (
        len(mensagens_recentes[usuario_id]) >= SPAM_LIMITE
    )

    # ==============================
    # ANTI-SPAM — MENSAGENS REPETIDAS
    # ==============================

    if usuario_id not in mensagens_repetidas:
        mensagens_repetidas[usuario_id] = []

    mensagens_repetidas[usuario_id].append(
        (agora, conteudo)
    )

    limite_repetido = agora - SPAM_REPETIDO_JANELA

    mensagens_repetidas[usuario_id] = [
        (tempo, texto)
        for tempo, texto in mensagens_repetidas[usuario_id]
        if tempo >= limite_repetido
    ]

    repeticoes = sum(
        1
        for tempo, texto in mensagens_repetidas[usuario_id]
        if texto == conteudo and conteudo
    )

    spam_repetido_detectado = (
        repeticoes >= SPAM_REPETIDO_LIMITE
    )

    # ==============================
    # PUNIÇÃO
    # ==============================

    if flood_detectado or spam_repetido_detectado:

        # Administradores não são punidos
        if message.author.guild_permissions.administrator:

            print(
                f"[ANTI-SPAM] {message.author} é administrador. "
                "Punição ignorada."
            )

            mensagens_recentes[usuario_id].clear()
            mensagens_repetidas[usuario_id].clear()

        else:

            try:
                await message.author.timeout(
                    discord.utils.utcnow()
                    + timedelta(seconds=SPAM_PUNICAO),
                    reason="Devion Guard — Spam/Flood detectado"
                )

                print(
                    f"[ANTI-SPAM] {message.author} "
                    f"foi punido por spam."
                )

                mensagens_recentes[usuario_id].clear()
                mensagens_repetidas[usuario_id].clear()

            except discord.Forbidden:

                print(
                    f"[ANTI-SPAM] Não foi possível punir "
                    f"{message.author}: falta de permissão."
                )

            except discord.HTTPException:

                print(
                    f"[ANTI-SPAM] Erro ao punir "
                    f"{message.author}."
                )

    await bot.process_commands(message)
# ==============================
# DEVION GUARD — PROTEÇÃO
# DE CARGOS E CANAIS
# ==============================

PROTECAO_CANAIS = True
PROTECAO_CARGOS = True

LIMITE_EXCLUSOES = 2
JANELA_EXCLUSOES = 10

exclusoes_recentes = {}


@bot.event
async def on_guild_channel_delete(channel):
    if not PROTECAO_CANAIS:
        return

    guild = channel.guild

    print(
        f"[PROTEÇÃO] Canal excluído: "
        f"{channel.name} em {guild.name}"
    )

    try:
        async for entry in guild.audit_logs(
            limit=1,
            action=discord.AuditLogAction.channel_delete
        ):
            usuario = entry.user

            if usuario is None:
                return

            if usuario.id == bot.user.id:
                return

            agora = time.time()

            if usuario.id not in exclusoes_recentes:
                exclusoes_recentes[usuario.id] = []

            exclusoes_recentes[usuario.id].append(agora)

            limite = agora - JANELA_EXCLUSOES

            exclusoes_recentes[usuario.id] = [
                tempo
                for tempo in exclusoes_recentes[usuario.id]
                if tempo >= limite
            ]

            if len(exclusoes_recentes[usuario.id]) >= LIMITE_EXCLUSOES:
                try:
                    await guild.ban(
                        usuario,
                        reason="Devion Guard — exclusão em massa de canais"
                    )

                    print(
                        f"[PROTEÇÃO] {usuario} foi banido "
                        f"por excluir canais em massa."
                    )

                except (discord.Forbidden, discord.HTTPException):
                    pass

            return

    except (discord.Forbidden, discord.HTTPException):
        pass


@bot.event
async def on_guild_role_delete(role):
    if not PROTECAO_CARGOS:
        return

    guild = role.guild

    print(
        f"[PROTEÇÃO] Cargo excluído: "
        f"{role.name} em {guild.name}"
    )

    try:
        async for entry in guild.audit_logs(
            limit=1,
            action=discord.AuditLogAction.role_delete
        ):
            usuario = entry.user

            if usuario is None:
                return

            if usuario.id == bot.user.id:
                return

            agora = time.time()

            if usuario.id not in exclusoes_recentes:
                exclusoes_recentes[usuario.id] = []

            exclusoes_recentes[usuario.id].append(agora)

            limite = agora - JANELA_EXCLUSOES

            exclusoes_recentes[usuario.id] = [
                tempo
                for tempo in exclusoes_recentes[usuario.id]
                if tempo >= limite
            ]

            if len(exclusoes_recentes[usuario.id]) >= LIMITE_EXCLUSOES:
                try:
                    await guild.ban(
                        usuario,
                        reason="Devion Guard — exclusão em massa de cargos"
                    )

                    print(
                        f"[PROTEÇÃO] {usuario} foi banido "
                        f"por excluir cargos em massa."
                    )

                except (discord.Forbidden, discord.HTTPException):
                    pass

            return

    except (discord.Forbidden, discord.HTTPException):
        pass

@bot.event
async def on_member_remove(member):
    try:
        async for entry in member.guild.audit_logs(
            limit=1,
            action=discord.AuditLogAction.kick
        ):
            if entry.target.id == member.id:
                print(
                    f"[LOG] {member} foi expulso por {entry.user}"
                )
                return
    except (discord.Forbidden, discord.HTTPException):
        pass

    print(f"[LOG] Membro saiu: {member}")


@bot.event
async def on_member_ban(guild, user):
    print(
        f"[LOG] BAN: {user} foi banido de {guild.name}"
    )


@bot.event
async def on_member_unban(guild, user):
    print(
        f"[LOG] UNBAN: {user} foi desbanido de {guild.name}"
    )

# ==============================
# DEVION GUARD — WHITELIST
# ==============================

USUARIOS_AUTORIZADOS = set()
BOTS_AUTORIZADOS = set()


@bot.command()
@commands.has_permissions(administrator=True)
async def whitelist(ctx, membro: discord.Member):
    USUARIOS_AUTORIZADOS.add(membro.id)

    await ctx.send(
        f"✅ {membro.mention} foi adicionado à **Whitelist**."
    )

    print(
        f"[WHITELIST] {membro} foi autorizado."
    )


@bot.command()
@commands.has_permissions(administrator=True)
async def unwhitelist(ctx, membro: discord.Member):
    USUARIOS_AUTORIZADOS.discard(membro.id)
    BOTS_AUTORIZADOS.discard(membro.id)

    await ctx.send(
        f"✅ {membro.mention} foi removido da **Whitelist**."
    )

    print(
        f"[WHITELIST] {membro} foi removido da autorização."
    )


@bot.command()
@commands.has_permissions(administrator=True)
async def whitelistlista(ctx):
    if not USUARIOS_AUTORIZADOS:
        await ctx.send("📋 A Whitelist está vazia.")
        return

    lista = []

    for usuario_id in USUARIOS_AUTORIZADOS:
        membro = ctx.guild.get_member(usuario_id)

        if membro:
            lista.append(f"• {membro.mention}")

    if not lista:
        await ctx.send("📋 A Whitelist está vazia.")
        return

    await ctx.send(
        "📋 **Whitelist do servidor:**\n\n"
        + "\n".join(lista)
    )

# ==============================
# DEVION GUARD — ENTRADA DE MEMBROS
# ANTI-BOT + ANTI-RAID
# ==============================

@bot.event
async def on_member_join(member):

    # ==============================
    # ANTI-BOT
    # ==============================

    if member.bot:
        if member.id in BOTS_AUTORIZADOS:
            print(f"[ANTI-BOT] Bot autorizado: {member}")
            return

        print(f"[ANTI-BOT] Bot não autorizado: {member}")

        try:
            await member.kick(
                reason="Bot não autorizado pelo Devion Guard"
            )

            print(f"[ANTI-BOT] Bot removido: {member}")

        except discord.Forbidden:
            print(
                f"[ANTI-BOT] Não foi possível remover {member}: "
                "falta de permissão."
            )

        except discord.HTTPException:
            print(
                f"[ANTI-BOT] Erro ao tentar remover {member}."
            )

        return

    # ==============================
    # ANTI-RAID
    # ==============================

    agora = time.time()

    entradas_recentes.append(agora)

    limite = agora - RAID_JANELA

    while entradas_recentes and entradas_recentes[0] < limite:
        entradas_recentes.pop(0)

    if len(entradas_recentes) >= RAID_LIMITE:
        asyncio.create_task(
            ativar_modo_raid(member.guild)
        )

        entradas_recentes.clear()

# ==============================
# DEVION GUARD — MODO EMERGÊNCIA
# ==============================

modo_emergencia = False


async def ativar_emergencia(guild):
    global modo_emergencia

    if modo_emergencia:
        return

    modo_emergencia = True

    print(f"[EMERGÊNCIA] Proteção máxima ativada em {guild.name}")

    for canal in guild.text_channels:
        try:
            await canal.set_permissions(
                guild.default_role,
                send_messages=False
            )
        except (discord.Forbidden, discord.HTTPException):
            pass


async def desativar_emergencia(guild):
    global modo_emergencia

    modo_emergencia = False

    for canal in guild.text_channels:
        try:
            await canal.set_permissions(
                guild.default_role,
                send_messages=None
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

    print(f"[EMERGÊNCIA] Proteção desativada em {guild.name}")


@bot.command()
@commands.has_permissions(administrator=True)
async def emergencia(ctx):
    await ativar_emergencia(ctx.guild)

    await ctx.send(
        "🚨 **MODO EMERGÊNCIA ATIVADO**\n"
        "O servidor foi colocado em modo de proteção."
    )


@bot.command()
@commands.has_permissions(administrator=True)
async def emergenciaoff(ctx):
    await desativar_emergencia(ctx.guild)

    await ctx.send(
        "✅ **MODO EMERGÊNCIA DESATIVADO**\n"
        "A proteção de emergência foi encerrada."
    )

@bot.event
async def on_ready():
    print(f"Devion Guard conectado como {bot.user}")

import os

bot.run(os.getenv("DISCORD_TOKEN"))
