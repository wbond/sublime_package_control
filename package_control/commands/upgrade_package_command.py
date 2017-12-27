import threading

import sublime_plugin

from ..package_installer import PackageInstaller
from ..package_renamer import PackageRenamer
from ..show_error import show_message
from ..show_quick_panel import show_quick_panel
from ..thread_progress import ThreadProgress


class UpgradePackageCommand(sublime_plugin.WindowCommand):

    """
    A command that presents the list of installed packages that can be upgraded
    """

    def run(self):
        thread = UpgradePackageThread(self.window)
        thread.start()
        ThreadProgress(thread, 'Loading repositories', '')


class UpgradePackageThread(threading.Thread, PackageInstaller):

    """
    A thread to run the action of retrieving upgradable packages in.
    """

    def __init__(self, window):
        """
        :param window:
            An instance of :class:`sublime.Window` that represents the Sublime
            Text window to show the list of upgradable packages in.
        """
        self.window = window
        self.package_list = None
        self.renamer = PackageRenamer()
        self.renamer.load_settings()
        threading.Thread.__init__(self)
        PackageInstaller.__init__(self)

    def run(self):
        self.renamer.rename_packages(self)

        self.package_list = self.make_package_list(['install', 'reinstall', 'none'])

        if not self.package_list:
            show_message('There are no packages ready for upgrade')
            return
        show_quick_panel(self.window, self.package_list, self.on_done)

    def on_done(self, picked):
        """
        Quick panel user selection handler - disables a package, upgrades it,
        then re-enables the package

        :param picked:
            An integer of the 0-based package name index from the presented
            list. -1 means the user cancelled.
        """

        if picked > -1:
            name = self.package_list[picked][0]
            disabled_packages = self.disable_packages(name, 'upgrade')
            self.upgrade(name, disabled_packages, True)
