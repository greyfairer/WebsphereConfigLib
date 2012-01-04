<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:redirect="http://xml.apache.org/xalan/redirect"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	extension-element-prefixes="redirect">
	<xsl:output method="xml" indent="yes" />
	<xsl:param name="distDir">.</xsl:param>
	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()" />
		</xsl:copy>
	</xsl:template>
	<xsl:template match="/Cell">
		<xsl:for-each select="ServerCluster">
			<redirect:open file="{$distDir}/{./@name}.xml" />
			<redirect:write file="{$distDir}/{./@name}.xml">
				<xsl:copy>
					<xsl:attribute name="xsi:noNamespaceSchemaLocation">file://configsrv/configurations/Servers/APPSRVs/MLEwsadmin/bin/createServer.py/WASConfig.xsd</xsl:attribute>
					<xsl:apply-templates select="@*|node()" />
				</xsl:copy>
			</redirect:write>
			<redirect:close file="{$distDir}/{./@name}.xml" />
		</xsl:for-each>
		<xsl:for-each select="NodeConfig">
			<redirect:open file="{$distDir}/{./@name}.xml" />
			<redirect:write file="{$distDir}/{./@name}.xml">
				<xsl:copy>
					<xsl:attribute name="xsi:noNamespaceSchemaLocation">file://configsrv/configurations/Servers/APPSRVs/MLEwsadmin/bin/createServer.py/WASConfig.xsd</xsl:attribute>
					<xsl:apply-templates select="@*|node()" />
				</xsl:copy>
			</redirect:write>
			<redirect:close file="{$distDir}/{./@name}.xml" />
		</xsl:for-each>
		<xsl:if test="Applications">
			<redirect:open file="{$distDir}/Applications.xml" />
			<redirect:write file="{$distDir}/Applications.xml">
				<Applications>
				<xsl:attribute name="xsi:noNamespaceSchemaLocation">file://configsrv/configurations/Servers/APPSRVs/MLEwsadmin/bin/createServer.py/WASConfig.xsd</xsl:attribute>
				<xsl:copy-of select="Applications/*" />
				</Applications>
			</redirect:write>
			<redirect:close file="{$distDir}/Applications.xml" />
		</xsl:if>
		<CellConfig>
				<xsl:attribute name="xsi:noNamespaceSchemaLocation">file://configsrv/configurations/Servers/APPSRVs/MLEwsadmin/bin/createServer.py/WASConfig.xsd</xsl:attribute>
				<xsl:apply-templates select="CellConfig/*" />
		</CellConfig>
	</xsl:template>
	<xsl:template match="WorkManagerInfo[@name='DefaultWorkManager']" />
	<xsl:template match="WorkManagerProvider/text()" />
	<xsl:template match="DataSource/Attributes/J2EEResourceProperty" />
	<xsl:template match="JDBCProvider[@providerType='Derby JDBC Provider (XA)']" />
	<xsl:template match="JDBCProvider[@providerType='Oracle JDBC Driver']">
		<JDBCProvider providerType="Oracle JDBC Driver" databaseType="Oracle" implementationType="Connection pool data source"
			name="Oracle JDBC Driver" description="Oracle JDBC Driver">
			<xsl:for-each select="DataSource">
				<DataSource>
					<xsl:apply-templates select="@*" />
					<ResourceProperties>
						<xsl:copy-of select="Attributes/J2EEResourceProperty[@name='URL']" />
					</ResourceProperties>
					<Attributes>
						<xsl:apply-templates select="Attributes/*" />
					</Attributes>
				</DataSource>
			</xsl:for-each>
		</JDBCProvider>
	</xsl:template>
	<xsl:template match="JDBCProvider[@providerType='Oracle JDBC Driver (XA)']">
		<JDBCProvider providerType="Oracle JDBC Driver" databaseType="Oracle" implementationType="XA data source"
			description="Oracle JDBC Driver (XA)" name="Oracle JDBC Driver (XA)" >
			<xsl:for-each select="DataSource">
				<DataSource>
					<xsl:apply-templates select="@*" />
					<ResourceProperties>
						<xsl:copy-of select="Attributes/J2EEResourceProperty[@name='URL']" />
					</ResourceProperties>
					<Attributes>
						<xsl:apply-templates select="Attributes/*" />
					</Attributes>
				</DataSource>
			</xsl:for-each>
		</JDBCProvider>
	</xsl:template>
	<xsl:template match="JDBCProvider[@providerType='DB2 Legacy CLI-based Type 2 JDBC Driver' and @xa='false']">
		<JDBCProvider databaseType="DB2" providerType="DB2 Legacy CLI-based Type 2 JDBC Driver (Deprecated)" implementationType="Connection pool data source" 
			name="DB2 Legacy CLI-based Type 2 JDBC Driver" description="Deprecated - DB2 JDBC2-compliant Provider">
			<xsl:for-each select="DataSource">
				<DataSource>
					<xsl:apply-templates select="@*" />
					<ResourceProperties>
						<xsl:copy-of select="Attributes/J2EEResourceProperty[@name='databaseName']" />
					</ResourceProperties>
					<Attributes>
						<xsl:apply-templates select="Attributes/*" />
					</Attributes>
				</DataSource>
			</xsl:for-each>
		</JDBCProvider>
	</xsl:template>
	<xsl:template match="JDBCProvider[@providerType='DB2 Legacy CLI-based Type 2 JDBC Driver (XA)' and @xa='true']">
		<JDBCProvider databaseType="DB2" providerType="DB2 Legacy CLI-based Type 2 JDBC Driver (Deprecated)" implementationType="XA data source" 
			name="DB2 Legacy CLI-based Type 2 JDBC Driver (XA)" description="Deprecated - DB2 JDBC2-compliant Provider">
			<xsl:for-each select="DataSource">
				<DataSource>
					<xsl:apply-templates select="@*" />
					<ResourceProperties>
						<xsl:copy-of select="Attributes/J2EEResourceProperty[@name='databaseName']" />
					</ResourceProperties>
					<Attributes>
						<xsl:apply-templates select="Attributes/*" />
					</Attributes>
				</DataSource>
			</xsl:for-each>
		</JDBCProvider>
	</xsl:template>
</xsl:stylesheet>
