class NonCleanExitError(Exception):

    """
    When an subprocess does not exit cleanly

    :param returncode:
        The command line integer return code of the subprocess
    """

    def __init__(self, returncode):
        self.returncode = returncode

    def __unicode__(self):
        return str(self.returncode)

    def __str__(self):
        return self.__unicode__()

    def __bytes__(self):
        return self.__unicode__().encode('utf-8')
