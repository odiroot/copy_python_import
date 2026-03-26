# Copy Python Import

A [Sublime Text 4](https://www.sublimetext.com/) package.

Copies a full Python import statement for the symbol under cursor to 
the clipboard.

Supports:

* classes,
* functions,
* methods [^1].
* module-global variables (sometimes called _constants_).
* modules [^2].


[^1]: For class methods, the import statement will point at a class, as 
importing methods directly is impossible.

[^2]: Current module is selected whenever no other syntax element 
(from the list above) can be identified. Thus _module_ is a fallback that 
always works.


# Install

> [!NOTE]
> Installation from the [Package Control](http://wbond.net/sublime_packages/package_control) 
> extension is not yet possible at this moment. Work in progress.

First find your Sublime Text packages directory. 
You can use the built in command:

1. Open _Command Palette_ 
   (e.g. <kbd>Ctrl+Shift+P</kbd> or _Tools_ -> _Command Palette_ in the menu.)
2. Select _Preferences: Browse Packages_
3. Copy the directory path from your file manager
   (e.g. `~/.config/sublime-text/Packages/`)

Now you have a few options to proceed.

## With Git

1. Open a shell and navigate to the aforementioned packages directory.
2. Run:

        git clone git@github.com:odiroot/copy_python_import.git copy_python_import

3. The package is already installed and running.

> [!NOTE]
> You can always update to the newest version by running `git pull`
> from inside of that `copy_python_import` directory.

## From a download

1. Open the [releases](https://github.com/odiroot/copy_python_import/releases) page.
2. Download _Source code (zip)_ for the newest release.
3. Unpack the ZIP archive.
4. Copy the `copy_python_import-master` directory to your Sublime Text package directory.
5. All done!

# Usage

Navigate with your keyboard or mouse to move the cursor to a symbol you want
to import. 

Then either:

1. press <kbd>Ctrl+Alt+I</kbd> (default) on your keyboard,
2. right click to open menu the context menu and click _Copy Python Import_.

# Configuration

These are the default key bindings to copy the import:

* <kbd>Ctrl+Alt+I</kbd> on Linux and Windows.
* <kbd>Super+Option+I</kbd> on Mac OS X.

You configure your own preferred key binding with _Preferences_ → _Key Bindings_
in Sublime Text menu. The command for this extension is called `copy_python_import`.

Example:

```json
[
    { "keys": ["ctrl+alt+i"], "command": "copy_python_import" }
]

```



# Disclaimer

Forked from [pokidovea/copy_python_path](https://github.com/pokidovea/copy_python_path)
