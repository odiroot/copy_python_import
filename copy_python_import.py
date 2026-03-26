import os
import re

import sublime
import sublime_plugin

CLASS_NAME_SELECTORS = (
    "entity.name.class.python",
    "entity.name.type.class.python",
)
FUNCTION_NAME_SELECTOR = "entity.name.function.python"
# Heuristic for top-level constants:
# all uppercase, optionally with digits and underscores,
TOP_LEVEL_CONSTANT_PATTERN = re.compile(
    r"^(?P<name>[A-Z][A-Z0-9_]*)\s*(?::[^=\n]+)?="
)


def _get_module_path(file_name):
    """Constructs the Python import path from a file's absolute path."""
    python_path_items = []
    head, tail = os.path.split(file_name)

    # Establish current module name.
    module = os.path.splitext(tail)[0]
    if module != "__init__":
        python_path_items.append(module)

    # Go up the directory tree...
    head, tail = os.path.split(head)

    while tail:
        try:
            # but only as long as we're in a Python package.
            if "__init__.py" in os.listdir(os.path.join(head, tail)):
                python_path_items.insert(0, tail)
            else:
                break
        except OSError:
            # Ignore directories that can't be read and stop traversing.
            break

        # Keep going up (chopping off the current package).
        head, tail = os.path.split(head)

    return python_path_items


class CopyPythonImportCommand(sublime_plugin.TextCommand):
    def _matches_any_selector(self, point, selectors):
        """Check if current point is at any of the given syntax selectors."""
        return any(
            self.view.match_selector(point, selector) for selector in selectors
        )

    def _find_regions_for_any_selector(self, selectors):
        """Find all regions in current editor that match given selectors."""
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
        """Find the name of the class from any point in its body."""
        class_name_regions = self._find_regions_for_any_selector(
            CLASS_NAME_SELECTORS
        )
        possible_class_point = 0

        for region in class_name_regions:
            if region.a < point:
                possible_class_point = region.a
            else:
                break  # We've gone past the cursor.

        # No class found between the cursor and the start of the file.
        if possible_class_point <= 0:
            return None

        # Guess: if cursor is more indented than the class, it's inside.
        class_indent = self.view.indentation_level(possible_class_point)
        cursor_indent = self.view.indentation_level(point)
        if cursor_indent <= class_indent:
            return None

        return self.view.substr(self.view.word(possible_class_point))

    def _get_top_level_variable_name(self, point):
        """Best effort search for the module-global variable under cursor."""
        # Globals generally won't be indented.
        if self.view.indentation_level(point) != 0:
            return None

        word_region = self.view.word(point)
        candidate = self.view.substr(word_region)

        # Quick check: "constants" are usually in all-caps.
        if not candidate or not candidate.isupper():
            return None

        line_region = self.view.line(point)
        line_text = self.view.substr(line_region)
        # Full (slower) check for the usual "constant" naming pattern.
        match = TOP_LEVEL_CONSTANT_PATTERN.match(line_text)
        if not match or match.group("name") != candidate:
            return None

        constant_region = sublime.Region(
            line_region.a + match.start("name"),
            line_region.a + match.end("name"),
        )
        if word_region != constant_region:
            return None

        return candidate

    def _get_symbol_path_items(self):
        """Determines the current symbol at the cursor."""
        caret_point = self.view.sel()[0].begin()
        path_items = []

        # Priority 1: Cursor is on a function/method name.
        if self.view.match_selector(caret_point, FUNCTION_NAME_SELECTOR):
            method_name = self.view.substr(self.view.word(caret_point))

            # Indented code: class method or nested function.
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

        # Priority 3: Cursor is possibly inside a class body.
        class_name = self._find_containing_class_name(caret_point)
        if class_name:
            path_items.append(class_name)
            return path_items

        # Priority 4: Cursor is on a top-level constant assignment.
        constant_name = self._get_top_level_variable_name(caret_point)
        if constant_name:
            path_items.append(constant_name)
            return path_items

        return path_items

    def _build_statement(self, module_part, symbol_path):
        """Builds import statement for the given module and symbol path."""

        # Module-only import if we couldn't find a symbol.
        if not symbol_path:
            return "import %s" % (module_part,)

        # If there are two items in the symbol path, assume it's a method and
        # import the class instead but offer a second line with
        # the method access.
        if len(symbol_path) == 2:
            class_name, method_name = symbol_path
            return "from %s import %s\n%s.%s" % (
                module_part,
                class_name,
                class_name,
                method_name,
            )

        # Symbol found in a module.
        symbol_part = ".".join(symbol_path)
        return "from %s import %s" % (module_part, symbol_part)

    def run(self, edit):
        """Copy the import statement for the symbol at the cursor."""
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

    def _enabled(self):
        # This command should only be enabled for Python files.
        matcher = "source.python"
        # Check the first selection (if any) since that's where the cursor is.
        return self.view.match_selector(self.view.sel()[0].begin(), matcher)

    def is_enabled(self):
        return self._enabled()

    def is_visible(self):
        return self._enabled()
