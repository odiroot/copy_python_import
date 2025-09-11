import os
import sys

import sublime
import sublime_plugin


def _get_module_path(file_name):
    """Constructs the Python import path from a file's absolute path."""
    python_path_items = []
    head, tail = os.path.split(file_name)

    module = tail.rsplit(".", 1)[0]
    if module != "__init__":
        python_path_items.append(module)

    head, tail = os.path.split(head)

    while tail:
        try:
            if "__init__.py" in os.listdir(os.path.join(head, tail)):
                python_path_items.insert(0, tail)
            else:
                break
        except OSError:
            # Ignore directories that can't be read and stop traversing.
            break
        head, tail = os.path.split(head)

    return python_path_items


class CopyPythonImportCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Get the base module path from the file's location.
        module_path = _get_module_path(self.view.file_name())
        # Get the path of the symbol (class/function) at the cursor.
        symbol_path = self._get_symbol_path_items()

        if not module_path:
            # Can't import.
            sublime.status_message("Cannot determine module path.")
            return


        module_part = '.'.join(module_path)

        if symbol_path:
            symbol_part = '.'.join(symbol_path)
            statement = "from %s import %s" % (
                module_part, symbol_part
            )
        else:
            statement = "import %s" % (module_part)

        # Copy to clipboard and show status.
        sublime.set_clipboard(statement)
        sublime.status_message('"%s" copied to clipboard' % statement)

    def _get_symbol_path_items(self):
        """Determines the symbol (class/function) at the cursor."""
        caret_point = self.view.sel()[0].begin()
        scope = self.view.scope_name(caret_point)
        path_items = []

        class_entity = (
            "entity.name.class.python"
            if sys.version_info < (3, 0, 0)
            else "entity.name.type.class.python"
        )

        # Case 1: Cursor is on a class definition
        if class_entity in scope:
            path_items.append(self.view.substr(self.view.word(caret_point)))

        # Case 2: Cursor is on a function/method definition
        elif "entity.name.function.python" in scope:
            method_name = self.view.substr(self.view.word(caret_point))

            # If indented, it's a method, so find the parent class.
            if self.view.indentation_level(caret_point) > 0:
                regions = self.view.find_by_selector(class_entity)
                possible_class_point = 0
                for region in regions:
                    if region.b < caret_point:
                        possible_class_point = region.a
                    else:
                        break

                if possible_class_point > 0:
                    class_name = self.view.substr(
                        self.view.word(possible_class_point)
                    )
                    path_items.append(class_name)
                else:
                    # Just nested function.
                    path_items.append(method_name)
            else:
                path_items.append(method_name)

        return path_items

    def _enabled(self):
        # This command should only be enabled for Python files.
        matcher = "source.python"
        return self.view.match_selector(self.view.sel()[0].begin(), matcher)

    def is_enabled(self):
        return self._enabled()

    def is_visible(self):
        return self._enabled()
