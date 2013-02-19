import sublime
import sys
import os


st_version = 2
# With the way ST3 works, the sublime module is not "available" at startup
# which results in an empty version number
if sublime.version() == '' or int(sublime.version()) > 3000:
	st_version = 3


reloader_name = 'package_control.reloader'

if st_version == 3:
	from imp import reload

# Make sure all dependencies are reloaded on upgrade
if reloader_name in sys.modules:
    reload(sys.modules[reloader_name])

sys.path.insert(0, os.path.split(__file__)[0])

from package_control import reloader
from package_control import sys_path

from package_control.commands.add_repository_channel_command import AddRepositoryChannelCommand
from package_control.commands.add_repository_command import AddRepositoryCommand
from package_control.commands.create_binary_package_command import CreateBinaryPackageCommand
from package_control.commands.create_package_command import CreatePackageCommand
from package_control.commands.disable_package_command import DisablePackageCommand
from package_control.commands.discover_packages_command import DiscoverPackagesCommand
from package_control.commands.enable_package_command import EnablePackageCommand
from package_control.commands.install_package_command import InstallPackageCommand
from package_control.commands.list_packages_command import ListPackagesCommand
from package_control.commands.remove_package_command import RemovePackageCommand
from package_control.commands.upgrade_all_packages_command import UpgradeAllPackagesCommand
from package_control.commands.upgrade_package_command import UpgradePackageCommand

from package_control.package_cleanup import PackageCleanup


# Start shortly after Sublime starts so package renames don't cause errors
# with keybindings, settings, etc disappearing in the middle of parsing
sublime.set_timeout(lambda: PackageCleanup().start(), 2000)
