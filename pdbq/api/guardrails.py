# pdbq - Natural language query agent for PeeringDB
# Copyright (C) 2025 Chris Grundemann
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
Pre-flight guardrails applied before the agent is invoked.
These are cheap checks that avoid burning API tokens on obviously invalid input.
"""
import re

# Maximum query length — guards against prompt injection via very long inputs
MAX_QUERY_LENGTH = 800

# Patterns that are almost certainly off-topic or injection attempts.
# This is a first-pass filter only; the agent's decline_query tool handles
# ambiguous cases.
_OFFTOPIC_PATTERNS = re.compile(
    r"\b("
    r"write (me )?(a |an )?(poem|story|essay|song|haiku|joke|script|novel)"
    r"|ignore (all )?(previous|prior|above) instructions?"
    r"|you are now|pretend (you are|to be)|act as (a |an )(?!expert)"
    r"|translate (this|the following)"
    r"|what is the (weather|stock price|recipe)"
    r"|tell me a joke"
    r")\b",
    re.IGNORECASE,
)


class QueryRejected(Exception):
    """Raised when a query fails pre-flight checks."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def check_query(query: str) -> None:
    """
    Run pre-flight checks on a raw query string.
    Raises QueryRejected if the query should be rejected before reaching the agent.
    """
    if not query or not query.strip():
        raise QueryRejected("Query cannot be empty.")

    if len(query) > MAX_QUERY_LENGTH:
        raise QueryRejected(
            f"Query is too long ({len(query)} characters). "
            f"Please keep queries under {MAX_QUERY_LENGTH} characters."
        )

    if _OFFTOPIC_PATTERNS.search(query):
        raise QueryRejected(
            "pdbq answers questions about PeeringDB data — internet exchanges, "
            "networks (ASNs), facilities, and peering relationships. "
            "This query appears to be outside that scope."
        )
