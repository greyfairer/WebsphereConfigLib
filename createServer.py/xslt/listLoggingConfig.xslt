<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="xml" indent="yes" />
	
	<xsl:template match="/">
	<xsl:for-each select="/Cell/ServerCluster/ServerConfig">
<ServerConfig match="{./@match}">
  <Attributes>
<xsl:copy-of select="Attributes/outputStreamRedirect"/>
<xsl:copy-of select="Attributes/errorStreamRedirect"/>
  </Attributes>
</ServerConfig>
<xsl:text>
</xsl:text>
	</xsl:for-each>
	</xsl:template>
</xsl:stylesheet>
