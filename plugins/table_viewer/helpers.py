def status_message(message, pos: int = 0):
    """
    Decorator to set the status bar message in the main window.

    This decorator function sets the status bar message to the provided message before executing the decorated function,
    and then sets the status bar message back to "Main thread ready" after the function has completed.

    Args:
        message (str): The message to be displayed in the status bar.

    Returns:
        The decorated function.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            old_message = self.status_bar.GetStatusText(pos)
            self.status_bar.SetStatusText(message, pos)
            result = func(self, *args, **kwargs)
            self.status_bar.SetStatusText(old_message, pos)
            return result
        return wrapper
    return decorator
