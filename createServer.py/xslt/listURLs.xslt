<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes"/>

    <xsl:template match="/Cell">
        <Cell name="{@name}" xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'
              xsi:noNamespaceSchemaLocation='file://configsrv/configurations/Servers/APPSRVs/MLEwsadmin/bin/createServer.py/WASConfig.xsd'>
            <xsl:if test="CellConfig/Resources/URLProvider/URL">
                <CellConfig>
                    <Resources>
                        <xsl:for-each select="CellConfig/Resources/URLProvider[URL]">
                            <xsl:copy-of select="."/>
                        </xsl:for-each>
                    </Resources>
                </CellConfig>
            </xsl:if>
            <xsl:for-each select="ServerCluster">
                <ServerCluster name="{./@name}">
                    <ClusterConfig>
                        <Resources>
                            <xsl:for-each select="ClusterConfig/Resources/URLProvider[URL]">
                                <xsl:copy-of select="."/>
                            </xsl:for-each>
                        </Resources>
                    </ClusterConfig>
                    <xsl:for-each select="ServerConfig[Resources/URLProvider/URL]">
                        <ServerConfig match="{./@match}">
                            <Resources>
                                <xsl:for-each select="Resources/URLProvider[URL]">
                                    <xsl:copy-of select="."/>
                                </xsl:for-each>
                            </Resources>
                        </ServerConfig>
                    </xsl:for-each>
                </ServerCluster>
            </xsl:for-each>
        </Cell>
    </xsl:template>
</xsl:stylesheet>
