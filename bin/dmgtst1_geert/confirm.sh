# History info
VERSION="01.01"
#     01.01      janssensl    cleanup earsdir
#  
echo "Vesion $VERSION"


LOGDATE=`date +%Y%m%d`
WAS_CELL=WasPrd2Network; export WAS_CELL
DEPLOY_BASEDIR=/home/gpante/DeployBaseDir; export DEPLOY_BASEDIR
MLEWSADMIN_BINDIR=/home/gpante/MLEwsadmin/bin

if [ -f /etc/sysconfig/mazda ]; then
	. /etc/sysconfig/mazda
fi

if [ "$HOSTNAME" = "dmgtst1.mle.mazdaeur.com" ]  ; then
    WAS_CELL=dmgtst1Cell01; export WAS_CELL
elif [ "$HOSTNAME" = "mwas1" ]  ; then
    WAS_CELL=mwas1Cell01; export WAS_CELL
fi

/opt/IBM/WebSphere/AppServer/bin/ws_ant.sh -f ${MLEWSADMIN_BINDIR}/autodeploy.py/automatedDeploy.xml confirm

