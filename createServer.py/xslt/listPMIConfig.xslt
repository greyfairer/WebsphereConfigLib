<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" indent="yes"/>

    <xsl:template match="/">
        <xsl:for-each select="/Cell/ServerCluster/ServerConfig">
            Server Name:
            <xsl:value-of select="@match"/>
            PMIService statisticSet:
            <xsl:value-of select="Services/PMIService/Attributes/statisticSet/text()"/>
            PMIService synchronizedUpdate:
            <xsl:value-of select="Services/PMIService/Attributes/synchronizedUpdate/text()"/>
        </xsl:for-each>
<xsl:text>
</xsl:text>
    </xsl:template>
</xsl:stylesheet>
