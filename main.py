import os
import time
import logging
import subprocess
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Print to console only
    ]
)
logger = logging.getLogger(__name__)

def get_current_ip():
    """Get current IP using ip4.me API"""
    try:
        logger.info("Fetching current IP address...")
        result = subprocess.run(['curl', '-s', 'ip4.me/api/'], 
                              capture_output=True, text=True, check=True)
        # Split the response and get the IP address (second element)
        ip = result.stdout.strip().split(',')[1].strip()
        logger.info(f"Current IP: {ip}")
        return ip
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting current IP: {e}")
        return None
    except IndexError as e:
        logger.error(f"Unexpected API response format: {result.stdout}")
        return None

def read_last_ip():
    """Read the last IP from last.ip file"""
    try:
        with open('last.ip', 'r') as f:
            for line in f:
                if line.startswith('last_ip='):
                    ip = line.split('=')[1].strip()
                    logger.debug(f"Last known IP: {ip}")
                    return ip
    except FileNotFoundError:
        logger.warning("last.ip file not found")
        return None
    return None

def write_last_ip(ip):
    """Write the current IP to last.ip file"""
    try:
        with open('last.ip', 'w') as f:
            f.write(f'last_ip={ip}\n')
        logger.info(f"Updated last.ip with: {ip}")
    except Exception as e:
        logger.error(f"Failed to write to last.ip: {e}")

def update_mam_seedbox(cookie_file, mam_id=None):
    """Update MAM seedbox information"""
    try:
        if mam_id:
            logger.info("Performing initial MAM seedbox setup...")
            cmd = ['curl', '-s', 
                  '-b', 'mam_id=' + mam_id,
                  '-c', cookie_file, 
                  'https://t.myanonamouse.net/json/dynamicSeedbox.php']
        else:
            logger.info("Updating MAM seedbox with existing cookies...")
            cmd = ['curl', '-s', 
                  '-b', cookie_file, 
                  '-c', cookie_file, 
                  'https://t.myanonamouse.net/json/dynamicSeedbox.php']
        
        logger.debug(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse JSON response
        response = json.loads(result.stdout)
        
        # Write raw response to file
        with open('/config/mam.output', 'w') as f:
            f.write(result.stdout)

        # Check for success
        if not response.get('Success', False):
            error_msg = response.get('msg', 'Unknown error')
            logger.error(f"MAM API Error: {error_msg}")
            logger.info("Shutting down container due to API error...")
            sys.exit(1)
            
        logger.info("Successfully updated MAM seedbox")
        logger.debug(f"MAM response: {result.stdout}")
            
        return True
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse MAM API response: {result.stdout}")
        logger.info("Shutting down container due to invalid API response...")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error updating MAM seedbox: {e}")
        if e.stderr:
            logger.error(f"Error output: {e.stderr}")
        logger.info("Shutting down container due to curl error...")
        sys.exit(1)
    return False

def check_cookie_file(cookie_file):
    """Check if cookie file contains valid session"""
    try:
        with open(cookie_file, 'r') as f:
            content = f.read()
            return 'mam_id' in content
    except:
        return False

def main():
    logger.info("Starting MAM Dynamic API service")
    load_dotenv()
    mam_id = os.getenv('MAM_ID')
    
    if not mam_id:
        logger.error("MAM_ID environment variable is not set")
        return

    cookie_file = '/config/mam.cookies'
    logger.info(f"Using cookie file: {cookie_file}")

    # Check if cookie file exists and contains valid session
    if not check_cookie_file(cookie_file):
        logger.info("No valid session found, performing initial setup...")
        if not update_mam_seedbox(cookie_file, mam_id):
            logger.error("Failed to perform initial setup")
            return

    logger.info(f"Starting monitoring loop with MAM_ID: {mam_id}")
    
    while True:
        try:
            current_ip = get_current_ip()
            last_ip = read_last_ip()

            if current_ip and current_ip != last_ip:
                logger.info(f"IP change detected: {last_ip} -> {current_ip}")
                if update_mam_seedbox(cookie_file):
                    write_last_ip(current_ip)
                    logger.info("Successfully updated MAM seedbox with new IP")
                else:
                    logger.error("Failed to update MAM seedbox")
            else:
                logger.info("No IP change detected")
            
            logger.info("Waiting 60 minutes before next check...")
            time.sleep(60 * 60)
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
            time.sleep(60)  # Wait a minute before retrying on error

if __name__ == "__main__":
    main() 