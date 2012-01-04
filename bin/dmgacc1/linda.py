overrideSessionManagementAttr = ['enable', 'true']
attrs = [overrideSessionManagementAttr]
sessionMgt = [['sessionManagement', attrs]]

wcfg = AdminConfig.list('WebModuleConfig', *webModuleId *)
if wcfg == '':
    print 'creating WebModuleConfig...'
AdminConfig.create('WebModuleConfig', *webModuleId *, sessionMgt)
else:
print 'modifying WebModuleConfig...'
AdminConfig.modify(wcfg, sessionMgt)
print 'URL Re-writing was enabled successfully'
