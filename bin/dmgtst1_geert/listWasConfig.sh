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


cd /usr/local/MLEwsadmin/bin/createServer.py

/opt/IBM/WebSphere/AppServer/bin/ws_ant.sh -f /usr/local/MLEwsadmin/bin/createServer.py/listConfig.xml listConfig split

xsltproc xslt/listHeapSize.xslt        ../../conf/$WAS_CELL/$WAS_CELL.xml > ../../conf/$WAS_CELL/listHeapSize.txt
xsltproc xslt/listDataSources.xslt     ../../conf/$WAS_CELL/$WAS_CELL.xml > ../../conf/$WAS_CELL/listDataSources.txt
xsltproc xslt/listPMIConfig.xslt       ../../conf/$WAS_CELL/$WAS_CELL.xml > ../../conf/$WAS_CELL/listPMIConfig.txt
xsltproc xslt/listJAASLogins.xslt      ../../conf/$WAS_CELL/$WAS_CELL.xml > ../../conf/$WAS_CELL/listJAASLogins.txt
xsltproc xslt/listLoggingConfig.xslt   ../../conf/$WAS_CELL/$WAS_CELL.xml > ../../conf/$WAS_CELL/listLoggingConfig.txt
xsltproc xslt/listTransactionTimeouts.xslt   ../../conf/$WAS_CELL/$WAS_CELL.xml > ../../conf/$WAS_CELL/listTransactionTimeouts.txt
xsltproc xslt/listMailSessions.xslt   ../../conf/$WAS_CELL/$WAS_CELL.xml > ../../conf/$WAS_CELL/listMailSessions.xml
xsltproc xslt/listURLs.xslt   ../../conf/$WAS_CELL/$WAS_CELL.xml > ../../conf/$WAS_CELL/listURLs.xml
xsltproc xslt/listDataSourcesXml.xslt   ../../conf/$WAS_CELL/$WAS_CELL.xml > ../../conf/$WAS_CELL/listDataSourcesXml.xml

cp  ../../conf/$WAS_CELL/$WAS_CELL.xml  ../../conf/$WAS_CELL/$WAS_CELL.${LOGDATE}.xml

gzip ../../conf/$WAS_CELL/$WAS_CELL.${LOGDATE}.xml

cd -
pwd
