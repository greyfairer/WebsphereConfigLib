<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="xml" indent="yes" />

	<xsl:template match="/Cell">
		<Cell name="{@name}" xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xsi:noNamespaceSchemaLocation='file://configsrv/configurations/Servers/APPSRVs/MLEwsadmin/bin/createServer.py/WASConfig.xsd'>
			<xsl:if test="CellConfig/Resources/JDBCProvider/DataSource">
				<CellConfig>
					<Resources>
						<xsl:for-each select="CellConfig/Resources/JDBCProvider[DataSource]">
							<xsl:apply-templates select="."/>
						</xsl:for-each>
					</Resources>
				</CellConfig>
			</xsl:if>
			<xsl:for-each select="ServerCluster">
				<ServerCluster name="{./@name}">
					<ClusterConfig>
						<Resources>
							<xsl:for-each select="ClusterConfig/Resources/JDBCProvider[DataSource]">
								<xsl:apply-templates select="."/>
							</xsl:for-each>
						</Resources>
					</ClusterConfig>
					<xsl:for-each select="ServerConfig[Resources/JDBCProvider[@providerType='Oracle JDBC Driver' or @providerType='Oracle JDBC Driver (XA)' or @providerType='DB2 Legacy CLI-based Type 2 JDBC Driver' or @providerType='DB2 Legacy CLI-based Type 2 JDBC Driver (XA)']/DataSource]">
						<ServerConfig match="{./@match}">
							<Resources>
								<xsl:for-each select="Resources/JDBCProvider[DataSource]">
									<xsl:apply-templates select="."/>
								</xsl:for-each>
							</Resources>
						</ServerConfig>
					</xsl:for-each>
				</ServerCluster>
			</xsl:for-each>
		</Cell>
	</xsl:template>

	<xsl:template match="JDBCProvider[@providerType='Oracle JDBC Driver']">
		<JDBCProvider providerType="Oracle JDBC Driver" databaseType="Oracle" implementationType="Connection pool data source"
			name="Oracle JDBC Driver" description="Oracle JDBC Driver">
			<xsl:for-each select="DataSource">
				<DataSource>
					<xsl:copy-of select="@*" />
					<ResourceProperties>
						<xsl:copy-of select="Attributes/J2EEResourceProperty[@name='URL']" />
					</ResourceProperties>
					<Attributes>
						<xsl:copy-of select="Attributes/authDataAlias" />
						<xsl:copy-of select="Attributes/connectionPool" />
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
					<xsl:copy-of select="@*" />
					<ResourceProperties>
						<xsl:copy-of select="Attributes/J2EEResourceProperty[@name='URL']" />
					</ResourceProperties>
					<Attributes>
						<xsl:copy-of select="Attributes/authDataAlias" />
						<xsl:copy-of select="Attributes/connectionPool" />
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
					<xsl:copy-of select="@*" />
					<ResourceProperties>
						<xsl:copy-of select="Attributes/J2EEResourceProperty[@name='databaseName']" />
					</ResourceProperties>
					<Attributes>
						<xsl:copy-of select="Attributes/authDataAlias" />
						<xsl:copy-of select="Attributes/connectionPool" />
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
					<xsl:copy-of select="@*" />
					<ResourceProperties>
						<xsl:copy-of select="Attributes/J2EEResourceProperty[@name='databaseName']" />
					</ResourceProperties>
					<Attributes>
						<xsl:copy-of select="Attributes/authDataAlias" />
						<xsl:copy-of select="Attributes/connectionPool" />
					</Attributes>
				</DataSource>
			</xsl:for-each>
		</JDBCProvider>
	</xsl:template>
		
</xsl:stylesheet>
