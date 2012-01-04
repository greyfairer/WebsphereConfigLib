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

/opt/IBM/WebSphere/AppServer/bin/ws_ant.sh -f ${MLEWSADMIN_BINDIR}/autodeploy.py/automatedDeploy.xml $1

cd ${DEPLOY_BASEDIR}/DeployNow

for f in `ls *.xml.done`
do
    echo "Cleanup $f" 
    ear=`grep file $f | cut -d\> -f 2 | cut -d\< -f 1`
    echo "Moving $f to ${DEPLOY_BASEDIR}/archive"
    mv "$f" ${DEPLOY_BASEDIR}/archive
    echo "Deleting $ear"
    rm $ear
    eardir=`dirname $ear`
    rmdir $eardir
done

## generate Plugin !!!!!
if [ "$HOSTNAME" = "dmgacc1" ]  
then
   set -x 
  ${MLEWSADMIN_BINDIR}/MLEGenPluginCfg.sh ACCHTTP
  ${MLEWSADMIN_BINDIR}/MLEGenPluginCfg.sh ACCHTTPS
elif [ "$HOSTNAME" = "dmgprd2.mle.mazdaeur.com" ]  
then
  ${MLEWSADMIN_BINDIR}/MLEGenPluginCfg.sh PRDHTTP
  ${MLEWSADMIN_BINDIR}/MLEGenPluginCfg.sh PRDHTTPS
fi

