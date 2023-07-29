:start
@echo off
java -Xms2048M -Xmx2048M -jar server.jar -o true --nogui
rmdir "plugins/Citizens" /s /q