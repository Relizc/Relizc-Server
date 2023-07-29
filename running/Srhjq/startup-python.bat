:start
@echo off
java -Xms256M -Xmx256M -jar server.jar -o false
rmdir "plugins/Citizens" /s /q