# Server Backup

Script for creating backups and uploading to Dropbox.

## Task Files

This script is using task files located in
SCRIPT_DIR/tasks/*.txt

Example of the task file:
```
@ENABLED=1
@TASK=ExampleTask
@PASSWORD=P4$$W0RD
@PATHS
/path/test/abc
/path/test/def
/etc/other/path
```

Description of fields:

* `@ENABLED` = [0, 1]: 1 - task enabled, 0 - disabled.
* `@TASK` = string: name of the task (only letters, numbers or underscores).
* `@PASSWORD` = string: backup archive password.
* `@PATHS` = section: after this line there should only be a list with paths to backup.

## Decryption

```
gpg -d FILENAME.tar.gpg > FILENAME.tar
```
