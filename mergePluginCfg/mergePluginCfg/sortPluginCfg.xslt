<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="xml" indent="yes" />
	
	<xsl:template match="/Config">
	  <xsl:copy>
		<xsl:copy-of select="@*"/>
		<xsl:apply-templates select="*">
			<xsl:sort select="name()" order="descending"/>
			<xsl:sort select="@Name"/>
			<xsl:sort select="@ServerCluster"/>
		</xsl:apply-templates>
	  </xsl:copy>
	</xsl:template>

	<xsl:template match="/Config/UriGroup">
	  <xsl:copy>
		<xsl:apply-templates select="@*|*"><xsl:sort select="@Name"/></xsl:apply-templates>
	  </xsl:copy>
	</xsl:template>
	
	<xsl:template match="/Config/UriGroup/Uri">
	  <xsl:if test="preceding-sibling::node()[@Name=current()/@Name]">
	  	<xsl:message>WARN: Double Uri <xsl:value-of select="@Name"/> - <xsl:value-of select="../@Name"/></xsl:message>
	  	<xsl:comment>Double Uri</xsl:comment>
	  </xsl:if>
	  <xsl:if test="../preceding-sibling::node()/Uri[@Name=current()/@Name]">
	  	<xsl:message>WARN: Double Uri <xsl:value-of select="@Name"/> - <xsl:value-of select="../@Name"/> = <xsl:value-of select="../preceding-sibling::node()[Uri/@Name=current()/@Name]/@Name"/></xsl:message>
	  	<xsl:comment>Double Uri, see <xsl:value-of select="../preceding-sibling::node()[Uri/@Name=current()/@Name]/@Name"/></xsl:comment>
	  </xsl:if>
		<xsl:copy><xsl:apply-templates select="@*|*"/></xsl:copy>
	</xsl:template>
	
	<xsl:template match="/Config/VirtualHostGroup">
	  <xsl:copy><xsl:apply-templates select="@*|*"><xsl:sort select="@Name"/></xsl:apply-templates></xsl:copy>
	</xsl:template>

	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()" />
		</xsl:copy>
	</xsl:template>
</xsl:stylesheet>
