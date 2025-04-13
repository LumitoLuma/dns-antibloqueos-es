# DNS antibloqueos
Evita los bloqueos indiscriminados hacia páginas web legítimas desde los principales ISPs españoles.

## Pasos de instalación:
1. Crear un servidor con Linux en el que haya disponibles permisos root. Puede funcionar en Windows, pero aún no se ha probado.
2. Instalar Python 3 y su módulo "dns" (en muchos casos, python3-dns).
3. Comprobar que el puerto 53 está disponible (con netstat -tlupn).
4. Ejecutar main.py como root.
5. Apuntar los DNS del sistema al servidor de Linux.
6. A poder navegar por Internet.

## Nota importante:
Este proyecto está en un estado muy temprano, y puede estar plagado de errores. Por favor, abran una incidencia si encuentran cualquier problema.

## Agradecimientos:
ChatGPT (mayoría del código).
