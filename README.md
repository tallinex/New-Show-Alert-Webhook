For Synology NAS:
Download the new_season_alert.py file and store in a convenient location e.g. /scripts/new_season_alerts/new_season_alert.py

Set up your webhook
For discord:
on your server, click the cog icon (edit channel) next to the channel you want the alert to be shown on.
click on Integrations on the left menu and then webhooks on the right pane
press New Webhook
give it a name (eg Coming Soon) and an avatar if desired
press save and then press Copy Webhook URL

Configure the script:
open the new_season_alert.py file and set the variables at the top
SONARR_URL = "http://your-nas-ip:8989"  # Your Sonarr URL
SONARR_API_KEY = "your_api_key_here"  # Get from Sonarr Settings > General
WEBHOOK_URL = "webhook url copied from previous section"  # Discord, Slack, or custom webhook
DAYS_AHEAD = 30  # Check for shows returning in next X days
REQUEST_TIMEOUT = 30  # Timeout in seconds for API requests


set up a scheduled task:
1: Control Panel --> Task Scheduler
2: Create -->Scheduled Task --> User Defined Script
3: General tab; Task Name - e.g. New Season Alert; User - root
4: Schedule; Repeate - Daily; Start Time - eg 17 : 00 (for 5pm)
5: Task Settings; user-defiend script - python3 /volume1/scripts/new_season_alerts/new_season_alert.py
6: Press ok to save

The task will run every day at the set time and 
