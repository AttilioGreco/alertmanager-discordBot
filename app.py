from flask import Flask, request, jsonify
from logging.config import dictConfig
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
import json
import os
import sys

try:
    log_level = os.environ["LOG_LEVEL"]
except KeyError:
    log_level = 'INFO'

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': log_level,
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

app.logger.info(f"Log level is set to {log_level}")
try:
    discord_webhook = os.environ["DISCORD_WEBHOOK"]
    app.logger.info(f"Discord WebHook url is configured to {log_level}")
except KeyError:
    app.logger.fatal(f"Discord WebHook is not configured")
    sys.exit(1)

@app.route("/status")
def status():
    app.logger.debug(f"app is ok")
    status = {'status': 'ok'}
    return status


@app.route("/alert-to-discord", methods=['POST'])
def alert_to_discord():
    status = {'status': 'ok'}
    alert_manager_in = request.json
    app.logger.info(f"data from post:\n#######################################\n {alert_manager_in}\n###############################################\n")

    webhook = DiscordWebhook(url=discord_webhook)
    app.logger.debug(f"discord weebhook: {discord_webhook}")
    # app.logger.debug(f"Data from post: {alert_manager_in}")
    # print(alert_manager_in)
    if alert_manager_in['status'] == 'firing':
        app.logger.debug(f"Alert Gobal Status is firing")
        embed = DiscordEmbed(title='Status: FIRING 🔥', color=16711680)
        app.logger.debug(f"common labels")
    elif alert_manager_in['status'] == 'resolved':
        embed = DiscordEmbed(title='Status: RESOLVED', color=6729778)
        app.logger.debug(f"Alert Gobal Status is resolved")
    else:
        app.logger.warning(f"Status is Unknown")
        for key,value in alert_manager_in["commonLabels"].items():
            embed.add_embed_field(name=key, value=value, inline=False)
        embed = DiscordEmbed(title='Status: Unknown', color=10494192)

    for key,value in alert_manager_in["commonLabels"].items():
        app.logger.debug(f"{key}: {value}")
        embed.add_embed_field(name=key, value=value, inline=False)
    
    webhook.add_embed(embed)
    # for each aler creare new message
    index = 0
    for alert in alert_manager_in["alerts"]:
        app.logger.debug(f"START ALERT CREATIONS number {index}")
        webhook.add_embed(alertItems(alert))
        app.logger.debug(f"END FUNC RETURN")
        index = index + 1
    response = webhook.execute()
    return status

def alertItems(alert):
    # Create new object
    discordList = DiscordEmbed()

    # Configure title with alertname

    discordList.set_title(alert['labels']['alert_name'])
    app.logger.debug(f"Set title to: {alert['labels']['alert_name']}")
    # remove alert from labels or will repit
    app.logger.debug(f"Remove Title from labels")
    alert['labels'].pop('alert_name', None)

    # Set alert Coloro base on severity
    if alert['labels']['severity'] == 'critical':
        app.logger.debug(f"Alert Severity is critical, set color to Red")
        discordList.set_color(16656146)
    elif alert['labels']['severity'] == 'warning':
        app.logger.debug(f"Alert Severity is critical, set color to Yellow")
        discordList.set_color(16703232)
    elif alert['labels']['severity'] == 'info':
        app.logger.debug(f"Alert Severity is critical, set color to Blue")
        discordList.set_color(2061822)
    else:
        app.logger.warning(f"Alert Severity is Not critical, warning, info, then is not mamaged set color to Violet")
        discordList.set_color(10494192)
    # add each labels to fields
    app.logger.debug(f"Labels")
    for label, value in alert['labels'].items():
        app.logger.debug(f"{label}: {value}")
        discordList.add_embed_field(name=label, value=value, inline=False)
    # add annotations to fields
    app.logger.debug(f"Annotations")
    for annotation, value in alert['annotations'].items():
        app.logger.debug(f"{annotation}: {value}")
        discordList.add_embed_field(name=label, value=value, inline=False)
    # set timestamp to message
    app.logger.debug(f"Data start at: {alert['startsAt']}")
    discordList.add_embed_field(name='startsAt', value=alert['startsAt'], inline=False)
    app.logger.debug(f"Data ends at: {alert['endsAt']}")
    discordList.add_embed_field(name='endsAt', value=alert['endsAt'], inline=False)
    # return final message
    return discordList


if __name__ == "__main__":
    app.run(debug=True)
