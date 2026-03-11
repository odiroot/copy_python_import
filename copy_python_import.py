import os

import sublime
import sublime_plugin

CLASS_NAME_SELECTORS = (
    "entity.name.class.python",
    "entity.name.type.class.python",
)
FUNCTION_NAME_SELECTOR = "entity.name.function.python"


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
    def _matches_any_selector(self, point, selectors):
        return any(
            self.view.match_selector(point, selector)
            for selector in selectors
        )

    def _find_regions_for_any_selector(self, selectors):
        regions = []
        seen = set()

        for selector in selectors:
            for region in self.view.find_by_selector(selector):
                key = (region.a, region.b)
                if key in seen:
                    continue
                seen.add(key)
                regions.append(region)

        return sorted(regions, key=lambda region: region.a)

    def _find_containing_class_name(self, point):
        class_name_regions = self._find_regions_for_any_selector(
            CLASS_NAME_SELECTORS
        )
        possible_class_point = 0

        for region in class_name_regions:
            if region.a < point:
                possible_class_point = region.a
            else:
                break  # We've gone past the cursor

        if possible_class_point <= 0:
            return None

        # Guess: if cursor is more indented than the class, it's inside.
        class_indent = self.view.indentation_level(possible_class_point)
        cursor_indent = self.view.indentation_level(point)
        if cursor_indent <= class_indent:
            return None

        return self.view.substr(self.view.word(possible_class_point))

    def run(self, edit):
        # Get the base module path from the file's location.
        module_path = _get_module_path(self.view.file_name())
        # Get the path of the symbol (class/function) at the cursor.
        symbol_path = self._get_symbol_path_items()

        if not module_path:
            # Can't import.
            sublime.status_message("Cannot determine module path.")
            return

        module_part = ".".join(module_path)

        statement = self._build_statement(module_part, symbol_path)

        # Copy to clipboard and show status.
        sublime.set_clipboard(statement)
        sublime.status_message('"%s" copied to clipboard' % statement)

    def _build_statement(self, module_part, symbol_path):
        if not symbol_path:
            return "import %s" % (module_part,)

        if len(symbol_path) == 2:
            class_name, method_name = symbol_path
            return "from %s import %s\n%s.%s" % (
                module_part,
                class_name,
                class_name,
                method_name,
            )

        symbol_part = ".".join(symbol_path)
        return "from %s import %s" % (module_part, symbol_part)

    def _get_symbol_path_items(self):
        """
        Determines the symbol (class/function) at the cursor, or the class
        containing the cursor.
        """
        caret_point = self.view.sel()[0].begin()
        path_items = []

        # Priority 1: Cursor is on a function/method name.
        if self.view.match_selector(caret_point, FUNCTION_NAME_SELECTOR):
            method_name = self.view.substr(self.view.word(caret_point))
            if self.view.indentation_level(caret_point) > 0:
                class_name = self._find_containing_class_name(caret_point)
                if class_name:
                    path_items.extend((class_name, method_name))
                else:
                    pass  # Nested function, do nothing.
            else:
                path_items.append(method_name)
            return path_items

        # Priority 2: Cursor is directly on a class name.
        if self._matches_any_selector(caret_point, CLASS_NAME_SELECTORS):
            path_items.append(self.view.substr(self.view.word(caret_point)))
            return path_items

        # Priority 3: Try to find a containing class.
        class_name = self._find_containing_class_name(caret_point)
        if class_name:
            path_items.append(class_name)
            return path_items

        return path_items

    def _enabled(self):
        # This command should only be enabled for Python files.
        matcher = "source.python"
        return self.view.match_selector(self.view.sel()[0].begin(), matcher)

    def is_enabled(self):
        return self._enabled()

    def is_visible(self):
        return self._enabled()
