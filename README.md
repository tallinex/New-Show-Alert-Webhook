<img width="586" height="291" alt="image" src="https://github.com/user-attachments/assets/c5bb14a9-35a3-4094-9d42-51ece144b7ff" />
<h1>New Season Alert</h1>
<h3>Send a one time alert to your discord server channel when a new season of a show you are monitoring in Sonarr has a new season coming soon.</h3>


<h2>For Synology NAS:</h2>
Download the new_season_alert.py file and store in a convenient location e.g. /scripts/new_season_alerts/new_season_alert.py<br>

<h2>Set up your webhook</h2><br>
<b>For discord:</b><br>
on your server, click the cog icon (edit channel) next to the channel you want the alert to be shown on.<br>
click on Integrations on the left menu and then webhooks on the right pane<br>
press New Webhook<br>
give it a name (eg Coming Soon) and an avatar if desired<br>
press save and then press Copy Webhook URL<br>
<img width="1044" height="558" alt="image" src="https://github.com/user-attachments/assets/ae031376-90b6-4a81-865f-cf3a16eee5a0" />

<h2>Configure the script:</h2><br>
open the new_season_alert.py file and set the variables at the top<br>
SONARR_URL = "http://your-nas-ip:8989"  # Your Sonarr URL<br>
SONARR_API_KEY = "your_api_key_here"  # Get from Sonarr Settings > General<br>
WEBHOOK_URL = "webhook url copied from previous section"  # Discord, Slack, or custom webhook<br>
DAYS_AHEAD = 30  # Check for shows returning in next X days<br>
REQUEST_TIMEOUT = 30  # Timeout in seconds for API requests<br>


<h2>set up a scheduled task:</h2><br>
1: Control Panel --> Task Scheduler<br>
2: Create -->Scheduled Task --> User Defined Script<br>
3: General tab; Task Name - e.g. New Season Alert; User - root<br>
4: Schedule; Repeate - Daily; Start Time - eg 17 : 00 (for 5pm)<br>
5: Task Settings; user-defiend script - python3 /volume1/scripts/new_season_alerts/new_season_alert.py<br>
6: Press ok to save<br>

The task will run every day at the set time and push an alert to your discord webhook
<img width="586" height="291" alt="image" src="https://github.com/user-attachments/assets/c5bb14a9-35a3-4094-9d42-51ece144b7ff" />
