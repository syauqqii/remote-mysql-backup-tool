import os
import json
import argparse
import logging
import datetime
from time import gmtime, strftime
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient
import subprocess

LOG_FILENAME = 'logs/backup.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

parser = argparse.ArgumentParser(description="Remote MySQL backup script")
parser.add_argument("-nr", "--norestore", help="Don't restore in local mysql", action='store_true')
args = parser.parse_args()

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

config = load_config()
deletedays = config["config"]["deletedays"]
localuser = config["config"]["localuser"]
localpass = config["config"]["localpass"]
backups = config["backups"]

def setup_ssh_client():
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    return ssh

def perform_backup(ssh, backup):
    timestamp = strftime("%Y%m%d_%H%M%S", gmtime())
    filename = f"{backup['dbname']}_{timestamp}.sql.gz"
    dumpcmd = f"mysqldump -u {backup['dbuser']} -p{backup['dbpass']} {backup['dbname']} | gzip > {filename}"
    
    try:
        logging.info(f"Connecting to {backup['sshhost']}")
        ssh.connect(backup['sshhost'], username=backup['sshuser'], timeout=10)
    except paramiko.AuthenticationException:
        logging.error(f"Login failed on {backup['sshhost']}")
        return

    stdin, stdout, stderr = ssh.exec_command(dumpcmd)
    channel = stdout.channel
    logging.info(f"{filename} dump started")
    status = channel.recv_exit_status()
    logging.info(f"{filename} dump finished")

    scp = SCPClient(ssh.get_transport())
    curr_path = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(curr_path, "backups", backup['dbname'], strftime("%Y/%m", gmtime()))
    local_db_path = os.path.join(target_dir, filename)

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    logging.info(f"Downloading {filename}")
    scp.get(filename, local_db_path)
    logging.info(f"{filename} downloaded")

    removecmd = f"rm {filename}"
    stdin, stdout, stderr = ssh.exec_command(removecmd)
    channel = stdout.channel
    logging.info(f"{filename} remove started")
    status = channel.recv_exit_status()
    logging.info(f"{filename} remove finished")

    if not args.norestore:
        restore_backup(local_db_path, backup['dbname'])
    
    scp.close()
    ssh.close()

def restore_backup(local_db_path, dbname):
    import MySQLdb as db
    con = db.connect(user=localuser, passwd=localpass)
    cur = con.cursor()
    cur.execute(f'CREATE DATABASE IF NOT EXISTS {dbname}')
    logging.info(f"Database {dbname} created (if not existed)")

    restore_cmd = f"zcat {local_db_path} | mysql -u {localuser} -p{localpass} {dbname}"
    process = subprocess.Popen(restore_cmd, shell=True, stdout=subprocess.PIPE)
    process.wait()
    logging.info(f"{dbname} restored")

def delete_old_backups():
    curr_path = os.path.dirname(os.path.abspath(__file__))
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=deletedays)

    for backup in backups:
        target_dir = os.path.join(curr_path, "backups", backup['dbname'])
        for root, dirs, files in os.walk(target_dir):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                dir_date = datetime.datetime.strptime(dir_name, "%Y/%m")
                if dir_date < cutoff_date:
                    logging.info(f"Deleting old backup directory: {dir_path}")
                    subprocess.call(['rm', '-rf', dir_path])

def main():
    ssh = setup_ssh_client()
    logging.info("Backup script started")
    
    for backup in backups:
        perform_backup(ssh, backup)
    
    delete_old_backups()
    
    logging.info("Backup script finished")

if __name__ == "__main__":
    main()
