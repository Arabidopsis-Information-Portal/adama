# Configuration file for ipython.
from textwrap import dedent


c = get_config()

imports = dedent(
    r"""
    %load_ext autoreload
    %autoreload 2
    print('\n-- Autoreload extension activated')
    import channelpy
    import stores
    import tools
    """
)

c.InteractiveShellApp.exec_lines = imports.splitlines()