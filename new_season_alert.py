#!/usr/bin/env python3
"""
Sonarr Upcoming Shows Alert Script
Checks for monitored shows returning within 30 days and sends webhook notifications
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Set

# Configuration - UPDATE THESE VALUES
SONARR_URL = "http://your-nas-ip:8989"  # Your Sonarr URL
SONARR_API_KEY = "your_api_key_here"  # Get from Sonarr Settings > General
WEBHOOK_URL = "your_webhook_url_here"  # Discord, Slack, or custom webhook
DAYS_AHEAD = 30  # Check for shows returning in next X days
REQUEST_TIMEOUT = 30  # Timeout in seconds for API requests

# Alert tracking file - stores which shows have been alerted
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ALERT_LOG_FILE = os.path.join(SCRIPT_DIR, "sonarr_alerts_sent.txt")

def load_alerted_shows() -> Set[str]:
    """Load the set of shows that have already been alerted"""
    if not os.path.exists(ALERT_LOG_FILE):
        return set()
    
    try:
        with open(ALERT_LOG_FILE, 'r') as f:
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        print(f"Error loading alert log: {e}")
        return set()

def save_alerted_show(show_key: str):
    """Save a show to the alert log"""
    try:
        with open(ALERT_LOG_FILE, 'a') as f:
            f.write(f"{show_key}\n")
    except Exception as e:
        print(f"Error saving to alert log: {e}")

def get_sonarr_series() -> List[Dict]:
    """Fetch all series from Sonarr"""
    url = f"{SONARR_URL}/api/v3/series"
    headers = {"X-Api-Key": SONARR_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print(f"Error: Request timed out after {REQUEST_TIMEOUT} seconds")
        print(f"Try increasing REQUEST_TIMEOUT or check if Sonarr is responding slowly")
        return []
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Cannot connect to Sonarr at {SONARR_URL}")
        print(f"Check that Sonarr is running and the URL is correct")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching series from Sonarr: {e}")
        return []

def get_episodes_for_series(series_id: int) -> List[Dict]:
    """Fetch episodes for a specific series"""
    url = f"{SONARR_URL}/api/v3/episode?seriesId={series_id}"
    headers = {"X-Api-Key": SONARR_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching episodes for series {series_id}: {e}")
        return []

def check_upcoming_shows(series_list: List[Dict], alerted_shows: Set[str]) -> List[Dict]:
    """Check for NEW SEASONS starting within the specified days"""
    upcoming = []
    today = datetime.now()
    cutoff_date = today + timedelta(days=DAYS_AHEAD)
    
    for series in series_list:
        # Skip if show is not monitored
        if not series.get('monitored', False):
            continue
        
        # Check if series has a next airing date
        next_airing = series.get('nextAiring')
        if not next_airing:
            continue
        
        # Parse the next airing date
        try:
            airing_date = datetime.fromisoformat(next_airing.replace('Z', '+00:00'))
            airing_date = airing_date.replace(tzinfo=None)  # Remove timezone for comparison
            
            # Check if it's within our date range
            if today <= airing_date <= cutoff_date:
                # Fetch episodes to check if this is a season premiere
                episodes = get_episodes_for_series(series['id'])
                
                # Find the next episode that will air
                next_episode = None
                for ep in episodes:
                    if not ep.get('airDateUtc'):
                        continue
                    ep_date = datetime.fromisoformat(ep['airDateUtc'].replace('Z', '+00:00'))
                    ep_date = ep_date.replace(tzinfo=None)
                    
                    if ep_date >= today and not ep.get('hasFile', False):
                        next_episode = ep
                        break
                
                # Only include if it's episode 1 (season premiere)
                if next_episode and next_episode.get('episodeNumber') == 1:
                    season_num = next_episode.get('seasonNumber', 0)
                    show_key = f"{series.get('title')}|S{season_num}"
                    
                    # Skip if we've already alerted for this show/season
                    if show_key in alerted_shows:
                        continue
                    
                    days_until = (airing_date - today).days
                    
                    upcoming.append({
                        'title': series.get('title'),
                        'next_airing': airing_date.strftime('%A %d %B'),
                        'days_until': days_until,
                        'season': season_num,
                        'network': series.get('network', 'Unknown'),
                        'status': series.get('status', 'Unknown'),
                        'show_key': show_key,
                        'tmdbId': series.get('tmdbId','Unknown')
                    })
        except (ValueError, TypeError) as e:
            print(f"Error parsing date for {series.get('title')}: {e}")
            continue
    
    # Sort by days until airing
    upcoming.sort(key=lambda x: x['days_until'])
    return upcoming

def send_webhook_alert(show: Dict):
    """Send individual alert to webhook for a single show"""
    
    # Create message for single show
    days_text = "TODAY!" if show['days_until'] == 0 else f"in {show['days_until']} days"
    
    message = (
        f"**{show['title']}**\n"
        f"Season {show['season']} Starts on {show['next_airing']} \n"
        f"https://www.themoviedb.org/tv/{show['tmdbId']}/season/{show['season']}"
    )
    
    # Webhook payload (works with Discord, adapt for other services)
    payload = {
        "content": message,
        "username": "Coming Soon"
    }
    
    # For Slack, use this format instead:
    # payload = {
    #     "text": message
    # }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        print(f"Alert sent for: {show['title']} Season {show['season']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending webhook for {show['title']}: {e}")
        return False

def main():
    """Main execution function"""
    print(f"Checking Sonarr for NEW SEASONS starting within {DAYS_AHEAD} days...")
    
    # Load previously alerted shows
    alerted_shows = load_alerted_shows()
    print(f"Previously alerted shows: {len(alerted_shows)}")
    
    # Fetch all series
    series_list = get_sonarr_series()
    if not series_list:
        print("No series data retrieved from Sonarr.")
        return
    
    print(f"Found {len(series_list)} total series in Sonarr")
    
    # Check for upcoming season premieres
    upcoming_shows = check_upcoming_shows(series_list, alerted_shows)
    
    if upcoming_shows:
        print(f"Found {len(upcoming_shows)} new season(s) to alert:")
        
        # Send individual alert for each show
        for show in upcoming_shows:
            print(f"  - {show['title']} Season {show['season']} in {show['days_until']} days")
            
            # Send webhook alert
            if send_webhook_alert(show):
                # Mark this show/season as alerted
                save_alerted_show(show['show_key'])
            else:
                print(f"  Failed to send alert for {show['title']}")
    else:
        print("No new seasons starting within the specified timeframe (or all already alerted).")

if __name__ == "__main__":
    main()
