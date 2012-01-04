<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="xml" indent="yes"/>
	<xsl:template match="/Cell">
<ClusterApplications>
	<xsl:for-each-group select="Applications/Application/Module" group-by="Target/@cluster">
<Cluster name="{current-grouping-key()}">
	<xsl:for-each-group select="current-group()" group-by="../@name">
  <Application name="{current-grouping-key()}" classloader.mode="{/Cell/Applications/Application[@name=current-grouping-key()]/Attributes/@classloader.mode}" warClassLoaderPolicy="{/Cell/Applications/Application[@name=current-grouping-key()]/Attributes/@warClassLoaderPolicy}">
    <xsl:for-each select="current-group()">
    <Module uri="{@uri}" classloaderMode="{Attributes/@classloaderMode}" startingWeight="{Attributes/@startingWeight}"/>
    </xsl:for-each>
   </Application>
	</xsl:for-each-group>
	<xsl:for-each select="/Cell/ServerCluster[@name=current-grouping-key()]/Node/Server">
<Server name="{./@name}" node="{../@name}" maxHeapSize="{../../ServerConfig/Services/JavaVirtualMachine/Attributes/maximumHeapSize/text()}">
	<xsl:copy-of select="ServerPort[@endPointName='BOOTSTRAP_ADDRESS']" copy-namespaces="no"/>
	<xsl:copy-of select="ServerPort[@endPointName='WC_defaulthost']" copy-namespaces="no"/>
	<xsl:copy-of select="ServerPort[@endPointName='SOAP_CONNECTOR_ADDRESS']" copy-namespaces="no"/>
</Server>
  </xsl:for-each>	
</Cluster>
	</xsl:for-each-group>
	<xsl:for-each-group select="Applications/Application/Module" group-by="Target/@node">
<Node name="{current-grouping-key()}">
	<xsl:for-each-group select="current-group()" group-by="Target[@node=current-grouping-key()]/@server">
  <Server name="{current-grouping-key()}">
	<xsl:for-each-group select="current-group()" group-by="../@name">
  <Application name="{current-grouping-key()}" classloader.mode="{/Cell/Applications/Application[@name=current-grouping-key()]/Attributes/@classloader.mode}" warClassLoaderPolicy="{/Cell/Applications/Application[@name=current-grouping-key()]/Attributes/@warClassLoaderPolicy}">
    <xsl:for-each select="current-group()">
    <Module uri="{@uri}" classloaderMode="{Attributes/@classloaderMode}" startingWeight="{Attributes/@startingWeight}"/>
    </xsl:for-each>
   </Application>
	</xsl:for-each-group>
  </Server>
	</xsl:for-each-group>
</Node>
	</xsl:for-each-group>
</ClusterApplications>
    </xsl:template>
</xsl:stylesheet>
	