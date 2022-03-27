import os
import tempfile
import shutil
from tempfile import gettempdir
import logging
_logger = logging.getLogger(__name__)
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, date, time

def get_temp_dir():
    """
        This method generate new directory in Temp directory
    """
    temp_directory = tempfile.TemporaryDirectory()
    parent_dir = temp_directory.name
    temp_directory.cleanup()
    while os.path.exists(parent_dir):
        temp_directory = tempfile.TemporaryDirectory()
        parent_dir = temp_directory.name
    dir_name = os.makedirs(parent_dir)
    return parent_dir


def delete_directory(filename):
    '''
        This method deletes directory from Temp directory

        Args:
            filename (str): filename which has to be deleted
    '''
    file_path = os.path.join(gettempdir(), filename)
    try:
        if os.path.exists(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        _logger.warning(e)

def _get_full_date_from_timestamp(tz, date):
    mytz = pytz.timezone(tz)
    display_date_result = datetime.strftime(pytz.utc.localize(datetime.strptime(
        str(date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(mytz), "%Y-%m-%d %H:%M:%S")
    return display_date_result

