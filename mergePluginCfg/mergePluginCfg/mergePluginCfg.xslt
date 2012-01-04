<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="xml" indent="yes" />
	<xsl:param name="mergeFileName">required param: mergeFileName</xsl:param>
	<xsl:variable name="mergeFileDoc" select="document($mergeFileName)" />
	
	<xsl:template match="/Config/VirtualHostGroup">
		<xsl:variable name="groupName" select="./@Name" />
		<xsl:copy>
			<xsl:copy-of select="@*"/>

			<xsl:variable name="currentVirtualHosts" select="./VirtualHost" />
			<xsl:apply-templates />
			<xsl:comment>VirtualHosts from <xsl:value-of select="$mergeFileName" /></xsl:comment>
			<xsl:text>
			</xsl:text>
			<xsl:for-each select="$mergeFileDoc/Config/VirtualHostGroup[@Name=$groupName]/VirtualHost">
				<xsl:if test="not($currentVirtualHosts[@Name=current()/@Name])">
					<xsl:copy-of select="." />
				</xsl:if>
			</xsl:for-each>
		</xsl:copy>
	</xsl:template>
	
	<xsl:template match="/Config/ServerCluster[1]">
		<xsl:comment>Other VirtualHostGroups from <xsl:value-of select="$mergeFileName" /></xsl:comment>
		<xsl:text>
		</xsl:text>
		<xsl:variable name="currentVirtualHostGroups" select="/Config/VirtualHostGroup" />
		<xsl:for-each select="$mergeFileDoc/Config/VirtualHostGroup">
			<xsl:if test="not($currentVirtualHostGroups[@Name=current()/@Name])">
				<xsl:copy-of select="." />
			</xsl:if>
		</xsl:for-each>
		<xsl:copy-of select="."/>
	</xsl:template>	
	
	<xsl:template match="/Config/ServerCluster[count(/Config/ServerCluster)]">
		<xsl:copy-of select="." />
		<xsl:comment>ServerClusters from <xsl:value-of select="$mergeFileName" /></xsl:comment>
		<xsl:text>
		</xsl:text>
		<xsl:copy-of select="$mergeFileDoc/Config/ServerCluster" />
	</xsl:template>
	<xsl:template match="/Config/Route[count(/Config/Route)]">
		<xsl:copy-of select="." />
		<xsl:comment>UriGroups/Routes from <xsl:value-of select="$mergeFileName" /></xsl:comment>
		<xsl:text>
		</xsl:text>
		<xsl:copy-of select="$mergeFileDoc/Config/*[name()='UriGroup' or name()='Route']" />
	</xsl:template>
	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()" />
		</xsl:copy>
	</xsl:template>
</xsl:stylesheet>