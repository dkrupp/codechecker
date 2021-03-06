# CodeChecker

First of all, you have to setup the environment for CodeChecker.
CodeChecker uses SQLite database (by default) to store the results
which is also packed into the package.

Running CodeChecker is via its main invocation script, `CodeChecker`:

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker [-h]
                   {checkers,analyze,analyzers,check,cmd,log,parse,plist,quickcheck,server,store,version}
                   ...

Run the CodeChecker sourcecode analyzer framework.
Please specify a subcommand to access individual features.

positional arguments:
  {checkers,analyze,analyzers,check,cmd,log,parse,plist,quickcheck,server,store,version}
                        commands
    checkers            List the available checkers for the supported
                        analyzers and show their default status (+ for being
                        enabled, - for being disabled by default).
    analyze             Execute the supported code analyzers for the files
                        recorded in a JSON Compilation Database.
    analyzers           List supported and available analyzers.
    check               Perform analysis on a project and store results to
                        database.
    cmd                 View analysis results on a running server from the
                        command line.
    log                 Run a build command and collect the executed
                        compilation commands, storing them in a JSON file.
    parse               Print analysis summary and results in a human-readable
                        format.
    plist               Use plist files in a given directory to pretty-print
                        or store the results.
    quickcheck          Perform analysis on a project and print results to
                        standard output.
    server              Start and manage the CodeChecker Web server.
    store               Save analysis results to a database.
    version             Print the version of CodeChecker package that is being
                        used.

optional arguments:
  -h, --help            show this help message and exit

Example scenario: Analyzing, and storing results
------------------------------------------------
Start the server where the results will be stored and can be viewed
after the analysis is done:
    CodeChecker server

Analyze a project with default settings:
    CodeChecker check -b "cd ~/myproject && make" -n myproject

The results can be viewed:
 * In a web browser: http://localhost:8001
 * In the command line:
    CodeChecker cmd results -p 8001 -n myproject

Example scenario: Analyzing, and printing results to Terminal (no storage)
--------------------------------------------------------------------------
In this case, no database is used, and the results are printed on the standard
output.

    CodeChecker quickcheck -b "cd ~/myproject && make"
~~~~~~~~~~~~~~~~~~~~~


## Default configuration

Used ports:
* `5432` - PostgreSQL
* `8001` - CodeChecker result viewer

# Easy analysis wrappers

CodeChecker provides, along with the more fine-tuneable commands, some easy
out-of-the-box invocations to ensure the most user-friendly operation. These
two modes are called **check** and **quickcheck**.

## Check

`check` is the basic, most used and most important command used in
_CodeChecker_. It analyzes your project and stores the reported code defects
in a database, which can be viewed in a Web Browser later on (via `CodeChecker
server`), the server should be started before the `check` command is executed:

~~~~~~~~~~~~~~~~~~~~~
CodeChecker server
~~~~~~~~~~~~~~~~~~~~~

To analyse your project by doing a build and reporting every
found issue in the built files, execute:

~~~~~~~~~~~~~~~~~~~~~
CodeChecker check --build "make" --name "run_name"
~~~~~~~~~~~~~~~~~~~~~

Please make sure your build command actually compiles (builds) the source
files you intend to analyse, as CodeChecker only analyzes files that had been
used by the build system.

If you have an already existing JSON Compilation Commands file, you can also
supply it to `check`:

~~~~~~~~~~~~~~~~~~~~~
CodeChecker check --logfile ./my-build.json --name "run_name"
~~~~~~~~~~~~~~~~~~~~~

`check` is a wrapper over the following calls:

 * If `--build` is specified, the build is executed as if `CodeChecker log`
   were invoked.
 * The resulting logfile, or a `--logfile` specified is used for `CodeChecker
   analyze`
 * The analysis results are feeded for `CodeChecker store`.

After the results has been stored in the database, the temporary files
used for the analysis are cleaned up.

Please see the individual help for `log`, `analyze` and `store` (below in this
_User guide_) for information about the arguments of `check`.

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker check [-h] [--keep-tmp] [-c] [--update] -n NAME
                         [-w WORKSPACE] [-f] [-q] (-b COMMAND | -l LOGFILE)
                         [-j JOBS] [-i SKIPFILE]
                         [--analyzers ANALYZER [ANALYZER ...]]
                         [--add-compiler-defaults]
                         [--saargs CLANGSA_ARGS_CFG_FILE]
                         [--tidyargs TIDY_ARGS_CFG_FILE]
                         [-e checker/checker-group] [-d checker/checker-group]
                         [-u SUPPRESS] [--host HOST] [-p PORT]
                         [--verbose {info,debug,debug_analyzer}]

Run analysis for a project with storing results in the database. Check only
needs a build command or an already existing logfile and performs every step
of doing the analysis in batch.

optional arguments:
  -h, --help            show this help message and exit
  --keep-tmp
  -c , --clean
  --update
  -n NAME, --name NAME
  -w WORKSPACE, --workspace WORKSPACE
                        Directory where CodeChecker can store analysis related
                        data, such as intermediate result files and the
                        database. (default: /home/<username>/.codechecker)
  -f, --force
  -u SUPPRESS, --suppress SUPPRESS
  --verbose {info,debug,debug_analyzer}
                        Set verbosity level. (default: info)

log arguments:

  -q, --quiet-build
  -b COMMAND, --build COMMAND
  -l LOGFILE, --logfile LOGFILE

analyzer arguments:

  -j JOBS, --jobs JOBS
  -i SKIPFILE, --skip SKIPFILE
  --analyzers ANALYZER [ANALYZER ...]
  --add-compiler-defaults
  --saargs CLANGSA_ARGS_CFG_FILE
  --tidyargs TIDY_ARGS_CFG_FILE

checker configuration:

  -e checker/checker-group, --enable checker/checker-group
  -d checker/checker-group, --disable checker/checker-group

server arguments:

  --host HOST
  -p PORT, --port PORT
~~~~~~~~~~~~~~~~~~~~~

## Quickcheck

It is possible to easily analyse the project for defects without keeping the
temporary analysis files and without using any database to store the reports
in, but instead printing the found issues to the standard output.

To analyse your project by doing a build and reporting every found issue in the
built files, execute

~~~~~~~~~~~~~~~~~~~~~
CodeChecker quickcheck --build "make"
~~~~~~~~~~~~~~~~~~~~~

Please make sure your build command actually compiles (builds) the source
files you intend to analyse, as CodeChecker only analyzes files that had been
used by the build system.

If you have an already existing JSON Compilation Commands file, you can also
supply it to `quickcheck`:

~~~~~~~~~~~~~~~~~~~~~
CodeChecker quickcheck --logfile ./my-build.json
~~~~~~~~~~~~~~~~~~~~~

By default, only the report's main messages are printed. To print the
individual steps the analysers took in discovering the issue, specify
`--steps`.

`quickcheck` is a wrapper over the following calls:

 * If `--build` is specified, the build is executed as if `CodeChecker log`
   were invoked.
 * The resulting logfile, or a `--logfile` specified is used for `CodeChecker
   analyze`
 * The analysis results are feeded for `CodeChecker parse`.

After the results has been printed to the standard output, the temporary files
used for the analysis are cleaned up.

Please see the individual help for `log`, `analyze` and `parse` (below in this
_User guide_) for information about the arguments of `quickcheck`.

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker quickcheck [-h] [-q] (-b COMMAND | -l LOGFILE)
                              [-j JOBS] [-i SKIPFILE]
                              [--analyzers ANALYZER [ANALYZER ...]]
                              [--add-compiler-defaults]
                              [--saargs CLANGSA_ARGS_CFG_FILE]
                              [--tidyargs TIDY_ARGS_CFG_FILE]
                              [-e checker/checker-group]
                              [-d checker/checker-group] [-u SUPPRESS] [-s]
                              [--verbose {info,debug,debug_analyzer}]

Run analysis for a project with printing results immediately on the standard
output. Quickcheck only needs a build command or an already existing logfile
and performs every step of doing the analysis in batch.

optional arguments:
  -h, --help            show this help message and exit
  --verbose {info,debug,debug_analyzer}
                        Set verbosity level. (default: info)

log arguments:

  -q, --quiet-build
  -b COMMAND, --build COMMAND
  -l LOGFILE, --logfile LOGFILE

analyzer arguments:

  -j JOBS, --jobs JOBS
  -i SKIPFILE, --skip SKIPFILE
  --analyzers ANALYZER [ANALYZER ...]
  --add-compiler-defaults
  --saargs CLANGSA_ARGS_CFG_FILE
  --tidyargs TIDY_ARGS_CFG_FILE

checker configuration:

  -e checker/checker-group, --enable checker/checker-group
  -d checker/checker-group, --disable checker/checker-group

output arguments:

  -u SUPPRESS, --suppress SUPPRESS
  -s, --steps, --print-steps
~~~~~~~~~~~~~~~~~~~~~

# Available CodeChecker commands

## 1. `log` mode

The first step in performing an analysis on your project is to record
information about the files in your project for the analyzers. This is done by
recording a build of your project, which is done by the command `CodeChecker
log`.

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker log [-h] -o LOGFILE -b COMMAND [-q]
                       [--verbose {info,debug,debug_analyzer}]

Runs the given build command and records the executed compilation steps. These
steps are written to the output file in a JSON format. Available build logger
tool that will be used is '...'.

optional arguments:
  -h, --help            show this help message and exit
  -o LOGFILE, --output LOGFILE
                        Path of the file to write the collected compilation
                        commands to. If the file already exists, it will be
                        overwritten.
  -b COMMAND, --build COMMAND
                        The build command to execute. Build commands can be
                        simple calls to 'g++' or 'clang++' or 'make', but a
                        more complex command, or the call of a custom script
                        file is also supported.
  -q, --quiet-build     Do not print the output of the build tool into the
                        output of this command. (default: False)
  --verbose {info,debug,debug_analyzer}
                        Set verbosity level. (default: info)
~~~~~~~~~~~~~~~~~~~~~

Please note, that only the files that are used in the given `--build` argument
will be recorded. To analyze your whole project, make sure your build tree has
been cleaned before executing `log`.

You can change the compilers that should be logged.
Set `CC_LOGGER_GCC_LIKE` environment variable to a colon separated list.
For example (default):

~~~~~~~~~~~~~~~~~~~~~
export CC_LOGGER_GCC_LIKE="gcc:g++:clang"
~~~~~~~~~~~~~~~~~~~~~

Example:

~~~~~~~~~~~~~~~~~~~~~
CodeChecker log -o ../codechecker_myProject_build.log -b "make -j2"
~~~~~~~~~~~~~~~~~~~~~

## 2. `analyze` mode

After a JSON Compilation Command Database has been created, the next step is
to invoke and execute the analyzers. CodeChecker will use the specified
`logfile`s (there can be multiple given) and create the outputs to the
`--output` directory. (These outputs will be `plist` files, currently only
these are supported.) The machine-readable output files can be used later on
for printing an overview in the terminal (`CodeChecker parse`) or storing
(`CodeChecker store`) analysis results in a database, which can later on be
viewed in a browser.

Example:

~~~~~~~~~~~~~~~~~~~~~
CodeChecker analyze ../codechecker_myProject_build.log -o my_plists
~~~~~~~~~~~~~~~~~~~~~

`CodeChecker analyze` supports a myriad of fine-tuning arguments, explained
below:

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker analyze [-h] [-j JOBS] [-i SKIPFILE] [-o OUTPUT_PATH]
                           [-t {plist}] [-n NAME]
                           [--analyzers ANALYZER [ANALYZER ...]]
                           [--add-compiler-defaults]
                           [--saargs CLANGSA_ARGS_CFG_FILE]
                           [--tidyargs TIDY_ARGS_CFG_FILE]
                           [--ctu | --ctu-collect | --ctu-analyze]
                           [--ctu-on-the-fly] [-e checker/checker-group]
                           [-d checker/checker-group] [--enable-all]
                           [--verbose {info,debug,debug_analyzer}]
                           logfile [logfile ...]

Use the previously created JSON Compilation Database to perform an analysis on
the project, outputting analysis results in a machine-readable format.

positional arguments:
  logfile               Path to the JSON compilation command database files
                        which were created during the build. The analyzers
                        will check only the files registered in these build
                        databases.

optional arguments:
  -h, --help            show this help message and exit
  -j JOBS, --jobs JOBS  Number of threads to use in analysis. More threads
                        mean faster analysis at the cost of using more memory.
                        (default: 1)
  -i SKIPFILE, --ignore SKIPFILE, --skip SKIPFILE
                        Path to the Skipfile dictating which project files
                        should be omitted from analysis. Please consult the
                        User guide on how a Skipfile should be laid out.
  -o OUTPUT_PATH, --output OUTPUT_PATH
                        Store the analysis output in the given folder.
                        (default: /home/<username>/.codechecker/reports)
  -t {plist}, --type {plist}, --output-format {plist}
                        Specify the format the analysis results should use.
                        (default: plist)
  -n NAME, --name NAME  Annotate the ran analysis with a custom name in the
                        created metadata file.
  --verbose {info,debug,debug_analyzer}
                        Set verbosity level. (default: info)
~~~~~~~~~~~~~~~~~~~~~

### _Skip_ file

~~~~~~~~~~~~~~~~~~~~~
-s SKIPFILE, --ignore SKIPFILE, --skip SKIPFILE
                      Path to the Skipfile dictating which project files
                      should be omitted from analysis.
~~~~~~~~~~~~~~~~~~~~~

Skipfiles filter which files should or should not be analyzed. CodeChecker
reads the skipfile from top to bottom and stops at the first matching pattern
when deciding whether or not a file should be analyzed.

Each line in the skip file begins with a `-` or a `+`, followed by a path glob
pattern. `-` means that if a file matches a pattern it should **not** be
checked, `+` means that it should be.

#### Example

~~~~~~~~~~~~~~~~~~~~~
-/skip/all/files/in/directory/*
-/do/not/check/this.file
+/dir/do.check.this.file
-/dir/*
~~~~~~~~~~~~~~~~~~~~~

In the above example, every file under `/dir` **will be** skipped, except the
one explicitly specified to **be analyzed** (`/dir/do.check.this.file`).

### Analyzer configuration

~~~~~~~~~~~~~~~~~~~~~
analyzer arguments:
  --analyzers ANALYZER [ANALYZER ...]
                        Run analysis only with the analyzers specified.
                        Currently supported analyzers are: clangsa, clang-
                        tidy.
  --add-compiler-defaults
                        Retrieve compiler-specific configuration from the
                        compilers themselves, and use them with Clang. This is
                        used when the compiler on the system is special, e.g.
                        when doing cross-compilation. (default: False)
  --saargs CLANGSA_ARGS_CFG_FILE
                        File containing argument which will be forwarded
                        verbatim for the Clang Static Analyzer.
  --tidyargs TIDY_ARGS_CFG_FILE
                        File containing argument which will be forwarded
                        verbatim for Clang-Tidy.
~~~~~~~~~~~~~~~~~~~~~

CodeChecker supports several analyzer tools. Currently, these analyzers are
the [_Clang Static Analyzer_](http://clang-analyzer.llvm.org) and
[_Clang-Tidy_](http://clang.llvm.org/extra/clang-tidy). `--analyzers` can be
used to specify which analyzer tool should be used (by default, all supported
are used). The tools are completely independent, so either can be omitted if
not present as they are provided by different binaries.

#### Compiler-specific include path and define detection (cross compilation)

Some of the include paths are hardcoded during compiler build. If a (cross)
compiler is used to build a project it is possible that the wrong include
paths are searched and the wrong headers will be included which causes
analyses to fail. These hardcoded include paths and defines can be marked for
automatically detection by specifying the `--add-compiler-defaults` flag.

CodeChecker will get the hardcoded values for the compilers set in the
`CC_LOGGER_GCC_LIKE` environment variable.

~~~~~~~~~~~~~~~~~~~~~
export CC_LOGGER_GCC_LIKE="gcc:g++:clang"
~~~~~~~~~~~~~~~~~~~~~

If there are still compilation errors after using the `--add-compiler-defaults`
argument, it is possible that the wrong build target architecture
(32bit, 64bit) is used. Please try to forward these compilation flags
to the analyzers:

 - `-m32` (32-bit build)
 - `-m64` (64-bit build)

#### Forwarding compiler options

Forwarded options can modify the compilation actions logged by the build logger
or created by CMake (when exporting compile commands). The extra compiler
options can be given in config files which are provided by the flags
described below.

The config files can contain placeholders in `$(ENV_VAR)` format. If the
`ENV_VAR` environment variable is set then the placeholder is replaced to its
value. Otherwise an error message is logged saying that the variable is not
set, and in this case an empty string is inserted in the place of the
placeholder.

##### _Clang Static Analyzer_

Use the `--saargs` argument to a file which contains compilation options.

~~~~
CodeChecker analyze mylogfile.json --saargs extra_sa_compile_flags.txt -n myProject
~~~~

Where the `extra_sa_compile_flags.txt` file contains additional compilation
options, for example:

~~~~~
-I~/include/for/analysis -I$(MY_LIB)/include -DDEBUG
~~~~~

(where `MY_LIB` is the path of a library code)

##### _Clang-Tidy_

Use the `--tidyargs` argument to a file which contains compilation options.

~~~~
CodeChecker analyze mylogfile.json --tidyargs extra_tidy_compile_flags.txt -n myProject
~~~~

Where the `extra_tidy_compile_flags.txt` file contains additional compilation
flags.

Clang-Tidy requires a different format to add compilation options.
Compilation options can be added before (`-extra-arg-before=<string>`) and
after (`-extra-arg=<string>`) the original compilation options.

Example:

~~~~
-extra-arg-before='-I~/include/for/analysis' -extra-arg-before='-I~/other/include/for/analysis/' -extra-arg-before='-I$(MY_LIB)/include' -extra-arg='-DDEBUG'
~~~~

(where `MY_LIB` is the path of a library code)

### Toggling checkers

The list of checkers to be used in the analysis can be fine-tuned with the
`--enable` and `--disable` options. See `codechecker-checkers` for the list of
available checkers in the binaries installed on your system.

~~~~~~~~~~~~~~~~~~~~~
checker configuration:

  -e checker/checker-group, --enable checker/checker-group
                        Set a checker (or checker group) to BE USED in the
                        analysis.
  -d checker/checker-group, --disable checker/checker-group
                        Set a checker (or checker group) to BE PROHIBITED from
                        use in the analysis.
  --enable-all          Force the running analyzers to use almost every
                        checker available. The checker groups 'alpha.',
                        'debug.' and 'osx.' (on Linux) are NOT enabled
                        automatically and must be EXPLICITLY specified.
                        WARNING! Enabling all checkers might result in the
                        analysis losing precision and stability, and could
                        even result in a total failure of the analysis. USE
                        WISELY AND AT YOUR OWN RISK!
~~~~~~~~~~~~~~~~~~~~~

Both `--enable` and `--disable` take individual checkers or checker groups as
their argument and there can be any number of such flags specified.

For example

~~~
--enable core --disable core.uninitialized --enable core.uninitialized.Assign
~~~

will enable every `core` checker which is not `core.uninitialized`, but
`core.uninitialized.Assign` will also be enabled.

Disabling certain checkers - such as the `core` group - is unsupported by
the LLVM/Clang community, and thus discouraged.

#### `--enable-all`

Specifying `--enable-all` will "force" CodeChecker to enable **every** checker
available in the analyzers. This presents an easy shortcut to force such an
analysis without the need of editing configuration files or supplying long
command-line arguments. However, `--enable-all` *might* result in the analysis
losing stability and precision, and worst case, might result in a complete and
utter failure in the analysis itself. **`--enable-all` may only be used at
your own risk!**

Even specifying `--enable-all` will **NOT** enable checkers from some special
checker groups, such as `alpha.` and `debug.`. `osx.` checkers are only enabled
if CodeChecker is ran on a macOS machine. `--enable-all` can further be
fine-tuned with subsequent `--enable` and `--disable` arguments, for example

~~~~
--enable-all --enable alpha --disable misc
~~~~

can be used to "further" enable `alpha.` checkers, and disable `misc` ones.

### Cross Translation Unit (CTU) analysis mode

If the `clang` static analyzer binary in your installation supports
[Cross Translation Unit analysis](http://llvm.org/devmtg/2017-03//2017/02/20/accepted-sessions.html#7),
CodeChecker can execute the analyzers with this mode enabled.

These options are only visible in `analyze` if CTU support is present. CTU
mode uses some extra storage space under the specified `--output-dir`.

~~~~~~~~~~~~~~~~~~~~~
cross translation unit analysis arguments:
  These arguments are only available if the Clang Static Analyzer supports
  Cross-TU analysis. By default, no such analysis is ran when 'CodeChecker
  analyze' is called.

  --ctu, --ctu-all      Perform Cross Translation Unit (CTU) analysis, both
                        'collect' and 'analyze' phases. In this mode, the
                        extra files created by 'collect' are cleaned up after
                        the analysis.
  --ctu-collect         Perform the first, 'collect' phase of Cross-TU
                        analysis. This phase generates extra files needed by
                        CTU analysis, and puts them into '<OUTPUT_DIR>/ctu-
                        dir'. NOTE: If this argument is present, CodeChecker
                        will NOT execute the analyzers!
  --ctu-analyze         Perform the second, 'analyze' phase of Cross-TU
                        analysis, using already available extra files in
                        '<OUTPUT_DIR>/ctu-dir'. (These files will not be
                        cleaned up in this mode.)
  --ctu-on-the-fly      If specified, the 'collect' phase will not create the
                        extra AST dumps, but rather analysis will be ran with
                        an in-memory recompilation of the source files.
                        (default: False)
~~~~~~~~~~~~~~~~~~~~~

## 3. `parse` mode

`parse` is used to read previously created machine-readable analysis results
(such as `plist` files), usually previously generated by `CodeChecker analyze`.
`parse` prints analysis results to the standard output.

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker parse [-h] [-t {plist}] [--suppress SUPPRESS]
                         [--export-source-suppress] [--print-steps]
                         [--verbose {info,debug,debug_analyzer}]
                         [file/folder [file/folder ...]]

Parse and pretty-print the summary and results from one or more 'codechecker-
analyze' result files.

positional arguments:
  file/folder           The analysis result files and/or folders containing
                        analysis results which should be parsed and printed.
                        (default: /home/<username>/.codechecker/reports)

optional arguments:
  -h, --help            show this help message and exit
  -t {plist}, --type {plist}, --input-format {plist}
                        Specify the format the analysis results were created
                        as. (default: plist)
  --suppress SUPPRESS   Path of the suppress file to use. Records in the
                        suppress file are used to suppress the display of
                        certain results when parsing the analyses' report.
                        (Reports to an analysis result can also be suppressed
                        in the source code -- please consult the manual on how
                        to do so.) NOTE: The suppress file relies on the "bug
                        identifier" generated by the analyzers which is
                        experimental, take care when relying on it.
  --export-source-suppress
                        Write suppress data from the suppression annotations
                        found in the source files that were analyzed earlier
                        that created the results. The suppression information
                        will be written to the parameter of '--suppress'.
  --print-steps         Print the steps the analyzers took in finding the
                        reported defect. (default: False)
  --verbose {info,debug,debug_analyzer}
                        Set verbosity level. (default: info)
~~~~~~~~~~~~~~~~~~~~~

For example, if the analysis was ran like:

~~~~
CodeChecker analyze ../codechecker_myProject_build.log -o my_plists
~~~~

then the results of the analysis can be printed with

~~~~
CodeChecker parse ./my_plists
~~~~

### _Suppress_ file

~~~~~~~~~~~~~~~~~~~~~
--suppress SUPPRESS   Path of the suppress file to use. Records in the
                      suppress file are used to suppress the display of
                      certain results when parsing the analyses' report.
                      NOTE: The suppress file relies on the "bug
                      identifier" generated by the analyzers which is
                      experimental, take care when relying on it.
~~~~~~~~~~~~~~~~~~~~~

Certain defects reported by the analyzers might only cause clutter in the
output, e.g. because they are false positive results, or some other reason why
we don't want to show them, such as the bug not being relevant to your project
as it happens in a library you use. (In case of false positives, please report
the false positive to us and/or the LLVM community so that the checker which
reported it could be investigated and fixed!)

Suppress files contain information about suppressed analysis reports in an
internal format, and a suppressed report will not be shown in the output by
default. Suppress files should not be edited manually, instead, a CodeChecker
viewer server should manage them, but the suppress file could be committed
into the source code repository for distribution to teammates.

If `--suppress` is specified, `parse` will use the given suppress file and
will not show reports on the standard output which are marked as suppressed.

### Suppression in the source code

Suppress comments can be used in the source files to suppress specific or all
checker results found in a particular line of code. Suppress comment should be
above the line where the defect was found, and no empty lines are allowed
between the line with the bug and the suppress comment.

Only comment lines staring with `//` are supported!

#### Supported formats

~~~~~~~~~~~~~~~~~~~~~
void test() {
  int x;
  // codechecker_suppress [deadcode.DeadStores] suppress deadcode
  x = 1; // warn
}
~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~
void test() {
  int x;
  // codechecker_suppress [all] suppress all checker results
  x = 1; // warn
}
~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~
void test() {
  int x;

  // codechecker_suppress [all] suppress all
  // checker resuls
  // with a long
  // comment
  x = 1; // warn
}
~~~~~~~~~~~~~~~~~~~~~

#### Exporting source code suppression to suppress file

~~~~~~~~~~~~~~~~~~~~~
  --export-source-suppress
                        Write suppress data from the suppression annotations
                        found in the source files that were analyzed earlier
                        that created the results. The suppression information
                        will be written to the parameter of '--suppress'.
~~~~~~~~~~~~~~~~~~~~~

Using `CodeChecker parse`, you can automatically generate a suppress file
(compatible with `parse`, `store` and `server`) from suppressions found in the
source code, by specifying `--export-source-suppress` along with a file path in
`--suppress`.

In case the file given as `--suppress` already exists, it will be extended with
the results, otherwise, a new file will be created.

~~~~
CodeChecker parse ./my_plists --suppress generated.suppress --export-source-suppress
~~~~

## 4. `store` mode

A `Codechecker server` needs to be started before the reports can be stored to
a database.

`store` is used to save previously created machine-readable analysis results
(such as `plist` files), usually previously generated by `CodeChecker analyze`
to the database.

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker store [-h] [-t {plist}] [-j JOBS] [-n NAME]
                         [--suppress SUPPRESS] [-f] [--host HOST] [-p PORT]
                         [--verbose {info,debug,debug_analyzer}]
                         [file/folder [file/folder ...]]

Store the results from one or more 'codechecker-analyze' result files in a
database.

positional arguments:
  file/folder           The analysis result files and/or folders containing
                        analysis results which should be parsed and printed.
                        (default: /home/<username>/.codechecker/reports)

optional arguments:
  -h, --help            show this help message and exit
  -t {plist}, --type {plist}, --input-format {plist}
                        Specify the format the analysis results were created
                        as. (default: plist)
  -j JOBS, --jobs JOBS  Number of threads to use in storing results. More
                        threads mean faster operation at the cost of using
                        more memory. (default: 1)
  -n NAME, --name NAME  The name of the analysis run to use in storing the
                        reports to the database. If not specified, the '--
                        name' parameter given to 'codechecker-analyze' will be
                        used, if exists.
  --suppress SUPPRESS   Path of the suppress file to use. Records in the
                        suppress file are used to mark certain stored analysis
                        results as 'suppressed'. (Reports to an analysis
                        result can also be suppressed in the source code --
                        please consult the manual on how to do so.) NOTE: The
                        suppress file relies on the "bug identifier" generated
                        by the analyzers which is experimental, take care when
                        relying on it.
  -f, --force           Delete analysis results stored in the database for the
                        current analysis run's name and store only the results
                        reported in the 'input' files. (By default,
                        CodeChecker would keep reports that were coming from
                        files not affected by the analysis, and only
                        incrementally update defect reports for source files
                        that were analysed.) (default: False)
  --verbose {info,debug,debug_analyzer}
                        Set verbosity level. (default: info)

server arguments:
  Specifies a 'CodeChecker server' instance which will be used to store the
  results. This server must be running and listening prior to the 'store'
  command being ran.

  --host HOST           The IP address or hostname of the CodeChecker server.
                        (default: localhost)
  -p PORT, --port PORT  The port of the server to use for storing. (default:
                        8001)

The results can be viewed by connecting to such a server in a Web browser or
via 'CodeChecker cmd'.
~~~~~~~~~~~~~~~~~~~~~

For example, if the analysis was ran like:

~~~~
CodeChecker analyze ../codechecker_myProject_build.log -o ./my_plists
~~~~

then the results of the analysis can be stored with this command:

~~~~
CodeChecker store ./my_plists -n my_project
~~~~


### Using SQLite for database:

CodeChecker can also use SQLite for storing the results. In this case the
SQLite database will be created in the workspace directory.

In order to use PostgreSQL instead of SQLite, use the `--postgresql` command
line argument for `CodeChecker server` command.
If `--postgresql` is not given then SQLite is used by default in
which case `--dbport`, `--dbaddress`, `--dbname`, and
`--dbusername` command line arguments are ignored.

#### Note:
Schema migration is not supported with SQLite. This means if you upgrade your
CodeChecker to a newer version, you might need to re-check your project.

### Various deployment possibilities

The CodeChecker server should be started on a separate machine.
In that case multiple clients can use the same database to store new results or view old ones.


#### Codechecker server and database on the same machine

Codechecker server and the database are running on the same machine but the database server is started manually.
In this case the database handler and the database can be started manually by running the server command.
The workspace needs to be provided for both the server and the check commands.

~~~~~~~~~~~~~~~~~~~~~
CodeChecker server -w ~/codechecker_wp --dbname myProjectdb --dbport 5432 --dbaddress localhost --view-port 8001
~~~~~~~~~~~~~~~~~~~~~

The checking process can be started separately on the same machine

~~~~~~~~~~~~~~~~~~~~~
CodeChecker check  -w ~/codechecker_wp -n myProject -b "make -j 4" --host localhost --port 8001
~~~~~~~~~~~~~~~~~~~~~

or on a different machine

~~~~~~~~~~~~~~~~~~~~~
CodeChecker check  -w ~/codechecker_wp -n myProject -b "make -j 4" --host 192.168.1.1 --dbport 8001
~~~~~~~~~~~~~~~~~~~~~


#### Codechecker server and database are on different machines

It is possible that the CodeChecker server and the PostgreSQL database that contains the analysis results are on different machines. To setup PostgreSQL see later section.

In this case the CodeChecker server can be started using the following command:

~~~~~~~~~~~~~~~~~~~~~
CodeChecker server --dbname myProjectdb --dbport 5432 --dbaddress 192.168.1.2 --view-port 8001
~~~~~~~~~~~~~~~~~~~~~

Start CodeChecker server locally which connects to a remote database (which is started separately). Workspace is not required in this case.


Start the checking as explained previously.

~~~~~~~~~~~~~~~~~~~~~
CodeChecker check -w ~/codechecker_wp -n myProject -b "make -j 4" --host 192.168.1.2 --port 8001
~~~~~~~~~~~~~~~~~~~~~

## 5. `checkers` mode

List the checkers available in the installed analyzers which can be used when
performing an analysis.

### Old `CodeChecker checkers` command

The ```+``` (or ```-```) sign before a name of a checker shows whether the
checker is enabled (or disabled) by default.

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker checkers [-h] [--analyzers ANALYZERS [ANALYZERS ...]]
                            [--verbose {info,debug,debug_analyzer}]

optional arguments:
  -h, --help            show this help message and exit
  --analyzers ANALYZERS [ANALYZERS ...]
                        Select which analyzer checkers should be listed.
                        Currently supported analyzers: clangsa clang-tidy
                        (default: None)
  --verbose {info,debug,debug_analyzer}
                        Set verbosity level. (default: info)
~~~~~~~~~~~~~~~~~~~~~

### New `codechecker-checkers` command

By default, `codechecker-checkers` will list all checkers, one per each row,
providing a quick overview on which checkers are available in the analyzers.

~~~~~~~~~~~~~~~~~~~~~
usage: codechecker-checkers [-h] [--analyzers ANALYZER [ANALYZER ...]]
                            [--details] [--only-enabled | --only-disabled]
                            [-o {rows,table,csv,json}]
                            [--verbose {info,debug,debug_analyzer}]

Get the list of checkers available and their enabled status in the supported
analyzers. Currently supported analyzers are: clangsa, clang-tidy.

optional arguments:
  -h, --help            show this help message and exit
  --analyzers ANALYZER [ANALYZER ...]
                        Show checkers only from the analyzers specified.
  --details             Show details about the checker, such as description,
                        if available. (default: False)
  --only-enabled        Show only the enabled checkers. (default: False)
  --only-disabled       Show only the disabled checkers. (default: False)
  -o {rows,table,csv,json}, --output {rows,table,csv,json}
                        The format to list the applicable checkers as.
                        (default: rows)
  --verbose {info,debug,debug_analyzer}
                        Set verbosity level. (default: info)
~~~~~~~~~~~~~~~~~~~~~

The list provided by default is formatted for easy machine and human
reading. Use the `--only-` options (`--only-enabled` and `--only-disabled`) to
filter the list if you wish to see just the enabled/disabled checkers.

A detailed view of the available checkers is available via `--details`. In the
*detailed view*, checker status, severity and description (if available) is
also printed.

A machine-readable `csv` or `json` output can be generated by supplying the
`--output csv` or `--output json` argument.

The _default_ list of enabled and disabled checkers can be altered by editing
`{INSTALL_DIR}/config/config.json`. Note, that this file is overwritten when
the package is reinstalled!

## 6. `analyzers` mode

List the available and supported analyzers installed on the system. This command
can be used to retrieve the to-be-used analyzers' install path and version
information.

By default, this command only lists the names of the available analyzers (with
respect to the environment CodeChecker is ran in).

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker analyzers [-h] [-a] [--details] [-o {rows,table,csv,json}]
                             [--verbose {info,debug,debug_analyzer}]

Get the list of available and supported analyzers, querying their version and
actual binary executed.

optional arguments:
  -h, --help            show this help message and exit
  -a, --all             Show all supported analyzers, not just the available
                        ones. (default: False)
  --details             Show details about the analyzers, not just their
                        names. (default: False)
  -o {rows,table,csv,json}, --output {rows,table,csv,json}
                        Specify the format of the output list. (default: rows)
  --verbose {info,debug,debug_analyzer}
                        Set verbosity level. (default: info)
~~~~~~~~~~~~~~~~~~~~~

A detailed view of the available analyzers is available via `--details`. In the
*detailed view*, version string and install path is also printed.

A machine-readable `csv` or `json` output can be generated by supplying the
`--output csv` or `--output json` argument.

## 7. `server` mode

To view and store the analysis reports in a database, a `CodeChecker server`
must be started. This is done via the `server` command, which creates a
standard Web server and initializes or connects to a database with
the given configuration.

The CodeChecker Viewer server can be browsed by a Web browser by opening the
address of it (by default, [`http://localhost:8001`](http://localhost:8001)),
or via the `CodeChecker cmd` command-line client.

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker server [-h] [-w WORKSPACE] [-f CONFIG_DIRECTORY]
                          [--host LISTEN_ADDRESS] [-v PORT] [--not-host-only]
                          [-u SUPPRESS] [--sqlite SQLITE_FILE | --postgresql]
                          [--dbaddress DBADDRESS] [--dbport DBPORT]
                          [--dbusername DBUSERNAME] [--dbname DBNAME]
                          [-l | -s | --stop-all]
                          [--verbose {info,debug,debug_analyzer}]

The CodeChecker Web server is used to handle the storage and navigation of
analysis results. A started server can be connected to via a Web browser, or
by using the 'CodeChecker cmd' command-line client.

optional arguments:
  -h, --help            show this help message and exit
  -w WORKSPACE, --workspace WORKSPACE
                        Directory where CodeChecker can store analysis result
                        related data, such as the database. (Cannot be
                        specified at the same time with '--sqlite' or
                        '--config-directory'.) (default:
                        /home/<username>/.codechecker)
  -f CONFIG_DIRECTORY, --config-directory CONFIG_DIRECTORY
                        Directory where CodeChecker server should read server-
                        specific configuration (such as authentication
                        settings) from. (default: /home/<username>/.codechecker)
  --host LISTEN_ADDRESS
                        The IP address or hostname of the server on which it
                        should listen for connections. (default: localhost)
  -v PORT, --view-port PORT, -p PORT, --port PORT
                        The port which will be used as listen port for the
                        server. (default: 8001)
  --not-host-only       If specified, storing and viewing the results will be
                        possible not only by browsers and clients running
                        locally, but to everyone, who can access the server
                        over the Internet. (Equivalent to specifying '--host
                        ""'.) (default: False)
  -u SUPPRESS, --suppress SUPPRESS
                        Path of the suppress file to use. The suppress file is
                        used to store which analysis results are marked
                        'suppressed', which is a distinct category on the
                        result viewing interface. NOTE: The suppress file
                        relies on the "bug identifier" generated by the
                        analyzers which is experimental, take care when
                        relying on it.
  --verbose {info,debug,debug_analyzer}
                        Set verbosity level. (default: info)

database arguments:
  --sqlite SQLITE_FILE  Path of the SQLite database file to use. (default:
                        /home/<username>/.codechecker/codechecker.sqlite)
  --postgresql          Specifies that a PostgreSQL database is to be used
                        instead of SQLite. See the "PostgreSQL arguments"
                        section on how to configure the database connection.

PostgreSQL arguments:
  Values of these arguments are ignored, unless '--postgresql' is specified!

  --dbaddress DBADDRESS, --db-host DBADDRESS
                        Database server address. (default: localhost)
  --dbport DBPORT, --db-port DBPORT
                        Database server port. (default: 5432)
  --dbusername DBUSERNAME, --db-username DBUSERNAME
                        Username to use for connection. (default: codechecker)
  --dbname DBNAME, --db-name DBNAME
                        Name of the database to use. (default: codechecker)
~~~~~~~~~~~~~~~~~~~~~

To start a server with default configuration, simply execute

~~~~~~~~~~~~~~~~~~~~~
CodeChecker server
~~~~~~~~~~~~~~~~~~~~~

### Creating a public server

~~~~~~~~~~~~~~~~~~~~~
  --host LISTEN_ADDRESS
                        The IP address or hostname of the server on which it
                        should listen for connections. (default: localhost)
  --not-host-only       If specified, viewing the results will be possible not
                        only by browsers and clients running locally, but to
                        everyone, who can access the server over the Internet.
                        (Equivalent to specifying '--host ""'.) (default:
                        False)
~~~~~~~~~~~~~~~~~~~~~

By default, the running server can only be accessed from the same machine
(`localhost`) where it is running. This can be overridden by specifying
`--host ""`, instructing the server to listen on all available interfaces.

### Configuring database and server settings' location

The `--sqlite` (or `--postgresql` and the various `--db-` arguments) can be
used to specify where the database, containing the analysis reports is.

`--config-directory` specifies where the server configuration files, such as
[authentication config](docs/authentication.md) is. E.g., one can start two
servers with two different databases, but with the same configuration:

~~~~~~~~~~~~~~~~~~~~~
CodeChecker server --sqlite ~/major_bugs.sqlite -f ~/.codechecker -p 8001
CodeChecker server --sqlite ~/minor_bugs.sqlite -f ~/.codechecker -p 8002
~~~~~~~~~~~~~~~~~~~~~

The `--workspace` argument can be used to _shortcut_ this specification: by
default, the configuration directory is the _workspace_ itself, and therein
resides the `codechecker.sqlite` file, containing the analysis reports.

### Managing running servers

~~~~~~~~~~~~~~~~~~~~~
running server management:
  -l, --list            List the servers that has been started by you.
  -s, --stop            Stops the server associated with the given view-port
                        and workspace.
  --stop-all            Stops all of your running CodeChecker server
                        instances.
~~~~~~~~~~~~~~~~~~~~~

CodeChecker servers can be started in the background as any other service, via
common Shell tools, such as `nohup` and `&!`. The running instances can be
queried via `--list`.

Calling `CodeChecker server --stop` will stop the "default" server, i.e. one
that was started by simply calling `CodeChecker server`. This _"stop"_ command
is equivalent to pressing `Ctrl`-`C` in the server's terminal, resulting in an
immediate termination of the server.

A server running on a specific and port can be stopped by:

~~~~~~~~~~~~~~~~~~~~~
CodeChecker server -w ~/my_codechecker_workspace -p 8002 --stop
~~~~~~~~~~~~~~~~~~~~~

`--stop-all` will stop every running server that is printed by `--list`.

## 8. `cmd` mode

The `CodeChecker cmd` is a lightweight command line client that can be used to
view analysis results from the command-line. The command-line client can also
be integrated into a continuous integration loop or can be used to schedule
maintenance tasks.

Most of the features available in a Web browser opening the analysis result
viewer server on its port is available in the `cmd` tool.

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker cmd [-h] {runs,results,diff,sum,del,suppress,login} ...

The command-line client is used to connect to a running 'CodeChecker server'
(either remote or local) and quickly inspect analysis results, such as runs,
individual defect reports, compare analyses, etc. Please see the invidual
subcommands for further details.

optional arguments:
  -h, --help            show this help message and exit

available actions:
  {runs,results,diff,sum,del,login}
    runs                List the available analysis runs.
    results             List analysis result (finding) summary for a given
                        run.
    diff                Compare two analysis runs and show the difference.
    sum                 Show number of reports per checker.
    del                 Delete analysis runs.
    suppress            Manage and export/import suppressions of a CodeChecker
                        server.
    login               Authenticate into CodeChecker servers that require
                        privileges.
~~~~~~~~~~~~~~~~~~~~~

The operations available in `cmd` **always** require a running CodeChecker
viewer server (i.e. a server started by `CodeChecker server`), and the
connection details (`--host` and `--port`) to access the server.

Most result-giving commands also take an `--output` format parameter. If this
is set to `json`, a more detailed output is given, in JSON format.

~~~~~~~~~~~~~~~~~~~~~
common arguments:
  --host HOST           The address of the CodeChecker viewer server to
                        connect to. (default: localhost)
  -p PORT, --port PORT  The port the server is running on. (default: 8001)
  -o {plaintext,rows,table,csv,json}, --output {plaintext,rows,table,csv,json}
                        The output format to use in showing the data.
                        (default: plaintext)
  --verbose {info,debug,debug_analyzer}
                        Set verbosity level. (default: info)
~~~~~~~~~~~~~~~~~~~~~

### List runs (`runs`)

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker cmd runs [-h] [--host HOST] [-p PORT]
                            [-o {plaintext,rows,table,csv,json}]
                            [--verbose {info,debug,debug_analyzer}]

List the analysis runs available on the server.
~~~~~~~~~~~~~~~~~~~~~

### List analysis results' summary (`results`)

Prints basic information about analysis results, such as location, checker
name, summary.

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker cmd results [-h] -n RUN_NAME [-s] [--filter FILTER]
                               [--host HOST] [-p PORT]
                               [-o {plaintext,rows,table,csv,json}]
                               [--verbose {info,debug,debug_analyzer}]

Show the individual analysis reports' summary.

optional arguments:
  -h, --help            show this help message and exit
  -n RUN_NAME, --name RUN_NAME
                        Name of the analysis run to show result summaries of.
                        Use 'CodeChecker cmd runs' to get the available runs.
                        (default: None)
  -s, --suppressed      Filter results to only show suppressed entries.
                        (default: False)
  --filter FILTER       Filter results. The filter string has the following
                        format: <severity>:<checker_name>:<file_path>
                        (default: ::)
~~~~~~~~~~~~~~~~~~~~~

### Show differences between two runs (`diff`)

This mode shows analysis results (in the same format as `results`) does, but
from the comparison of two runs.

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker cmd diff [-h] -b BASE_RUN -n NEW_RUN [-s] [--filter FILTER]
                            (--new | --resolved | --unresolved) [--host HOST]
                            [-p PORT] [-o {plaintext,rows,table,csv,json}]
                            [--verbose {info,debug,debug_analyzer}]

Compare two analysis runs to show the results that differ between the two.

optional arguments:
  -h, --help            show this help message and exit
  -b BASE_RUN, --basename BASE_RUN
                        The 'base' (left) side of the difference: this
                        analysis run is used as the initial state in the
                        comparison.
  -n NEW_RUN, --newname NEW_RUN
                        The 'new' (right) side of the difference: this
                        analysis run is compared to the -b/--basename run.
                        The parameter can be a run name(on the remote server) 
                        or a local report directory (result of the analyze
                        command).
  -s, --suppressed      Filter results to only show suppressed entries.
                        (default: False)
  --filter FILTER       Filter results. The filter string has the following
                        format: <severity>:<checker_name>:<file_path>
                        (default: ::)

comparison modes:
  --new                 Show results that didn't exist in the 'base' but
                        appear in the 'new' run.
  --resolved            Show results that existed in the 'base' but
                        disappeared from the 'new' run.
  --unresolved          Show results that appear in both the 'base' and the
                        'new' run.
~~~~~~~~~~~~~~~~~~~~~

The command can be used in *local* or *remote* compare modes.

In *local mode* the results of a local analysis (see `CodeChecker analyze`)
can be compared to the results stored (see `CodeChecker store`) on a remote
CodeChecker server:

~~~~~~~~~~~~~~~~~~~~~
CodeChecker cmd diff -p 8001 --basename my_project --newname ./my_updated_plists --new
~~~~~~~~~~~~~~~~~~~~~

In *remote* compare mode, two runs stored on a remote CodeChecker server can
be compared to each other:

~~~~~~~~~~~~~~~~~~~~~
CodeChecker cmd diff -p 8001 --basename my_project --newname my_new_checkin --new
~~~~~~~~~~~~~~~~~~~~~

### Show summarised count of results (`sum`)

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker cmd sum [-h] (-n RUN_NAME [RUN_NAME ...] | -a) [-s]
                           [--filter FILTER] [--host HOST] [-p PORT]
                           [-o {plaintext,rows,table,csv,json}]
                           [--verbose {info,debug,debug_analyzer}]

Show the count of checker reports per checker for some analysis runs.

optional arguments:
  -h, --help            show this help message and exit
  -n RUN_NAME [RUN_NAME ...], --name RUN_NAME [RUN_NAME ...]
                        Names of the analysis runs to show result count
                        breakdown for.
  -a, --all             Show breakdown for all analysis runs.
  -s, --suppressed      Filter results to only show suppressed entries.
                        (default: False)
  --filter FILTER       Filter results. The filter string has the following
                        format: <severity>:<checker_name>:<file_path>
                        (default: ::)
~~~~~~~~~~~~~~~~~~~~~

### Remove analysis runs (`del`)

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker cmd del [-h]
                           (-n RUN_NAME [RUN_NAME ...] |
                            --all-before-run RUN_NAME |
                            --all-after-run RUN_NAME |
                            --all-after-time TIMESTAMP |
                            --all-before-time TIMESTAMP)
                           [--host HOST] [-p PORT]
                           [--verbose {info,debug,debug_analyzer}]

Remove analysis runs from the server based on some criteria. NOTE! When a run
is deleted, ALL associated information is permanently lost!

optional arguments:
  -h, --help            show this help message and exit
  -n RUN_NAME [RUN_NAME ...], --name RUN_NAME [RUN_NAME ...]
                        Full name of the analysis run or runs to delete.
  --all-before-run RUN_NAME
                        Delete all runs that were stored to the server BEFORE
                        the specified one.
  --all-after-run RUN_NAME
                        Delete all runs that were stored to the server AFTER
                        the specified one.
  --all-after-time TIMESTAMP
                        Delete all analysis runs that were stored to the
                        server AFTER the given timestamp. The format of
                        TIMESTAMP is 'year:month:day:hour:minute:second' (the
                        "time" part can be omitted, in which case midnight
                        (00:00:00) is used).
  --all-before-time TIMESTAMP
                        Delete all analysis runs that were stored to the
                        server BEFORE the given timestamp. The format of
                        TIMESTAMP is 'year:month:day:hour:minute:second' (the
                        "time" part can be omitted, in which case midnight
                        (00:00:00) is used).
~~~~~~~~~~~~~~~~~~~~~

### Manage and export/import suppressions (`suppress`)

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker cmd suppress [-h] -n RUN_NAME [-f]
                                (-e SUPPRESS_FILE | -i SUPPRESS_FILE | --bugid BUGID)
                                [--file FILE] [-x] [-c COMMENT] [--host HOST]
                                [-p PORT]
                                [--verbose {info,debug,debug_analyzer}]

Exports or imports suppressions from a CodeChecker server from/to a suppress
file, and is also used (if '--bugid' is specified) to (un)suppress reports.

optional arguments:
  -h, --help            show this help message and exit
  -n RUN_NAME, --name RUN_NAME
                        Name of the analysis run to suppress or unsuppress a
                        report in.
  -f, --force           Enable suppression of already suppressed reports.
  -e SUPPRESS_FILE, --export SUPPRESS_FILE
                        Export into a suppress file from suppressions in the
                        server's database.
  -i SUPPRESS_FILE, --import SUPPRESS_FILE
                        Import suppression from the suppress file into the
                        database.
  --bugid BUGID         Manage suppression of the defect report based on its
                        ID.

per-report arguments:
  Options here are only applicable is '--bugid' is specified!

  --file FILE           Suppress/unsuppress the given report ONLY in the
                        specified file, instead of every occurrence of it.
  -x, --unsuppress      Unsuppress the specified report. (If not given,
                        default action is to suppress a report.)
  -c COMMENT, --comment COMMENT
                        Specify the (optional) comment which explains why the
                        given report is suppressed.
~~~~~~~~~~~~~~~~~~~~~

#### Export/import suppressions between server and suppress file


~~~~~~~~~~~~~~~~~~~~~
  -e SUPPRESS_FILE, --export SUPPRESS_FILE
                        Export into a suppress file from suppressions in the
                        server's database.
  -i SUPPRESS_FILE, --import SUPPRESS_FILE
                        Import suppression from the suppress file into the
                        database.
~~~~~~~~~~~~~~~~~~~~~

`--export` can be used to create a suppress file from the suppressions
stored in the database for a given run.

`--import` **appends** the suppressions found in the given suppress file to
the database on the server.

#### Suppress or unsuppress a particular bug report

~~~~~~~~~~~~~~~~~~~~~
  --bugid BUGID         Manage suppression of the defect report based on its
                        ID.

  --file FILE           Suppress/unsuppress the given report ONLY in the
                        specified file, instead of every occurrence of it.
  -x, --unsuppress      Unsuppress the specified report. (If not given,
                        default action is to suppress a report.)
  -c COMMENT, --comment COMMENT
                        Specify the (optional) comment which explains why the
                        given report is suppressed.
~~~~~~~~~~~~~~~~~~~~~

### Authenticate to the server (`login`)

~~~~~~~~~~~~~~~~~~~~~
usage: CodeChecker cmd login [-h] [-u USERNAME] [-d] [--host HOST] [-p PORT]
                             [--verbose {info,debug,debug_analyzer}]

Certain CodeChecker servers can require elevated privileges to access analysis
results. In such cases it is mandatory to authenticate to the server. This
action is used to perform an authentication in the command-line.

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        The username to authenticate with. (default: <username>)
  -d, --deactivate, --logout
                        Send a logout request to end your privileged session.
~~~~~~~~~~~~~~~~~~~~~

If a server [requires privileged access](docs/authentication.md), you must
log in before you can access the data on the particular server. Once
authenticated, your session is available for some time and `CodeChecker cmd`
can be used normally.

The password can be saved on the disk. If such "preconfigured" password is
not found, the user will be asked, in the command-line, to provide credentials.

# Advanced usage

## Run CodeChecker distributed in a cluster

You may want to configure CodeChecker to do the analysis on separate machines in a distributed way.
Start the postgres database on a central machine (in this example it is called codechecker.central) on a remotely accessible address and port and then run
```CodeChecker check``` on multiple machines (called host1 and host2), specify the remote dbaddress and dbport and use the same run name.

Create and start an empty database to which the CodeChecker server can connect.

## Setup PostgreSQL (one time only)

Before the first use, you have to setup PostgreSQL.
PostgreSQL stores its data files in a data directory, so before you start the PostgreSQL server you have to create and init this data directory.
I will call the data directory to pgsql_data.

Do the following steps:

~~~~~~~~~~~~~~~~~~~~~
# on machine codechecker.central

mkdir -p /path/to/pgsql_data
initdb -U codechecker -D /path/to/pgsql_data -E "SQL_ASCII"
# Start PostgreSQL server on port 5432
postgres -U codechecker -D /path/to/pgsql_data -p 5432 &>pgsql_log &
# Start the central CodeChecker server
CodeChecker server -w ~/codechecker_workspace --dbaddress localhost --dbport 5432 --view-port 8001
~~~~~~~~~~~~~~~~~~~~~

## Run CodeChecker on multiple hosts

Then you can run CodeChecker on multiple hosts but using the same run name (in this example this is called "distributed_run".
CodeChecker server is listening on codechecker.central port 8001.

~~~~~~~~~~~~~~~~~~~~~
# On host1 we check module1
CodeChecker check -w /tmp/codechecker_ws -b "cd module_1;make" --port 8001 --host codechecker.central -n distributed_run

# On host2 we check module2
CodeChecker check -w /tmp/codechecker_ws -b "cd module_2;make" --port 8001 --host codechecker.central -n disributed_run
~~~~~~~~~~~~~~~~~~~~~

### PostgreSQL authentication (optional)

If a CodeChecker is run with a user that needs database authentication, the
PGPASSFILE environment variable should be set to a pgpass file
For format and further information see PostgreSQL documentation:
http://www.postgresql.org/docs/current/static/libpq-pgpass.html

# Debugging CodeChecker

Command line flag can be used to turn in CodeChecker debug mode. The different
subcommands can be given a `-v` flag which needs a parameter. Possible values
are `debug`, `debug_analyzer` and `info`. Default is `info`.

`debug_analyzer` switches analyzer related logs on:

~~~~~~~~~~~~~~~~~~~~~
CodeChecker check -n <name> -b <build_command> --verbose debug_analyzer
~~~~~~~~~~~~~~~~~~~~~

Turning on CodeChecker debug level logging is possible for the most
subcommands:

~~~~~~~~~~~~~~~~~~~~~
CodeChecker check -n <name> -b <build_command> --verbose debug
CodeChecker server -v <view_port> --verbose debug
~~~~~~~~~~~~~~~~~~~~~

If debug logging is enabled and PostgreSQL database is used, PostgreSQL logs
are written to `postgresql.log` in the workspace directory.

Turn on SQL_ALCHEMY debug logging via the export below before calling
CodeChecker:

~~~~~~~~~~~~~~~~~~~~~
export CODECHECKER_ALCHEMY_LOG=True
~~~~~~~~~~~~~~~~~~~~~
