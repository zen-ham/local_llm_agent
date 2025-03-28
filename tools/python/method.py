import contextlib, traceback
from io import StringIO


def method(code):
    try:
        # Use the provided global namespace or the default one
        global_namespace = globals() or {}

        # Redirect stdout to capture the output
        with contextlib.redirect_stdout(StringIO()) as captured_output:
            # Execute the code with the specified global namespace
            exec(code, global_namespace)

        # Get the captured output as a string
        output_string = captured_output.getvalue()

        return output_string
    except Exception as e:
        # If an error occurs, format the error message with traceback details
        error_info = traceback.format_exc()
        return f"{error_info}"