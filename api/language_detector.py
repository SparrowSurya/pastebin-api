"""Programming language auto-detection utility using Pygments."""

import logging

from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.lexers.special import TextLexer

logger = logging.getLogger(__name__)


def detect_language(text: str, fallback_kind: str, filename: str = "") -> str:
    """Analyze text snippet content to automatically detect its programming language.

    Tries filename extension guessing first, then content-based guessing.
    If both fail or result in plain text, falls back to the user-provided kind.

    Args:
        text: Raw source code/text content.
        fallback_kind: User-supplied language kind fallback.
        filename: Filename of the snippet (optional).

    Returns:
        The detected language identifier/alias, or the fallback_kind.
    """
    # 1. Try filename-based detection first
    if filename:
        try:
            lexer = get_lexer_for_filename(filename)
            if lexer and not isinstance(lexer, TextLexer) and lexer.aliases:
                detected = str(lexer.aliases[0])
                logger.info(
                    "Auto-detected language '%s' from filename '%s' (user: '%s')",
                    detected,
                    filename,
                    fallback_kind,
                )
                return detected
        except Exception as e:
            logger.debug(f"Filename language guessing failed for '{filename}': {e}")

    # 2. Try content-based detection
    if text.strip():
        try:
            lexer = guess_lexer(text)
            # If Pygments successfully guesses a specific language (not plain text)
            if lexer and not isinstance(lexer, TextLexer) and lexer.aliases:
                detected = str(lexer.aliases[0])
                logger.info(
                    "Auto-detected language '%s' from content (user: '%s')",
                    detected,
                    fallback_kind,
                )
                return detected
        except Exception as e:
            logger.debug(f"Pygments language guessing failed: {e}")

    return str(fallback_kind or "text")
