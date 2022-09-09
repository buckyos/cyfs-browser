#!/bin/sh

/usr/bin/su $USER -c  "/usr/sbin/installer -pkg ./cyfs_browser_package.pkg -target CurrentUserHomeDirectory"

exit 0
