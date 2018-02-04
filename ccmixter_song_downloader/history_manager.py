import os
import logging
import json


class History:
    log_file = '._ccmixter_song_downloader_history.json'

    @staticmethod
    def history_log(wdir=os.getcwd(), log_file='log_file.txt',
                    mode='read', write_data=None):
        """This should generally be called after another program has finished
        to record it's progress or history.
        Read python dictionary from or write python dictionary to a file

        :param wdir: directory for text file to be saved to
        :param log_file: name of text file (include .txt extension)
        :param mode: 'read', 'write', or 'append' are valid
        :param write_data: data that'll get written in the log_file
        :type write_data: dictionary (or list or set)

        :return: returns data read from or written to file (depending on mode)
        :rtype: dictionary
        """
        mode_dict = {
            'read': 'r',
            'write': 'w',
            'append': 'a',
            'update': 'r+',
        }
        if mode in mode_dict:
            log_file_path = os.path.join(wdir, log_file)
            History.create_directories_if_needed(log_file_path)
            if mode == 'update':
                History.create_file_if_not_created(log_file_path, {})

            with open(log_file_path, mode_dict[mode]) as f:
                # read from file as JSON and return JSON
                if mode == 'read':
                    return json.loads(f.read())
                # read data then update data with new write_data then save JSON
                elif mode == 'update':
                    data = json.loads(f.read())
                    # only supporting updating if both are dictionaries
                    if isinstance(data, dict) and isinstance(write_data, dict):
                        data.update(write_data)
                        f.seek(0)  # seek to beginning to overwrite data
                        f.write(json.dumps(data))
                    else:
                        logging.critical(
                            "[ccmixter_song_downloader.history_manager."
                            "History.history_log] "
                            "Does not support updating non-dict JSON")
                    return data
                # write or append modes
                else:
                    f.write(json.dumps(write_data))
                    return write_data
        else:
            logging.debug('history_log func: invalid mode (param #3)')
            return {}

    @staticmethod
    def get_previous_download_amount(tags, sort, dir, verbose=False):
        """Open & update log_file to get last_id of subreddit of sort_type
        Creates log_file if no existing log file was found

        :param tags: name of subreddit
        :param sort: sort type of subreddit
        :param dir: directory log_file will be saved to
        :param log_file: name of log file
        :param verbose: prints extra messages

        :return: log_data (contains last ids), last_id
        :rtype: tuple

        Note: this has been modified to work with ccmixter_song_downloader
        """
        no_history = False
        log_data = None
        last_id = None
        try:
            # first: we try to open the log_file
            log_data = History.history_log(dir, History.log_file, 'read')

            # second: we check if the data loaded is a dictionary
            if not isinstance(log_data, dict):
                raise ValueError(
                    log_data,
                    'data from %s is not a dictionary, overwriting %s'
                    % (History.log_file, History.log_file))

            # third: try loading last id for subreddit & sort_type
            if tags in log_data:
                if sort in log_data[tags]:
                    last_id = log_data[tags][sort]['downloads']
                else:  # sort not in log_data but tags is
                    no_history = True
                    log_data[tags][sort] = {'downloads': 0}
            else:  # tags not listed as key in log_data
                no_history = True
                log_data[tags] = {sort: {'downloads': 0}}

        # py3 or py2 exception for dne file
        except (FileNotFoundError, IOError, FileExistsError):
            last_id = ''
            log_data = {
                tags: {
                    sort: {
                        'downloads': 0
                    }
                }
            }
            History.history_log(dir, History.log_file, 'write', log_data)
            if verbose:
                print('%s not found in %s, created new %s'
                      % (History.log_file, dir, History.log_file))

        except ValueError as e:
            if verbose:
                print('log_data:\n{}'.format(e.args))

        except Exception as e:
            print(e)

        if no_history:
            last_id = 0
            log_data = History.history_log(dir, History.log_file, 'write',
                                           log_data)

        return log_data, last_id

    @staticmethod
    def create_directories_if_needed(path, is_file=True):
        """Creates the directories leading to the path if they don't exist

        :param path: file path of a folder or file
        :param is_file: should be True if path points to file, False otherwise
        :return:
        """
        path = os.path.abspath(path)
        if is_file:
            path = os.path.dirname(path)
        if not os.path.isdir(path):
            os.makedirs(path)

    @staticmethod
    def create_file_if_not_created(file_path, write_data={}):
        try:
            with open(file_path, 'r'):
                pass
        except (FileNotFoundError, FileExistsError):
            with open(file_path, 'w') as f:
                f.write(json.dumps(write_data))
