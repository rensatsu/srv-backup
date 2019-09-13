#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

#__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
__dir=/opt/scripts/backup-srv/

bash $__dir/../notifications/send.sh --title="Backup" --message="Backup started" --icon="fa-archive" --status="default"
python3 $__dir/backup.py

if [ "$?" -ne "0" ]; then
    bash $__dir/../notifications/send.sh --title="Backup" --message="Backup failed" --icon="fa-archive" --status="danger"
else
    bash $__dir/../notifications/send.sh --title="Backup" --message="Backup completed" --icon="fa-archive" --status="success"
fi
