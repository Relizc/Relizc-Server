:start
@echo off
java -Xms<RAM>M -Xmx<RAM>M -jar server.jar -o false
rmdir "plugins/Citizens" /s /q