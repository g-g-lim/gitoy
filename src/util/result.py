class Result[T]:
    """Represents the outcome of an operation.

    Attributes
    ----------
    success : bool
        A flag that is set to True if the operation was successful, False if
        the operation failed.
    value : object
        The result of the operation if successful, value is None if operation
        failed or if the operation has no return value.
    error : str
        Error message detailing why the operation failed, value is None if
        operation was successful.
    """

    def __init__(self, success: bool, value: T | None, error: str | None):
        self.success = success
        self.error = error
        self.value = value

    @property
    def failed(self) -> bool:
        """True if operation failed, False if successful (read-only)."""
        return not self.success

    def __str__(self):
        if self.success:
            return f"[Success]"  # noqa: F541
        else:
            return f'[Failure] "{self.error}"'

    def __repr__(self):
        if self.success:
            return f"<Result success={self.success}>"
        else:
            return f'<Result success={self.success}, message="{self.error}">'

    @classmethod
    def Fail(cls, error: str) -> "Result":
        """Create a Result object for a failed operation."""
        return cls(False, value=None, error=error)

    @classmethod
    def Ok(cls, value: T) -> "Result":
        """Create a Result object for a successful operation."""
        return cls(True, value=value, error=None)
