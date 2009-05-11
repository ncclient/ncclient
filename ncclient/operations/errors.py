from ncclient import NCClientError

class OperationError(NCClientError):
    pass

class MissingCapabilityError(NCClientError):
    pass

