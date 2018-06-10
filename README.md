# Server Backup

Script for creating backups and uploading to Dropbox.

## Dependencies

This script depends on:
* [Dropbox Uploader](https://github.com/andreafabrizi/Dropbox-Uploader)

Installation script:
```
git clone https://github.com/andreafabrizi/Dropbox-Uploader.git /opt/dropbox-uploader/
```

## Task Files

This script is using task files located in
SCRIPT_DIR/tasks/*.txt

Example of the task file:
```
@ENABLED=1
@TASK=ExampleTask
@PASSWORD=P4$$W0RD
@EXECBEFORE=/opt/script.sh
@EXECAFTER=/opt/cleanup.sh
@PATHS
/path/test/abc
/path/test/def
/etc/other/path
```

Description of fields:

* `@ENABLED` = **[0, 1]**: 1 - task enabled, 0 - disabled.
* `@TASK` = **string**: name of the task (only letters, numbers or underscores).
* `@PASSWORD` = **string**: backup archive password.
* `@EXECBEFORE` = **string**: command to execute before starting backup (optional).
* `@EXECAFTER` = **string**: command to execute after starting backup (optional).
* `@PATHS` = **array of strings**: after this line there should only be a list with paths to backup.

## Decryption

```
gpg -d FILENAME.tar.gpg > FILENAME.tar
```
