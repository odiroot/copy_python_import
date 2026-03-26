import os
import shutil
import tempfile
import textwrap

import sublime
from unittesting import DeferrableTestCase

SAMPLE_SOURCE = textwrap.dedent(
    """\
    FOO_BAR = "baz"
    foo_bar = "module fallback"

    def function_e():
        return FOO_BAR

    class ClassD:
        def method_e(self):
            return FOO_BAR
    """
)


class CopyPythonImportCommandTestCase(DeferrableTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.temp_dir = tempfile.mkdtemp(prefix="copy-python-import-")
        package_root = os.path.join(cls.temp_dir, "a")
        module_dir = os.path.join(package_root, "b")

        os.makedirs(module_dir)

        for path in (package_root, module_dir):
            with open(
                os.path.join(path, "__init__.py"),
                "w",
                encoding="utf-8",
            ):
                pass

        cls.module_path = os.path.join(module_dir, "c.py")
        with open(cls.module_path, "w", encoding="utf-8") as handle:
            handle.write(SAMPLE_SOURCE)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)
        super().tearDownClass()

    def setUp(self):
        self.previous_clipboard = sublime.get_clipboard()
        sublime.set_clipboard("")
        self.views_to_close = []

    def tearDown(self):
        sublime.set_clipboard(self.previous_clipboard)

        for view in self.views_to_close:
            window = view.window()
            if window is None:
                continue
            window.focus_view(view)
            window.run_command("close_file")

    def _open_sample_view(self):
        window = sublime.active_window()
        self.assertIsNotNone(window)

        view = window.open_file(self.module_path)
        self.views_to_close.append(view)

        yield lambda: not view.is_loading()
        yield lambda: view.match_selector(0, "source.python")

        return view

    def _move_cursor(self, view, needle, occurrence=1):
        offset = -1
        search_from = 0

        for _ in range(occurrence):
            offset = SAMPLE_SOURCE.index(needle, search_from)
            search_from = offset + len(needle)

        view.sel().clear()
        view.sel().add(sublime.Region(offset))

    def _assert_clipboard(self, view, expected):
        view.run_command("copy_python_import")
        self.assertEqual(sublime.get_clipboard(), expected)

    def test_copy_module_import(self):
        view = yield from self._open_sample_view()

        self._move_cursor(view, "foo_bar")

        self._assert_clipboard(view, "import a.b.c")

    def test_copy_function_import(self):
        view = yield from self._open_sample_view()

        self._move_cursor(view, "function_e")

        self._assert_clipboard(view, "from a.b.c import function_e")

    def test_copy_class_import(self):
        view = yield from self._open_sample_view()

        self._move_cursor(view, "ClassD")

        self._assert_clipboard(view, "from a.b.c import ClassD")

    def test_copy_method_reference(self):
        view = yield from self._open_sample_view()

        self._move_cursor(view, "method_e")

        self._assert_clipboard(
            view,
            "from a.b.c import ClassD\nClassD.method_e",
        )

    def test_copy_constant_import(self):
        view = yield from self._open_sample_view()

        self._move_cursor(view, "FOO_BAR")

        self._assert_clipboard(view, "from a.b.c import FOO_BAR")
