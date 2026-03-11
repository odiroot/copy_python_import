# Copy Python Import

A Sublime Text package.

Puts the ready-made import statement for the current module, class or function 
in the clipboard.

Forked from [pokidovea/copy_python_path](https://github.com/pokidovea/copy_python_path)

# Install


The easiest way to install this is with [Package Control](http://wbond.net/sublime_packages/package_control).

# Usage
To copy the import line of the module select an option from the context menu of 
side bar or tab.
To copy the import line of the python class or method put caret on it and press 
<kbd>Ctrl+Alt+I</kbd> or `right-click` and select an option from the context 
menu.

# Testing

This package uses the standard Sublime Text 4
[UnitTesting](https://github.com/SublimeText/UnitTesting) package.

1. Install `UnitTesting` via Package Control.
2. Make this repo available as a Sublime package under your `Packages`
   directory, for example via a symlink:

   ```bash
   ln -s /path/to/copy_python_import \
     ~/.config/sublime-text/Packages/copy_python_import
   ```

   On macOS the `Packages` directory is usually:
   `~/Library/Application Support/Sublime Text/Packages`

   On Windows it is usually:
   `%APPDATA%\\Sublime Text\\Packages`
3. In Sublime Text, open the package from the `Packages` directory rather than
   from your original checkout location.
4. Run `UnitTesting: Test Current Package` from the Command Palette.

If you keep the repo outside `Packages`, `UnitTesting: Test Current Package`
cannot infer the package name from the active file path and will show
`Cannot determine package name.`

The tests live in `tests/test_copy_python_import.py` and exercise module,
function, class, method, and constant copying against a real `.py` file opened
inside Sublime Text.
