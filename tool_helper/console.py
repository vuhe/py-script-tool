import os


def for_print_path(root, curr) -> str:
    """"计算相对路径，用于优化打印输出"""
    # Normalize paths to eliminate trailing slashes and inconsistencies
    root = os.path.normpath(root)
    curr = os.path.normpath(curr)

    # Get the common prefix of the two paths
    common_prefix = os.path.commonpath([root, curr])

    # If the common path is the root, calculate the relative path
    if common_prefix == root:
        # Get the relative path from root to curr
        relative_path = os.path.relpath(curr, root)
        # Normalize to ensure the path is relative to the root directory
        return "./" + relative_path
    else:
        return "."
