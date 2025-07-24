from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from influxdb import InfluxDBClient
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from pytz import timezone, utc
import numpy as np
import pandas as pd

# Telegram Bot Token
BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# InfluxDB connections
client_captacion = InfluxDBClient(host='YOUR_INFLUXDB_HOST', port=8086, database='\2')
client_monitoreo = InfluxDBClient(host='YOUR_INFLUXDB_HOST', port=8086, database='\2')

# Timezone
QUITO_TZ = timezone('America/Guayaquil')

# Group ID for alerts
ALERT_GROUP_ID = YOUR_ALERT_GROUP_ID

# Custom keyboard
keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("📈 Graph"), KeyboardButton("📊 Status")],
     [KeyboardButton("⚡ Power"), KeyboardButton("💧 Levels")]],
    resize_keyboard=True
)

# Save last alert values and timestamps
last_alerts = {
    "embalse_280": {"value": None, "time": None},
    "embalse_560": {"value": None, "time": None},
    "generators": [None] * 8
}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🤖 *Bot de Monitoreo Activo*",
        reply_markup=keyboard,
        reply_to_message_id=None
    )

# /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
   # if update.effective_chat.id != ALERT_GROUP_ID:
    #    return

    ppm_main = client_captacion.query('SELECT LAST("value") FROM PPMS')
    ppm_desc = client_monitoreo.query('SELECT LAST("value") FROM ppmsdesc')
    ppm_emb = client_monitoreo.query('SELECT LAST("value") FROM ppmsemb')
    power_ccs = client_monitoreo.query('SELECT LAST("value") FROM potactot')

    reserv_ccs = client_monitoreo.query('SELECT LAST("value") FROM NivelEmbalse1')
    reserv_ccs = list(reserv_ccs.get_points())[0]['last']    
    tunel_ccs = client_monitoreo.query('SELECT LAST("value") FROM c_tunel')

    u_values = []
    for i in range(1, 9):
        result = client_monitoreo.query(f'SELECT LAST("value") FROM u{i}stat')
        value = list(result.get_points())[0]['last']
        u_values.append(value)

    ppm_main = list(ppm_main.get_points())[0]['last']
    ppm_desc = list(ppm_desc.get_points())[0]['last']
    ppm_emb = list(ppm_emb.get_points())[0]['last']
    power_ccs = list(power_ccs.get_points())[0]['last']

    
    tunel_ccs = list(tunel_ccs.get_points())[0]['last']

    now_quito = datetime.now(QUITO_TZ)
    time_str = now_quito.strftime("%Y-%m-%d %H:%M:%S")
    text = (
        f"📊 *Información Operativa - CCS:*\n"
        f"🕒 {time_str} (Hora local)\n\n"
        f"🟢 Captación: {np.round(ppm_main)} ppm\n"
        f"🔵 Descarga: {np.round(ppm_desc)} ppm\n"
        f"🟠 Embalse: {np.round(ppm_emb)} ppm\n\n"
        f"⚡ Potencia: {np.round(power_ccs)} MW\n"
        f"🌊 Nivel EMC: {np.round(reserv_ccs)} msnm\n"
        f"🔸 Túnel: {np.round(tunel_ccs)} m3/s\n\n"
        f"⚙️ *Generadores:*\n"
    )

    for i, val in enumerate(u_values, 1):
        icon = "🔴" if val == 1 else "🟢"
        text += f"{icon} Unidad {i}   "
        if i % 2 == 0:
            text += "\n"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode='Markdown',
        reply_to_message_id=None
    )

# /Power Units and energy
async def power(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #if update.effective_chat.id != ALERT_GROUP_ID:
     #   return
    p_values = []
    for i in range(1, 9):
        result = client_monitoreo.query(f'SELECT LAST("value") FROM U{i}_PAct')
        value = list(result.get_points())[0]['last']
        p_values.append(value)

    power_ccs = client_monitoreo.query('SELECT LAST("value") FROM potactot')
    power_ccs = list(power_ccs.get_points())[0]['last']

    reserv_ccs = client_monitoreo.query('SELECT LAST("value") FROM NivelEmbalse1')
    reserv_ccs = list(reserv_ccs.get_points())[0]['last']

    now_quito = datetime.now(QUITO_TZ)
    time_str = now_quito.strftime("%Y-%m-%d %H:%M:%S")
    text = (
        f"📊 *Potencia Activa - CCS:*\n"
        f"🕒 {time_str} (Hora local)\n\n"
        f"⚡ Planta: {np.round(power_ccs)} MW\n"
        f"🌊 Embalse: {np.round(0.9642*(reserv_ccs-1216)*(reserv_ccs-1216)+86.138*(reserv_ccs-1216))} MWh\n\n"
        f"⚙️ *Generadores:*\n"
    )

    for i, val in enumerate(p_values, 1):
        estado = " ❌" if val == 0 else ""
        text += f"• U{i}: {val:.2f} MW{estado}\n"


    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode='Markdown',
        reply_to_message_id=None
    )


# /Water Level
async def water(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #if update.effective_chat.id != ALERT_GROUP_ID:
     #   return

    reserv_ccs = client_monitoreo.query('SELECT LAST("value") FROM NivelEmbalse1')
    reserv_ccs = list(reserv_ccs.get_points())[0]['last']
    desc_ccs = client_monitoreo.query('SELECT LAST("value") FROM NivelDescarga')
    desc_ccs = list(desc_ccs.get_points())[0]['last']
    river_ccs = client_captacion.query('SELECT LAST("value") FROM nivelrio1')
    river_ccs = list(river_ccs.get_points())[0]['last']
    cuenco_ccs = client_captacion.query('SELECT LAST("value") FROM nivelbocatoma1')
    cuenco_ccs = list(cuenco_ccs.get_points())[0]['last']

    now_quito = datetime.now(QUITO_TZ)
    time_str = now_quito.strftime("%Y-%m-%d %H:%M:%S")
    text = (
        f"📊 *Niveles de agua - CCS:*\n"
        f"🕒 {time_str} (Hora local)\n\n"
        f"🏞️ Río: {np.round(river_ccs)} msnm\n"
        f"🌀 Cuenco: {np.round(cuenco_ccs)} msnm\n"
        f"🌊 Embalse: {np.round(reserv_ccs)} msnm\n"
        f"💦 Descarga: {np.round(desc_ccs)} msnm\n\n"
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode='Markdown',
        reply_to_message_id=None
    )



# /graph (3 separate smoothed plots)
async def graph(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #if update.effective_chat.id != ALERT_GROUP_ID:
    #    return

    now = datetime.utcnow()
    start_time = now - timedelta(minutes=30)

    sources = [
        {
            "client": client_captacion,
            "measurement": "PPMS",
            "label": "Captación",
            "color": "lime",
            "filename": "plot_captacion.png"
        },
        {
            "client": client_monitoreo,
            "measurement": "ppmsdesc",
            "label": "Descarga",
            "color": "deepskyblue",
            "filename": "plot_descarga.png"
        },
        {
            "client": client_monitoreo,
            "measurement": "ppmsemb",
            "label": "Embalse",
            "color": "orange",
            "filename": "plot_embalse.png"
        }
    ]

    for src in sources:
        query = f"SELECT value, time FROM {src['measurement']} WHERE time > '{start_time.isoformat()}Z'"
        result = src["client"].query(query)
        points = list(result.get_points())

        if not points:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"No hay datos recientes para {src['label']}.",
                reply_to_message_id=None
            )
            continue

        times_utc = [datetime.strptime(p['time'], "%Y-%m-%dT%H:%M:%S.%fZ") for p in points]
        times = [utc.localize(t).astimezone(QUITO_TZ) for t in times_utc]
        values = [p['value'] for p in points]

        values_smoothed = pd.Series(values).rolling(window=10).mean().to_numpy()
        times_ds = times[::150]
        values_ds = values_smoothed[::150]

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 5), facecolor='black')

        ax.plot(times_ds, values_ds, color=src['color'], linewidth=2)
        ax.set_title(f"PPM - {src['label']}", fontsize=14, color='white')
        ax.set_ylabel("PPM", fontsize=12, color='gray')
        ax.grid(True, linestyle='--', alpha=0.3, color='gray')
        ax.tick_params(colors='lightgray')
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=QUITO_TZ))
        fig.autofmt_xdate()

        plt.tight_layout()
        plt.savefig(src['filename'], dpi=150, bbox_inches='tight')
        plt.close()

        with open(src['filename'], 'rb') as photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                #caption=f"{src['label']}",
                reply_to_message_id=None
            )

# Periodic check for alerts
async def check_embalse_thresholds(context: ContextTypes.DEFAULT_TYPE):
    result = client_captacion.query('SELECT LAST("value") FROM PPMS')
    points = list(result.get_points())
    if not points:
        return

    value = points[0]['last']
    now = datetime.now()

    def get_trend(key):
        last = last_alerts[key]
        if last["value"] is None:
            return ""
        return "↗️ aumentando" if value > last["value"] else "↘️ disminuyendo"

    if value > 1000 and value <= 1999:
        last = last_alerts["embalse_280"]
        if last["time"] is None or now - last["time"] > timedelta(hours=1):
            trend = get_trend("embalse_280")
            last_alerts["embalse_280"] = {"value": value, "time": now}
            last_alerts["embalse_560"] = {"value": value, "time": now}
            await context.bot.send_message(
                chat_id=ALERT_GROUP_ID,
                text=(
                    f"🚨 *ALERTA: Nivel alto de PPM en Captación*\n"
                    f"Valor actual: {value:.2f} ppm\n"
                    f"Umbral: 1000 ppm\n"
                    f"Tendencia: {trend}"
                ),
                parse_mode='Markdown',
                reply_to_message_id=None
            )

    if value > 2000:
        last = last_alerts["embalse_560"]
        if last["time"] is None or now - last["time"] > timedelta(hours=1):
            trend = get_trend("embalse_560")
            last_alerts["embalse_560"] = {"value": value, "time": now}
            last_alerts["embalse_280"] = {"value": value, "time": now}
            await context.bot.send_message(
                chat_id=ALERT_GROUP_ID,
                text=(
                    f"🔥 *ALERTA CRÍTICA: PPM en Captación excede el nivel crítico*\n"
                    f"Valor actual: {value:.2f} ppm\n"
                    f"Umbral: 2000 ppm\n"
                    f"Tendencia: {trend}"
                ),
                parse_mode='Markdown',
                reply_to_message_id=None
            )

    cambios = []
    for i in range(1, 9):
        result = client_monitoreo.query(f'SELECT LAST("value") FROM u{i}stat')
        val = list(result.get_points())[0]['last']
        prev = last_alerts["generators"][i - 1]
        if prev is not None and prev != val:
            estado = "🔴 GCB Cerrado" if val == 1 else "🟢 GCB Abierto"
            cambios.append(f"Unidad {i}: {estado}")
        last_alerts["generators"][i - 1] = val

    if cambios:
        mensaje = "⚙️ *Cambio en estado de Generadores:*\n" + "\n".join(cambios)
        await context.bot.send_message(
            chat_id=ALERT_GROUP_ID,
            text=mensaje,
            parse_mode='Markdown',
            reply_to_message_id=None
        )

# Keyboard handler
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #if update.effective_chat.id != ALERT_GROUP_ID:
    #    return
    text = update.message.text
    if text == "📈 Graph":
        await graph(update, context)
    if text == "📊 Status":
        await status(update, context)
    if text == "💧 Levels":
        await water(update, context)
    if text == "⚡ Power":
        await power(update, context)
    #elif text == "📈 Graph":
        #await graph(update, context)
    #else:
    #    await context.bot.send_message(
    #        chat_id=update.effective_chat.id,
    #        text="Por favor selecciona una opción válida del teclado.",
    #        reply_to_message_id=None
    #    )

# Run bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("graph", graph))
app.add_handler(CommandHandler("power", power))
app.add_handler(CommandHandler("water", water))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
app.job_queue.run_repeating(check_embalse_thresholds, interval=300)
app.run_polling()
