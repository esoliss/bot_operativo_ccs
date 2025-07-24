# 🤖 ppm-monitor-bot

Bot de monitoreo operativo desarrollado con Python y Telegram, orientado a la supervisión de parámetros críticos como concentración de PPM, potencia activa y niveles hidráulicos en una central hidroeléctrica.

## 🚀 Funcionalidades

- Reporte de **estado actual** de parámetros operativos (`/status`)
- Consulta de **potencia activa por unidad** y embalse (`/power`)
- Visualización de **niveles hidráulicos** en captación, embalse, túnel y descarga (`/water`)
- Gráficas de tendencia de concentración de PPM en diferentes puntos del sistema (`/graph`)
- **Alertas automáticas** por umbrales de PPM y cambios de estado en generadores
- Interfaz de botones personalizada en Telegram

## 🧰 Tecnologías utilizadas

- Python 3.10+
- `python-telegram-bot`
- `influxdb` (cliente para InfluxDB 1.x)
- `matplotlib`, `pandas`, `numpy`
- `pytz` para manejo de zonas horarias

## 🛠️ Configuración

1. **Clonar el repositorio**:

```bash
git clone https://github.com/tu_usuario/ppm-monitor-bot.git
cd ppm-monitor-bot
