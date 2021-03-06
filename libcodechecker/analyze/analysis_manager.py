# -------------------------------------------------------------------------
#                     The CodeChecker Infrastructure
#   This file is distributed under the University of Illinois Open Source
#   License. See LICENSE.TXT for details.
# -------------------------------------------------------------------------
"""
"""

from collections import defaultdict
import glob
import multiprocessing
import os
import signal
import sys
import traceback
import zipfile

from libcodechecker import util
from libcodechecker.analyze import analyzer_env
from libcodechecker.analyze.analyzers import analyzer_types
from libcodechecker.logger import LoggerFactory

LOG = LoggerFactory.get_new_logger('ANALYSIS MANAGER')


def worker_result_handler(results, metadata, output_path):
    """
    Print the analysis summary.
    """

    if metadata is None:
        metadata = {}

    successful_analysis = defaultdict(int)
    failed_analysis = defaultdict(int)
    skipped_num = 0

    buildactions = []
    for res, skipped, buildaction, result_file in results:
        buildactions.append(buildaction)
        if skipped:
            skipped_num += 1
        else:
            if res == 0:
                successful_analysis[buildaction.analyzer_type] += 1
            else:
                failed_analysis[buildaction.analyzer_type] += 1

    LOG.info("----==== Summary ====----")
    LOG.info("Total compilation commands: " + str(len(results)))
    if successful_analysis:
        LOG.info("Successfully analyzed")
        for analyzer_type, res in successful_analysis.items():
            LOG.info('  ' + analyzer_type + ': ' + str(res))

    if failed_analysis:
        LOG.info("Failed to analyze")
        for analyzer_type, res in failed_analysis.items():
            LOG.info('  ' + analyzer_type + ': ' + str(res))

    if skipped_num:
        LOG.info("Skipped compilation commands: " + str(skipped_num))
    LOG.info("----=================----")

    metadata['successful'] = successful_analysis
    metadata['failed'] = failed_analysis
    metadata['skipped'] = skipped_num

    # check() created the result .plist files and additional, per-analysis
    # meta information in forms of .plist.source files.
    # We now soak these files into the metadata dict, as they are not needed
    # as loose files on the disk... but synchronizing LARGE dicts between
    # threads would be more error prone.
    source_map = {}
    for f in glob.glob(os.path.join(output_path, "*.source")):
        with open(f, 'r') as sfile:
            source_map[f[:-7]] = sfile.read().strip()
        os.remove(f)

    metadata['result_source_files'] = source_map


def create_dependencies(action):
    """
    Transforms the given original build 'command' to a command that, when
    executed, is able to generate a dependency list.
    """
    if 'CC_LOGGER_GCC_LIKE' not in os.environ:
        os.environ['CC_LOGGER_GCC_LIKE'] = 'gcc:g++:clang:clang++:cc:c++'

    command = action.original_command.split(' ')
    if any(binary_substring in command[0] for binary_substring
           in os.environ['CC_LOGGER_GCC_LIKE'].split(':')):
        # gcc and clang can generate makefile-style dependency list.
        command = [command[0], '-E', '-M', '-MQ', '__dummy'] + command[1:]

        option_index = next(
            (i for i, c in enumerate(command) if c == '-o' or c == '--output'),
            None)

        if option_index:
            # If an output file is set, the dependency is not written to the
            # standard output but rather into the given file.
            # We need to first eliminate the output from the command.
            command = command[0:option_index] + command[option_index+2:]

        output, rc = util.call_command(command, env=os.environ)
        if rc == 0:
            # Parse 'Makefile' syntax dependency output.
            dependencies = output.replace('__dummy: ', '') \
                .replace('\\', '') \
                .replace('  ', '') \
                .replace(' ', '\n')

            # The dependency list already contains the source file's path.
            return [dep for dep in dependencies.split('\n') if dep != ""]
        else:
            raise IOError("Failed to generate dependency list for " +
                          ' '.join(command) + "\n\nThe original output was: " +
                          output)
    else:
        raise ValueError("Cannot generate dependency list for build "
                         "command '" + ' '.join(command) + "'")


# Progress reporting.
progress_checked_num = None
progress_actions = None


def init_worker(checked_num, action_num):
    global progress_checked_num, progress_actions
    progress_checked_num = checked_num
    progress_actions = action_num


def check(check_data):
    """
    Invoke clang with an action which called by processes.
    Different analyzer object belongs to for each build action.

    skiplist handler is None if no skip file was configured.
    """

    action, context, analyzer_config_map, \
        output_dir, skip_handler = check_data

    skipped = False
    try:
        # If one analysis fails the check fails.
        return_codes = 0
        skipped = False

        result_file = ''
        for source in action.sources:

            # If there is no skiplist handler there was no skip list file
            # in the command line.
            # C++ file skipping is handled here.
            source_file_name = os.path.basename(source)

            if skip_handler and skip_handler.should_skip(source):
                LOG.debug_analyzer(source_file_name + ' is skipped')
                skipped = True
                continue

            # Escape the spaces in the source path, but make sure not to
            # over-escape already escaped spaces.
            if ' ' in source:
                space_locations = [i for i, c in enumerate(source) if c == ' ']
                # If a \ is added to the text, the following indexes must be
                # shifted by one.
                rolling_offset = 0

                for orig_idx in space_locations:
                    idx = orig_idx + rolling_offset
                    if idx != 0 and source[idx - 1] != '\\':
                        source = source[:idx] + '\ ' + source[idx + 1:]
                        rolling_offset += 1

            # Construct analyzer env.
            analyzer_environment = analyzer_env.get_check_env(
                context.path_env_extra,
                context.ld_lib_path_extra)

            # Create a source analyzer.
            source_analyzer = \
                analyzer_types.construct_analyzer(action,
                                                  analyzer_config_map)

            # Source is the currently analyzed source file
            # there can be more in one buildaction.
            source_analyzer.source_file = source

            # The result handler for analysis is an empty result handler
            # which only returns metadata, but can't process the results.
            rh = analyzer_types.construct_analyze_handler(action,
                                                          output_dir,
                                                          context.severity_map,
                                                          skip_handler)

            # Fills up the result handler with the analyzer information.
            source_analyzer.analyze(rh, analyzer_environment)

            # If source file contains escaped spaces ("\ " tokens), then
            # clangSA writes the plist file with removing this escape
            # sequence, whereas clang-tidy does not. We rewrite the file
            # names to contain no escape sequences for every analyzer.
            result_file = rh.analyzer_result_file.replace(r'\ ', ' ')

            if rh.analyzer_returncode == 0:
                # Analysis was successful processing results.
                if rh.analyzer_stdout != '':
                    LOG.debug_analyzer('\n' + rh.analyzer_stdout)
                if rh.analyzer_stderr != '':
                    LOG.debug_analyzer('\n' + rh.analyzer_stderr)
                rh.postprocess_result()
                # Generated reports will be handled separately at store.

                # Save some extra information next to the plist, .source
                # acting as an extra metadata file.
                with open(result_file + ".source", 'w') as orig:
                    orig.write(
                        rh.analyzed_source_file.replace(r'\ ', ' ') + "\n")

                if os.path.exists(rh.analyzer_result_file) and \
                        not os.path.exists(result_file):
                    os.rename(rh.analyzer_result_file, result_file)

                LOG.info("[%d/%d] %s analyzed %s successfully." %
                         (progress_checked_num.value, progress_actions.value,
                          action.analyzer_type, source_file_name))
            else:
                # If the analysis has failed, we help debugging.
                failed_dir = os.path.join(output_dir, "failed")
                if not os.path.exists(failed_dir):
                    os.makedirs(failed_dir)
                LOG.debug("Writing error debugging to '" + failed_dir + "'")

                zip_file = os.path.basename(result_file) + '.zip'
                with zipfile.ZipFile(os.path.join(failed_dir, zip_file),
                                     'w') as archive:
                    if len(rh.analyzer_stdout) > 0:
                        LOG.debug("[ZIP] Writing analyzer STDOUT to /stdout")
                        archive.writestr("stdout", rh.analyzer_stdout)

                    if len(rh.analyzer_stderr) > 0:
                        LOG.debug("[ZIP] Writing analyzer STDERR to /stderr")
                        archive.writestr("stderr", rh.analyzer_stderr)

                    LOG.debug("Generating and writing dependent headers...")
                    try:
                        dependencies = set(create_dependencies(rh.buildaction))
                    except Exception as ex:
                        LOG.debug("Couldn't create dependencies:")
                        LOG.debug(ex.message)
                        archive.writestr("no-sources", ex.message)
                        dependencies = set()

                    for dependent_source in dependencies:
                        LOG.debug("[ZIP] Writing '" + dependent_source + "' "
                                  "to the archive.")
                        archive.write(
                            dependent_source,
                            os.path.join("sources-root",
                                         dependent_source.lstrip('/')),
                            zipfile.ZIP_DEFLATED)

                    LOG.debug("[ZIP] Writing extra information...")

                    archive.writestr("build-action",
                                     rh.buildaction.original_command)
                    archive.writestr("analyzer-command",
                                     ' '.join(rh.analyzer_cmd))
                    archive.writestr("return-code",
                                     str(rh.analyzer_returncode))

                LOG.debug("ZIP file written at '" +
                          os.path.join(failed_dir, zip_file) + "'")
                LOG.error("Analyzing '" + source_file_name + "' with " +
                          action.analyzer_type + " failed.")
                if rh.analyzer_stdout != '':
                    LOG.error(rh.analyzer_stdout)
                if rh.analyzer_stderr != '':
                    LOG.error(rh.analyzer_stderr)
                return_codes = rh.analyzer_returncode

        progress_checked_num.value += 1

        return return_codes, skipped, action, result_file

    except Exception as e:
        LOG.debug_analyzer(str(e))
        traceback.print_exc(file=sys.stdout)
        return 1, skipped, action.analyzer_type, None


def start_workers(actions, context, analyzer_config_map,
                  jobs, output_path, skip_handler, metadata):
    """
    Start the workers in the process pool.
    For every build action there is worker which makes the analysis.
    """

    # Handle SIGINT to stop this script running.
    def signal_handler(*arg, **kwarg):
        try:
            pool.terminate()
        finally:
            sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)

    # Start checking parallel.
    checked_var = multiprocessing.Value('i', 1)
    actions_num = multiprocessing.Value('i', len(actions))
    pool = multiprocessing.Pool(jobs,
                                initializer=init_worker,
                                initargs=(checked_var,
                                          actions_num))

    try:
        # Workaround, equivalent of map.
        # The main script does not get signal
        # while map or map_async function is running.
        # It is a python bug, this does not happen if a timeout is specified;
        # then receive the interrupt immediately.

        analyzed_actions = [(build_action,
                             context,
                             analyzer_config_map,
                             output_path,
                             skip_handler)
                            for build_action in actions]

        pool.map_async(check,
                       analyzed_actions,
                       1,
                       callback=lambda results: worker_result_handler(
                           results, metadata, output_path)
                       ).get(float('inf'))

        pool.close()
    except Exception:
        pool.terminate()
        raise
    finally:
        pool.join()
