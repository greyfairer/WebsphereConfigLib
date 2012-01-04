<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="text"/>

	<xsl:template match="/">
<xsl:for-each select="/Cell/ServerCluster/ClusterConfig/Resources/JDBCProvider[@providerType!='Derby JDBC Provider (XA)']">
ClusterName: <xsl:value-of select="../../../@name"/>
ProviderType: <xsl:value-of select="@providerType"/>
<xsl:for-each select="DataSource">
  DataSource: <xsl:value-of select="@name"/>
    JNDI Name: <xsl:value-of select="@jndiName"/>
    Description: <xsl:value-of select="@Description"/>
    AuthDataAlias: <xsl:value-of select="Attributes/authDataAlias"/>
    Database Name: <xsl:value-of select="Attributes/J2EEResourceProperty[@name='databaseName']/@value"/>
    URL: <xsl:value-of select="Attributes/J2EEResourceProperty[@name='URL']/@value"/>
    Connection Pool: 
      connectionTimeout: <xsl:value-of select="Attributes/connectionPool/@connectionTimeout"/>
      maxConnections: <xsl:value-of select="Attributes/connectionPool/@maxConnections"/>
      minConnections: <xsl:value-of select="Attributes/connectionPool/@minConnections"/>
      unusedTimeout: <xsl:value-of select="Attributes/connectionPool/@unusedTimeout"/>   
</xsl:for-each>
</xsl:for-each>
<xsl:text>
</xsl:text>        
<xsl:for-each select="/Cell/ServerCluster/ServerConfig/Resources/JDBCProvider[@providerType!='Derby JDBC Provider (XA)']">
ClusterName: <xsl:value-of select="../../../@name"/>
ServerName: <xsl:value-of select="../../@match"/>
ProviderType: <xsl:value-of select="@providerType"/>
<xsl:for-each select="DataSource">
  DataSource: <xsl:value-of select="@name"/>
    JNDI Name: <xsl:value-of select="@jndiName"/>
    Description: <xsl:value-of select="@Description"/>
    AuthDataAlias: <xsl:value-of select="Attributes/authDataAlias"/>
    Database Name: <xsl:value-of select="Attributes/J2EEResourceProperty[@name='databaseName']/@value"/>
    URL: <xsl:value-of select="Attributes/J2EEResourceProperty[@name='URL']/@value"/>
    Connection Pool: 
      connectionTimeout: <xsl:value-of select="Attributes/connectionPool/@connectionTimeout"/>
      maxConnections: <xsl:value-of select="Attributes/connectionPool/@maxConnections"/>
      minConnections: <xsl:value-of select="Attributes/connectionPool/@minConnections"/>
      unusedTimeout: <xsl:value-of select="Attributes/connectionPool/@unusedTimeout"/>   
</xsl:for-each>
</xsl:for-each>
<xsl:text>
</xsl:text>        
    </xsl:template>
</xsl:stylesheet>
