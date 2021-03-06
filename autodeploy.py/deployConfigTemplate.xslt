<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes"/>
    <xsl:param name="earFileName"></xsl:param>
    <xsl:param name="httpServer">mappsacc.mle.mazdaeur.com</xsl:param>
    <xsl:param name="version"></xsl:param>
    <xsl:param name="serviceCall">Unknown</xsl:param>
    <xsl:param name="shortName"></xsl:param>
    <xsl:param name="comment"></xsl:param>
    <xsl:template match="/application">
        <application>
            <file>
                <xsl:value-of select="$earFileName"/>
            </file>
            <xsl:comment>Generated by AutoDeploy v4.0</xsl:comment>
            <xsl:if test="string-length($comment)>0">
                <xsl:comment>
                    <xsl:value-of select="$comment"/>
                </xsl:comment>
            </xsl:if>
            <name>
                <xsl:value-of select="normalize-space(display-name)"/>
            </name>
            <shortName>
                <xsl:value-of select="$shortName"/>
            </shortName>
            <version>
                <xsl:value-of select="$version"/>
            </version>
            <serviceCall>
                <xsl:value-of select="$serviceCall"/>
            </serviceCall>
            <xsl:for-each select="module/web">
                <module>
                    <name>
                        <xsl:value-of select="web-uri"/>
                    </name>
                    <context-root>
                        <xsl:value-of select="normalize-space(context-root)"/>
                    </context-root>
                </module>
            </xsl:for-each>
            <xsl:for-each select="module/ejb">
                <module>
                    <name>
                        <xsl:value-of select="."/>
                    </name>
                </module>
            </xsl:for-each>

            <target>
            </target>
            <installOption>-usedefaultbindings</installOption>
        </application>
    </xsl:template>
    <xsl:template match="/j2ee:application" xmlns:j2ee="http://java.sun.com/xml/ns/j2ee">
        <application>
            <file>
                <xsl:value-of select="$earFileName"/>
            </file>
            <xsl:comment>Generated by AutoDeploy v4.0</xsl:comment>
            <xsl:if test="string-length($comment)>0">
                <xsl:comment>
                    <xsl:value-of select="$comment"/>
                </xsl:comment>
            </xsl:if>
            <name>
                <xsl:value-of select="normalize-space(j2ee:display-name)"/>
            </name>
            <shortName>
                <xsl:value-of select="$shortName"/>
            </shortName>
            <version>
                <xsl:value-of select="$version"/>
            </version>
            <serviceCall>
                <xsl:value-of select="$serviceCall"/>
            </serviceCall>
            <xsl:for-each select="j2ee:module/j2ee:web">
                <module>
                    <name>
                        <xsl:value-of select="j2ee:web-uri"/>
                    </name>
                    <context-root>
                        <xsl:value-of select="normalize-space(j2ee:context-root)"/>
                    </context-root>
                </module>
            </xsl:for-each>
            <xsl:for-each select="j2ee:module/j2ee:ejb">
                <module>
                    <name>
                        <xsl:value-of select="."/>
                    </name>
                </module>
            </xsl:for-each>

            <target>
            </target>
            <installOption>-usedefaultbindings</installOption>
        </application>
    </xsl:template>
    <xsl:template match="/jee:application" xmlns:jee="http://java.sun.com/xml/ns/javaee">
        <application>
            <file>
                <xsl:value-of select="$earFileName"/>
            </file>
            <xsl:comment>Generated by AutoDeploy v4.0</xsl:comment>
            <xsl:if test="string-length($comment)>0">
                <xsl:comment>
                    <xsl:value-of select="$comment"/>
                </xsl:comment>
            </xsl:if>
            <name>
                <xsl:value-of select="normalize-space(jee:display-name)"/>
            </name>
            <shortName>
                <xsl:value-of select="$shortName"/>
            </shortName>
            <version>
                <xsl:value-of select="$version"/>
            </version>
            <serviceCall>
                <xsl:value-of select="$serviceCall"/>
            </serviceCall>
            <xsl:for-each select="jee:module/jee:web">
                <module>
                    <name>
                        <xsl:value-of select="jee:web-uri"/>
                    </name>
                    <context-root>
                        <xsl:value-of select="normalize-space(jee:context-root)"/>
                    </context-root>
                </module>
            </xsl:for-each>
            <xsl:for-each select="jee:module/jee:ejb">
                <module>
                    <name>
                        <xsl:value-of select="."/>
                    </name>
                </module>
            </xsl:for-each>

            <target>
            </target>
            <installOption>-usedefaultbindings</installOption>
        </application>
    </xsl:template>
</xsl:stylesheet>