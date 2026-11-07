"""Exception hierarchy; the CLI reports any FleetError as a one-line message."""


class FleetError(Exception):
    """Base class for expected, user-facing failures."""


class InventoryError(FleetError):
    """The inventory file is missing or does not match the contract."""


class TemplateError(FleetError):
    """A template cannot be resolved or rendered."""


class CommandError(FleetError):
    """An external command failed or could not be started."""
