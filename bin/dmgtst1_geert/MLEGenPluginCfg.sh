#!/bin/sh

# merge ACC plugin-cfg.xml files
# login into dmgacc1 -> main plugin-cfg.xml
# get others from dmgacc2 : /opt/Websphere and dmgportalsrv C:\Program Files\IBM\Websphere
# merge in 2 steps using xsltproc

# Add webservers defined in WAS6 deployment manager and corresponding node names in these functions
set -x
SSH=ssh
LOGDATE=`date +%Y%m%d`
BASE=/usr/local/MLEwsadmin/bin/mergePluginCfg

WEBSERVERCLASSES=2

function usage {
echo "usage - $0  <type>"
echo ""
echo "type must be :  TSTHTTPS, ACCHTTP, ACCHTTPS, PRDHTTP, PRDHTTPS" 
echo ""

exit
}

CLASS=$1

case $CLASS in 
	TSTHTTPS)  NODE="mappstmp.mazdaeur.com"
                  WEBSERVER="webtstdmz1"
                  SERVERS="webtstdmz1.mazdaeur.com"
                  CELL=dmgtst1Cell01
                  ;;
	ACCHTTP)  NODE="mappsacc.mle.mazdauer.com"
                  WEBSERVER="webacc1"
                  SERVERS="webacc1.mle.mazdaeur.com"
                  CELL=dmgacc1Network
                  ;;
        ACCHTTPS) NODE="mappsacc.mazdaeur.com"
                  WEBSERVER="webaccdmz1"
                  SERVERS="webaccdmz1.mazdaeur.com webaccdmz2.mazdaeur.com webaccdmz3.mazdaeur.com"
                  CELL=dmgacc1Network
                  ;;
	PRDHTTP)  NODE="mapps.willebroek.mazdaeurope.com"
                  WEBSERVER="webprdford1"
                  SERVERS="webprdford1.mazdaeur.com webprdford2.mazdaeur.com"
                  CELL=WasPrd2Network
                  ;;
        PRDHTTPS) NODE="mapps.mazdaeur.com"
                  WEBSERVER="webprddmz1"
                  SERVERS="webprddmz1.mazdaeur.com webprddmz2.mazdaeur.com webprddmz3.mazdaeur.com"
                  CELL=WasPrd2Network
                  ;;
        default)  echo "wrong classname"
                  usage
                  ;;
esac



  # WAS5 (epc3) plugin now static
  cp /usr/local/MLEwsadmin/conf/${NODE}/plugin-epc3-${CLASS}-fixed.xml /tmp/plugin-WAS5.xml

  # Portal plugin now static
  cp /usr/local/MLEwsadmin/conf/${NODE}/plugin-portal-${CLASS}-fixed.xml /tmp/plugin-portal.xml


  /opt/IBM/WebSphere/AppServer/bin/GenPluginCfg.sh  -node.name $NODE -webserver.name $WEBSERVER
  cp /opt/IBM/WebSphere/AppServer/profiles/Dmgr01/config/cells/${CELL}/nodes/$NODE/servers/$WEBSERVER/plugin-cfg.xml /tmp/plugin-WAS6-$CLASS.xml
  
  echo "Fixing WAS6 URL mappings"
  xsltproc -o /tmp/plugin-WAS6-$CLASS.xml.fixed ${BASE}/filterPluginCfg-$CLASS.xslt /tmp/plugin-WAS6-$CLASS.xml
  cp -f /tmp/plugin-WAS6-$CLASS.xml.fixed /tmp/plugin-WAS6-$CLASS.xml

  echo "Merging WAS6 plugin with WAS5 plugin"

  if [ -f /tmp/result1.xml ]; then
      rm -f /tmp/result1.xml
  fi

  xsltproc -o /tmp/result1.xml --stringparam mergeFileName /tmp/plugin-WAS5.xml ${BASE}/mergePluginCfg.xslt /tmp/plugin-WAS6-$CLASS.xml

  echo "Merging WAS6 and WAS5 plugins with Portal plugin"
# xsltproc -o /usr/local/MLEwsadmin/conf/plugin-cfg-$CLASS.xml --stringparam mergeFileName /tmp/plugin-portal.xml ${BASE}/mergePluginCfg.xslt /tmp/result1.xml
  if [ -f /tmp/result2.xml ]; then
      rm -f /tmp/result2.xml
  fi
  xsltproc -o /tmp/result2.xml --stringparam mergeFileName /tmp/plugin-portal.xml ${BASE}/mergePluginCfg.xslt /tmp/result1.xml

  echo "Sorting generated result"
  xsltproc -o /usr/local/MLEwsadmin/conf/plugin-cfg-$CLASS.xml ${BASE}/sortPluginCfg.xslt /tmp/result2.xml

  echo "Resulting plugin written to /usr/local/MLEwsadmin/conf/${NODE}/plugin-cfg-$CLASS.xml.$LOGDATE"
  mv  /usr/local/MLEwsadmin/conf/plugin-cfg-$CLASS.xml  /usr/local/MLEwsadmin/conf/${NODE}/plugin-cfg-$CLASS.xml.$LOGDATE 

rm -f /tmp/plugin-WAS6-*.xml /tmp/plugin-WAS5.xml /tmp/plugin-portal.xml /tmp/result1.xml /tmp/result2.xml



exit    



  # distribute correct plugin-cfg.xml to all webservers belonging to this class
  for SERVER in $SERVERS; do
    # check connectivity to server
    REMOTEDATE=`$SSH ${SERVER} "date"`
    if [ "x$REMOTEDATE" != "x" ]; then
      # process server
      DATE=`date +%Y%m%d`
      # backup existing plugin-cfg.xml
      # get list of existing backups made today - date/time should be synchronized between syslogsrv and web servers
      BACKUPS=`$SSH ${SERVER} "ls /etc/httpd/conf.d/plugin-cfg.xml.backup.${DATE}-*"`
      if [ "x${BACKUPS}" != "x" ]; then
        # get next backup number
        next=$((`echo $BACKUPS | rev | cut -d '-' -f 1 | rev | awk 'BEGIN{max = 0}{if ($1 > max) max = $1}END{print max}'` + 1))
        BACKUP="/etc/httpd/conf.d/plugin-cfg.xml.backup.${DATE}-$next"
      else
        BACKUP="/etc/httpd/conf.d/plugin-cfg.xml.backup.${DATE}-1"
      fi
      echo "Backing up plugin-cfg.xml on $SERVER to $BACKUP"
##      $SSH ${SERVER} "cp -f /etc/httpd/conf.d/plugin-cfg.xml ${BACKUP}"
      echo "Installing plugin-cfg-${CLASS}.xml onto $SERVER"
##      $SCP /tmp/plugin-cfg-${CLASS}.xml ${SERVER}:/etc/httpd/conf.d/plugin-cfg.xml
    fi
  done

