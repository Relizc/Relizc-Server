@echo off
java -Xms<RAM>M -Xmx<RAM>M -jar server.jar -o true
rmdir "plugins/Citizens" /s /q