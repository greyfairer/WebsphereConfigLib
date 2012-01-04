# History info
VERSION="01.01"
#     01.01      janssensl    cleanup earsdir
#  
echo "Vesion $VERSION"


LOGDATE=`date +%Y%m%d`
WAS_CELL=WasPrd2Network; export WAS_CELL

if [ -f /etc/sysconfig/mazda ]; then
	. /etc/sysconfig/mazda
fi

if [ "$HOSTNAME" = "dmgtst1.mle.mazdaeur.com" ]  ; then
    WAS_CELL=dmgtst1Cell01; export WAS_CELL
elif [ "$HOSTNAME" = "mwas1" ]  ; then
    WAS_CELL=mwas1Cell01; export WAS_CELL
fi

/opt/IBM/WebSphere/AppServer/bin/ws_ant.sh -f /usr/local/MLEwsadmin/bin/autodeploy.py/automatedDeploy.xml $1



cd /var/MLEwsadmin/DeployNow

for f in `ls *.xml.done`
do
    echo "Cleanup $f" 
    ear=`grep file $f | cut -d\> -f 2 | cut -d\< -f 1`
    echo "Moving $f to /var/MLEwsadmin/archive"
    mv "$f" /var/MLEwsadmin/archive
    echo "Deleting $ear"
    rm $ear
    eardir=`dirname $ear`
    rmdir $eardir
done

## generate Plugin !!!!!
if [ "$HOSTNAME" = "dmgacc1" ]  
then
   set -x 
  /usr/local/MLEwsadmin/bin/MLEGenPluginCfg.sh ACCHTTP
  /usr/local/MLEwsadmin/bin/MLEGenPluginCfg.sh ACCHTTPS
elif [ "$HOSTNAME" = "dmgprd2.mle.mazdaeur.com" ]  
then
  /usr/local/MLEwsadmin/bin/MLEGenPluginCfg.sh PRDHTTP
  /usr/local/MLEwsadmin/bin/MLEGenPluginCfg.sh PRDHTTPS
fi

