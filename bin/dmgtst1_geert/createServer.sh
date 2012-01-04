LOGDATE=`date +%Y%m%d`
WAS_CELL=WasPrd2Network; export WAS_CELL

if [ -f /etc/sysconfig/mazda ]; then
	. /etc/sysconfig/mazda
fi

if [ "$HOSTNAME" = "dmgtst1.mle.mazdaeur.com" ]  ; then
    WAS_CELL=dmgtst1Cell01; export WAS_CELL
fi

/opt/IBM/WebSphere/AppServer/bin/ws_ant.sh -DconfigFile=$(readlink -f $1) -f /usr/local/MLEwsadmin/bin/createServer.py/createServer.xml $2

