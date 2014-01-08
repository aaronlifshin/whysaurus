import os

from google.appengine.api import lib_config

# These should_profile functions return true whenever a request should be
# profiled.
#
# You can override these functions in appengine_config.py. See example below
# and https://developers.google.com/appengine/docs/python/tools/appengineconfig
#
# These functions will be run once per request, so make sure they are fast.
#
# Example:
#   ...in appengine_config.py:
#       def gae_mini_profiler_should_profile_production():
#           from google.appengine.api import users
#           return users.is_current_user_admin()


class Mode(object):
    """Possible profiler modes.

    TODO(kamens): switch this from an enum to a more sensible bitmask or other
    alternative that supports multiple settings without an exploding number of
    enums.

    TODO(kamens): when this is changed from an enum to a bitmask or other more
    sensible object with multiple properties, we should pass a Mode object
    around the rest of this code instead of using a simple string that this
    static class is forced to examine (e.g. if self.mode.is_rpc_enabled()).
    """

    SIMPLE = "simple"  # Simple start/end timing for the request as a whole
    CPU_INSTRUMENTED = "instrumented"  # Profile all function calls
    CPU_SAMPLING = "sampling"  # Sample call stacks
    CPU_LINEBYLINE = "linebyline" # Line-by-line profiling on a subset of functions
    RPC_ONLY = "rpc"  # Profile all RPC calls
    RPC_AND_CPU_INSTRUMENTED = "rpc_instrumented" # RPCs and all fxn calls
    RPC_AND_CPU_SAMPLING = "rpc_sampling" # RPCs and sample call stacks
    RPC_AND_CPU_LINEBYLINE = "rpc_linebyline" # RPCs and line-by-line profiling

    @staticmethod
    def is_rpc_enabled(mode):
        return mode in [
                Mode.RPC_ONLY,
                Mode.RPC_AND_CPU_INSTRUMENTED,
                Mode.RPC_AND_CPU_SAMPLING,
                Mode.RPC_AND_CPU_LINEBYLINE]

    @staticmethod
    def is_sampling_enabled(mode):
        return mode in [
                Mode.CPU_SAMPLING,
                Mode.RPC_AND_CPU_SAMPLING]

    @staticmethod
    def is_instrumented_enabled(mode):
        return mode in [
                Mode.CPU_INSTRUMENTED,
                Mode.RPC_AND_CPU_INSTRUMENTED]

    @staticmethod
    def is_linebyline_enabled(mode):
        return mode in [
                Mode.CPU_LINEBYLINE,
                Mode.RPC_AND_CPU_LINEBYLINE]


_config = lib_config.register("gae_mini_profiler", {
    # Default to disabling in production if this function isn't overridden.
    "should_profile_production": lambda: False,
    # Default to enabling in development if this function isn't overridden.
    "should_profile_development": lambda: True})


_mode = lib_config.register("gae_mini_profiler", {
    "get_default_mode_production": lambda: Mode.RPC_AND_CPU_SAMPLING,
    "get_default_mode_development": lambda: Mode.RPC_AND_CPU_INSTRUMENTED})


_DEVELOPMENT_SERVER = os.environ.get("SERVER_SOFTWARE", "").startswith("Devel")


def should_profile():
    """Returns true if the current request should be profiles."""
    if _DEVELOPMENT_SERVER:
        return _config.should_profile_development()
    else:
        return _config.should_profile_production()


def get_mode(environ, cookies):
    """Returns the profiling mode in by current request's headers & cookies.

    If not set explicitly, calls gae_mini_profiler_get_default_mode_development / production"""
    if "HTTP_G_M_P_MODE" in environ:
        mode = environ["HTTP_G_M_P_MODE"]
    else:
        mode = cookies.get_cookie_value("g-m-p-mode")

    if (mode in [
            Mode.SIMPLE,
            Mode.CPU_INSTRUMENTED,
            Mode.CPU_SAMPLING,
            Mode.CPU_LINEBYLINE,
            Mode.RPC_ONLY,
            Mode.RPC_AND_CPU_INSTRUMENTED,
            Mode.RPC_AND_CPU_SAMPLING,
            Mode.RPC_AND_CPU_LINEBYLINE]):
        return mode

    if _DEVELOPMENT_SERVER:
        return _mode.get_default_mode_development()
    else:
        return _mode.get_default_mode_production()
