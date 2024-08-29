def status_message(message):
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
            old_message = self.status_bar.GetStatusText()
            self.status_bar.SetStatusText(message)
            result = func(self, *args, **kwargs)
            self.status_bar.SetStatusText(old_message)
            return result
        return wrapper
    return decorator


THOUSAND = 1_000
MILLION = 1_000_000
BILLION = 1_000_000_000


def human_readable_rows(rows: int) -> str:
    """
    Convert the number of rows to a human-readable format.

    This method takes an integer representing the number of rows and converts it to a human-readable string,
    using appropriate units (e.g., thousands, millions, billions).

    Args:
        rows (int): The number of rows.

    Returns:
        str: The human-readable number of rows.
    """
    if rows < THOUSAND:
        return f"{rows:,}".replace(",", " ")
    elif rows < MILLION:
        return f"{rows / THOUSAND:.1f}K".replace(".0", "")
    elif rows < BILLION:
        return f"{rows / MILLION:.1f}M".replace(".0", "")
    else:
        return f"{rows / BILLION:.1f}B".replace(".0", "")
