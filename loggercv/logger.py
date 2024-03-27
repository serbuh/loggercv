# -*- coding: utf-8 -*-

# Stdlib imports
import os
import logging
import logging.config
import enum
import pathlib

# Third party imports


# Log level options
class LoggerOptions(enum.Enum):
    NO                        = 0
    FILE_ONLY                 = 1
    FILE_AND_CONSOLE          = 2

class Logger():
    def __init__(self, log_name, logs_base_dir, log_dir=None, create_dir=True, log_options=LoggerOptions.FILE_AND_CONSOLE, console_debug_lvl=logging.INFO, file_debug_level=logging.DEBUG, filtered_groups=[], propagate=False):
        '''
        logs_base_dir should be full path
        log_dir should be directory name

        Logs will be stored in (log_dir created only if given):
            <logs_base_dir>(/<log_dir>)/<log_name>.log

        current_log_dir_full_path:
            <logs_base_dir>(/<log_dir>)
        
        create_dir: True (default) <=> Create current_log_dir_full_path.
                    False          <=> Assuming logs_base_dir already exist.
        '''
        
        self.log_name = log_name
        
        # Disable logger and do not continue to the logging folder creation
        if log_options == LoggerOptions.NO:
            self.logger = logging.getLogger(log_name)
            self.logger.disabled=True
            return

        # Current log dir: <logs_base_dir>/<log_name>
        if log_dir:
            self.current_log_dir_full_path = os.path.join(logs_base_dir, log_dir)
        else:
            self.current_log_dir_full_path = logs_base_dir
        
        # Check if full log dir exists
        if not os.path.isdir(self.current_log_dir_full_path):
            if create_dir:
                pathlib.Path(self.current_log_dir_full_path).mkdir(parents=True, exist_ok=True)
            else:
                raise Exception(f"Given logs base dir does not exist!\n{logs_base_dir}")

        # Full path for the log file: (<logs_base_dir>/(<log_name>/)<log_name>.log)
        self.log_file_path = os.path.join(self.current_log_dir_full_path, log_name + '.log')
        
        # Prepare handlers list for the config
        if log_options == LoggerOptions.FILE_ONLY:
            handlers_list = ['file_handler']
        elif log_options == LoggerOptions.FILE_AND_CONSOLE:
            handlers_list = ['console_handler', 'file_handler']
        
        # Prepare config
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'clear_with_time_msec_format': {
                    'format': '%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                    'datefmt': '%H:%M:%S', # No date for the console
                },
                'clear_with_full_date_msec_format': {
                    'format': '%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S', # Full date for file
                },
            },
            'handlers': {
                'console_handler': {
                    'level': console_debug_lvl,
                    'formatter': 'clear_with_time_msec_format',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                },
                'file_handler': {
                    'level': file_debug_level,
                    'formatter': 'clear_with_full_date_msec_format',
                    'class': 'logging.FileHandler',
                    'filename': self.log_file_path,
                    'mode': 'a'
                },
            },
            'loggers': {
                log_name: {
                    'handlers': handlers_list,
                    'level': 'DEBUG',
                    'propagate': propagate,
                },
            },
        }

        # Apply logging config
        logging.config.dictConfig(logging_config)

        # Create logger
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)

        # Welcome message
        self.info(f'Initialized logger for "{log_name}"')
        # TODO if self.logger.handlers has FileHandler:
        self.info(f'Saving log to {self.log_file_path}')
        
        # Add filter
        self.update_filtered_groups(filtered_groups)
        
    def get_current_log_dir_full_path(self):
        return self.current_log_dir_full_path
    
    def update_filtered_groups(self, filtered_groups):
        # Add filter of the filtered groups
        f = Logger.FilterLogGroups(filtered_groups)
        self.logger.addFilter(f)

        if len(filtered_groups)>0:
            self.info(f"Filtering out log groups: {filtered_groups}")

    class FilterLogGroups(logging.Filter):
        '''
        Filter that drops LogRecords from filtered_groups
        '''
        
        def __init__(self, filtered_groups):
            self.filtered_groups = filtered_groups

        def filter(self, record):
            return False if record.log_group in self.filtered_groups else True

    def info(self, msg, log_group=None):
        self.logger.info(msg, extra={"log_group":log_group})

    def debug(self, msg, log_group=None):
        self.logger.debug(msg, extra={"log_group":log_group})
    
    def warning(self, msg, log_group=None):
        self.logger.warning(msg, extra={"log_group":log_group})
    
    def error(self, msg, log_group=None):
        self.logger.error(msg, extra={"log_group":log_group})
    
    def critical(self, msg, log_group=None):
        self.logger.critical(msg, extra={"log_group":log_group})
    
    def exception(self, msg, log_group=None):
        self.logger.exception(msg, extra={"log_group":log_group})
    
    def log(self, severity, msg, log_group=None):
        self.logger.log(severity, msg, extra={"log_group":log_group})

if __name__ == "__main__":
    # Run me to test the logger module
    import time
    datetime_now = time.strftime("%Y_%m_%d__%H_%M_%S")

    # filter out log groups
    filtered_groups = ["group_1"]

    # Assuming that <project_dir>/logger/logger.py
    project_dir = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
    logs_base_dir = os.path.join(project_dir, 'logs')
    logger = Logger("Module", logs_base_dir, log_dir='Test_Module', filtered_groups=filtered_groups) # log_options=LoggerOptions.FILE_ONLY

    # Log test
    logger.info("Filtered message", "group_1")
    logger.info("Unfiltered message", "group_2")
    logger.info("Welcome!")
    logger.debug("Debug")
    logger.error("Error")
    logger.critical("Critical")

    try:
        1/0
    except Exception as e:
        logger.exception(e)