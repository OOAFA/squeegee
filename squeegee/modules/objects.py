class RDPObject:

    def __init__(self):
        self._fileName = None
        self._operatingSystem = "None found"
        self._domain = "None found"
        self._isPatched = True
        self._usernames = []

    @property
    def fileName(self):
        return self._fileName

    @fileName.setter
    def fileName(self, fileName):
        self._fileName = fileName

    @property
    def operatingSystem(self):
        return self._operatingSystem
    
    @operatingSystem.setter
    def operatingSystem(self, operatingSystem):
        self._operatingSystem = operatingSystem

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, domain):
        self._domain = domain

    @property
    def isPatched(self):
        return self._isPatched

    @isPatched.setter
    def isPatched(self, isPatched):
        self._isPatched = isPatched

    @property
    def usernames(self):
        return self._usernames

    @usernames.setter
    def usernames(self, usernames):
        self._usernames = usernames



