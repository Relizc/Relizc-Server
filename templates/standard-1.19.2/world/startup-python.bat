:start
@echo off
java -Xms<RAM>M -Xmx<RAM>M -jar server.jar -o false --nogui
rmdir "plugins/Citizens" /s /q