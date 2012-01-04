<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="xml" indent="yes" />
	
	<xsl:template match="/Config/UriGroup[@Name='default_host_ACCmum1_URIs']/Uri[@Name='/adm-jmx/*']">
	</xsl:template>

	<xsl:template match="/Config/UriGroup[@Name='default_host_ACCmum1_URIs']/Uri[@Name='/crsaxis/*']">
	  <Uri AffinityCookie="JSESSIONID" AffinityURLIdentifier="jsessionid" Name="/crsaxis/services/MUMFederationUserDataService"/><xsl:text>
      </xsl:text><Uri AffinityCookie="JSESSIONID" AffinityURLIdentifier="jsessionid" Name="/crsaxis/services/MUMFederationTicketService"/><xsl:text>
      </xsl:text><Uri AffinityCookie="JSESSIONID" AffinityURLIdentifier="jsessionid" Name="/crsaxis/services/MUMFederationTicketChainService"/>
	</xsl:template>

	<xsl:template match="/Config/UriGroup[@Name='default_host_ACCmum1_URIs']/Uri[@Name='/crsxfire/*']">
      <Uri AffinityCookie="JSESSIONID" AffinityURLIdentifier="jsessionid" Name="/crsxfire/services/MUMTicketService"/><xsl:text>
      </xsl:text><Uri AffinityCookie="JSESSIONID" AffinityURLIdentifier="jsessionid" Name="/crsxfire/services/IoSubscriptionService"/><xsl:text>
      </xsl:text><Uri AffinityCookie="JSESSIONID" AffinityURLIdentifier="jsessionid" Name="/crsxfire/services/MUMTicketIssuanceService"/>
	</xsl:template>
	
	<xsl:template match="@*|node()">
		<xsl:copy>
			<xsl:apply-templates select="@*|node()" />
		</xsl:copy>
	</xsl:template>
</xsl:stylesheet>
