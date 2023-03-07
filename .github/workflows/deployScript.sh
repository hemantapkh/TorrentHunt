# Due to a bug in appleboy/ssh-action@master, some commands shows error and fails to execute.
# So, running a bash file instead of commands

echo $1 > /opt/TorrentHunt/TorrentHunt/src/config.json ; source /opt/TorrentHunt/venv/bin/activate && && cd /opt/TorrentHunt/TorrentHunt/ && pip3 install -r requirements.txt ; pm2 reload torrenthunt
