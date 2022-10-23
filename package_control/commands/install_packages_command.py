import threading
import time

import sublime
import sublime_plugin

from ..console_write import console_write
from ..package_installer import PackageInstaller
from ..show_error import show_error, show_message
from ..thread_progress import ThreadProgress

USE_QUICK_PANEL_ITEM = hasattr(sublime, 'QuickPanelItem')


class InstallPackagesCommand(sublime_plugin.ApplicationCommand):

    """
    A command that accepts a list of packages to install,
    or prompts the user to paste a comma-separated list.

    Example:

    ```py
    sublime.run_command(
        "install_packages",
        {
            "packages": ["Package 1", "Package 2"],
            "unattended": False  # don't suppress error dialogs
        }
    )
    ```
    """

    def run(self, packages=None, unattended=False):
        if isinstance(packages, list):
            thread = InstallPackagesThread(packages, unattended)
            thread.start()
            message = 'Installing package'
            if len(packages) > 1:
                message += 's'
            ThreadProgress(thread, message, '')
            return

        def on_done(input_text):
            packages = []
            for package in input_text.split(','):
                if package:
                    package = package.strip()
                    if package:
                        packages.append(package)

            if not packages:
                show_error('No package names were entered')
                return

            self.run(packages, False)

        sublime.active_window().show_input_panel(
            'Packages to install (comma-separated)',
            '',
            on_done,
            None,
            None
        )


class InstallPackagesThread(threading.Thread, PackageInstaller):

    """
    A thread to run the installation of one or more packages in
    """

    def __init__(self, packages, unattended):
        """
        Constructs a new instance.

        :param packages:
            The list of package names

        :param unattended:
            A flag to decide whether to display modal error/message dialogs.
        """

        self.packages = set(packages)
        self.unattended = unattended

        threading.Thread.__init__(self)
        PackageInstaller.__init__(self)

    def run(self):
        console_write('Loading repository...')
        package_list = self.make_package_list(['upgrade', 'downgrade', 'reinstall', 'pull', 'none'])
        if not package_list:
            console_write('There are no packages available for installation')
            if not self.unattended:
                show_message(
                    '''
                    There are no packages available for installation

                    Please see https://packagecontrol.io/docs/troubleshooting for help
                    '''
                )
            return

        if USE_QUICK_PANEL_ITEM:
            package_names = {info.trigger for info in package_list if info.trigger in self.packages}
        else:
            package_names = {info[0] for info in package_list if info[0] in self.packages}

        if not package_names:
            console_write('All packages already installed!')
            if not self.unattended:
                show_message('All packages already installed!')
            return

        console_write(
            'Installing %d package%s...',
            (len(package_names), 's' if len(package_names) != 1 else '')
        )

        self.disable_packages(package_names, 'install')
        time.sleep(0.7)

        deffered = set()

        try:
            for package in sorted(package_names, key=lambda s: s.lower()):
                result = self.manager.install_package(package)
                # do not re-enable package if operation is dereffered to next start
                if result is None:
                    deffered.add(package)
        finally:
            time.sleep(0.7)
            self.reenable_packages(package_names - deffered, 'install')