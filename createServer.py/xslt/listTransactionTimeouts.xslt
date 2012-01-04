<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" indent="yes"/>

    <xsl:template match="/">
	<xsl:text>Server name:&#09;total&#09;- maximum
</xsl:text>
        <xsl:for-each select="/Cell/ServerCluster/ServerConfig">
            <xsl:value-of select="@match"/>:&#09;<xsl:value-of
                select="Services/TransactionService/Attributes/totalTranLifetimeTimeout/text()"/>&#09;-
            <xsl:value-of
                    select="Services/TransactionService/Attributes/propogatedOrBMTTranLifetimeTimeout/text()"/>
	<xsl:text>
</xsl:text>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
