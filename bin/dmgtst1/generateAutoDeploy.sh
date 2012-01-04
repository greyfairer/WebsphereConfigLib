LOGDATE=`date +%Y%m%d`
WAS_CELL=WasPrd2Network; export WAS_CELL
DEPLOY_BASEDIR=/var/MLEwsadmin; export DEPLOY_BASEDIR

if [ -f /etc/sysconfig/mazda ]; then
	. /etc/sysconfig/mazda
fi

if [ "$HOSTNAME" = "dmgtst1.mle.mazdaeur.com" ]  ; then
    WAS_CELL=dmgtst1Cell01; export WAS_CELL
elif [ "$HOSTNAME" = "mwas1" ]  ; then
    WAS_CELL=mwas1Cell01; export WAS_CELL
fi

/opt/IBM/WebSphere/AppServer/bin/ws_ant.sh -f /usr/local/MLEwsadmin/bin/autodeploy.py/generateDeployXmls.xml $1

if [ "$HOSTNAME" = "mwas1" ]  ; then
    chmod 664      $DEPLOY_BASEDIR/DeployNow/*
    chgrp wasadmin $DEPLOY_BASEDIR/DeployNow/*
elif [ "$HOSTNAME" = "dmgtst1.mle.mazdaeur.com" ]  ; then
	chmod 664 $DEPLOY_BASEDIR/DeployNow/*
fi

