# telecli_admin/exceptions.py

class TelegramAdminError(Exception):
    """Base exception for the application."""
    pass

class AuthenticationError(TelegramAdminError):
    """Raised when authentication fails."""
    pass

class GroupNotFoundError(TelegramAdminError):
    """Raised when a specific group/channel is not found."""
    pass

class MediaExportError(TelegramAdminError):
    """Raised during a media export operation."""
    pass

class SpamDetectionError(TelegramAdminError):
    """Raised during a spam detection operation."""
    pass
