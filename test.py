import pytest
import anyio
from mcp.client.stdio import stdio_client, StdioServerParameters

@pytest.mark.anyio
async def test_stdio_client_no_broken_resource_error():
    """
    Regression test: Ensure stdio_client doesn't crash with BrokenResourceError
    during cleanup when child processes exit or streams break.
    """

    # Simple echo command that produces invalid JSON for the client
    server = StdioServerParameters(command="echo", args=["hello"])

    # Timeout to prevent test from hanging
    with anyio.move_on_after(5.0) as cancel_scope:
        with pytest.raises(Exception) as exc_info:
            async with stdio_client(server):
                await anyio.sleep(0.01)  # Let the client try to read invalid JSON

    error = exc_info.value
    error_text = str(error)

    # Flatten nested exceptions if it's an ExceptionGroup
    if hasattr(error, 'exceptions'):
        all_errors = [str(sub_error) for sub_error in error.exceptions]
        error_text = " | ".join(all_errors)

    # The fix: These errors should NOT appear
    assert "BrokenResourceError" not in error_text
    assert "Attempted to exit cancel scope" not in error_text

    # Ensure it didn't hang
    assert not cancel_scope.cancelled_caught, "Test timed out; cleanup should be graceful"






