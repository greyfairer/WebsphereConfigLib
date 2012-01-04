<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" indent="yes"/>

    <xsl:template match="/">
        <xsl:for-each select="/Cell/CellConfig/Security/JAASAuthData">
            JAASAuthData
            <xsl:value-of select="@alias"/> -> userId='<xsl:value-of select="@userId"/>'
        </xsl:for-each>
<xsl:text>
</xsl:text>
        <xsl:for-each select="/Cell/ServerCluster">
            Cluster
            <xsl:value-of select="@name"/>
            <xsl:for-each select="ClusterConfig/Resources/JDBCProvider/DataSource">
                <xsl:variable name="authDataAlias" select="Attributes/authDataAlias/text()"/>
                DataSource
                <xsl:value-of select="@jndiName"/> ->
                <xsl:value-of select="$authDataAlias"/> ->
                <xsl:value-of select="/Cell/CellConfig/Security/JAASAuthData[@alias=$authDataAlias]/@userId"/>
            </xsl:for-each>
<xsl:text>
</xsl:text>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
