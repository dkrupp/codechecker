# -------------------------------------------------------------------------
#                     The CodeChecker Infrastructure
#   This file is distributed under the University of Illinois Open Source
#   License. See LICENSE.TXT for details.
# -------------------------------------------------------------------------

import os

from libcodechecker.logger import LoggerFactory

LOG = LoggerFactory.get_new_logger('HOST CHECK')


# -----------------------------------------------------------------------------
def check_zlib():
    """ Check if zlib compression is available.
    If wrong libraries are installed on the host machine it is
    possible the the compression fails which is required to
    store data into the database.
    """

    try:
        import zlib
        zlib.compress('Compress this')
        return True
    except Exception as ex:
        LOG.error(str(ex))
        LOG.error('Failed to import zlib module.')
        return False


# -----------------------------------------------------------------------------
def get_postgresql_driver_name():
    try:
        driver = os.getenv('CODECHECKER_DB_DRIVER')
        if driver:
            return driver

        try:
            import psycopg2  # NOQA.
            return "psycopg2"
        except Exception:
            import pg8000  # NOQA.
            return "pg8000"
    except Exception as ex:
        LOG.error(str(ex))
        LOG.error('Failed to import psycopg2 or pg8000 module.')
        raise


# -----------------------------------------------------------------------------
def check_postgresql_driver():
    try:
        get_postgresql_driver_name()
        return True
    except Exception as ex:
        LOG.debug(ex)
        return False


# -----------------------------------------------------------------------------
def check_sql_driver(check_postgresql):
    if check_postgresql:
        try:
            get_postgresql_driver_name()
            return True
        except Exception:
            return False
    else:
        try:
            try:
                import pysqlite2
            except Exception:
                import sqlite3
        except Exception as ex:
            LOG.debug(ex)
            return False
        return True
