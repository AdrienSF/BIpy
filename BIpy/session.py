import json, csv

def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False



class Session():
    """A class that handles the execution and data collection of a Psychopy experiment

    Attributes
    ----------
    info : dict or None
        Information about the session, ex: {'session_id': 1234}
    blocks : list of lists of functions
        List of blocks, each block a list of trials, each trial a function that takes exactly one input: 'logger'
        each trial function should execute the intended trial
    use_json : bool
        Flag to indicate whether or not to save data to json on calling save()
    to_hide : list
        List of trials to be ignored when saving to csv
    log_history : list of lists of dicts
        Used to store trial data on call of log()
    _iq : list
        Index queue, list of tuples corresponding to the indeces of each trial function in blocks
    


    Methods
    -------
    run
        Iterates through and runs all trial functions of blocks in order
    log(to_log: dict, save_to_file=True)
        Stores to_log in log_history[current_block_num][current_trial_num]
    hide_trial
        Marks current trial to be ignored when saving to csv
    save
        Attempts to find an apropriate filename, and calls save_to_csv(filename)
        if use_json is True, also calls save_to_json(filename)
    save_to_csv(filename)
        Saves the Session's info, and log_history to filename in csv format
    get_current
        Returns the current block and trial nuber
    save_to_json(filename)
        Saves as much information about the current Session object as possible to filename in json format

    """

    def __init__(self, info: dict, blocks: list, use_json=False, hide_info=False, suppress_save=False):
        """
        Parameters        
        ----------
        info : dict or None
            Information about the session, ex: {'session_id': 1234}
        blocks : list of lists of functions
            List of blocks, each block a list of trials, each trial a function that takes exactly one input: 'logger'
            each trial function should execute the intended trial
        use_json : bool, default False
            Flag to indicate whether or not to save data to json on calling save()     
        suppress_save : bool, default False
            Flag to indicate log() calls should never save to file save to file
        hide_info : bool, default False
            Flag to indicate if 'info' should be saved to csv

        """


        # verify input
        assert type(blocks) == list
        assert all(type(block) == list for block in blocks)
        assert all(callable(trial) for block in blocks for trial in block)

        
        # check that each trial func takes exactly one input
        for block_num in range(len(blocks)):
            for trial_num in range(len(blocks[block_num])):
                trial_func = blocks[block_num][trial_num]

                all_args = trial_func.__code__.co_argcount
                if trial_func.__defaults__ is not None:  #  in case there are no kwargs
                    kwargs = len(trial_func.__defaults__)
                else:
                    kwargs = 0

                positional_args = all_args - kwargs

                if positional_args != 1:
                    raise RuntimeError('Block ' + str(block_num) + ' trial ' + str(trial_num) + '\'s function has ' + str(positional_args) + ' positional arguments, exactly 1 positional argment: \'logger\' is required')


        if type(info) != dict:
            self.hide_info = True
            raise UserWarning('No dict provided as \'info\', it will not be saved to csv')


        self.info = info
        self.blocks = blocks
        self.use_json = use_json
        self.hide_info = hide_info
        self.suppress_save = suppress_save
        self.to_hide = []
        
        # make queue of indeces
        self._iq = [ (block, trial) for block in range(len(blocks)) for trial in range(len(blocks[block])) ]

        # make log history of same shape as blocks
        self.log_history = [ [{} for trial in block] for block in blocks ]



    def run(self):
        """Iterates through and runs all trial functions of blocks in order"""

        try:
            for block in self.blocks:
                for trial in block:
                    trial(self)
                    self._iq.pop(0)

        except Exception as e:
            self.log({'crashes': e})
            raise e



    def log(self, to_log: dict, save_to_file=True):
        """Stores to_log in log_history[current_block_num][current_trial_num]

        Parameters
        ----------
        to_log: dict
            Python dict with information to save from the current trial, ex: {'RT': .129486}
        save_to_file: bool, defaul=True
            Flag to save data to file
            this can take time so set to False if you want to log some data but the current trial needs strict timing,
            then call Session.save() a the end of the experiment
        """

        if self.suppress_save:
            save_to_file = False

        # make sure to_log has str keys
        to_log = { str(key): to_log[key] for key in to_log }

        self.log_history[self._iq[0][0]][self._iq[0][1]].update(to_log)
        if save_to_file:
            self.save()


    def hide_trial(self):
        '''Marks current trial to be ignored when saving to csv'''
        self.to_hide.append(self._iq[0])


    def save(self):
        """Attempts to find an apropriate filename, and calls save_to_csv(filename)

        If self.use_json is True, also calls save_to_json(filename)
        """

        # try to get a reasonable ilename
        if self.info:
            idkey = [key for key in self.info if 'id' in key.lower()]
            if idkey:
                if any('sess' in key.lower() for key in idkey):
                    idkey = [key for key in idkey if 'sess' in key.lower()][0]
                else:
                    idkey = idkey[0]
            else:
                idkey = self.info.keys()[0]

            filename = str(idkey) + str(self.info[idkey])
        else:
            filename = ''


        self.save_to_csv(filename+'.csv')
        if self.use_json:
            self.save_to_json(filename+'.json')



    def save_to_csv(self, filename):
        """Saves the Session's info, and log_history to filename in csv format
        
        Parameters
        ----------
        filename : str
        """

        # make copy of log history
        hist = [ [trial for trial in block] for block in self.log_history ]
        # remove ignored from copy
        for block, trial in self.to_hide:
            hist[block].pop(trial)
        # remove any empty blocks
        hist = [ [trial for trial in block] for block in hist if block ]


        if not self.hide_info:
            # write the contents of info at the top of the file
            top = [ item for pair in self.info.items() for item in pair ]

        # get all keys
        keys = { key for block in hist for trial in block for key in trial.keys() }
        # normalize log_history so each trial has the same keys
        for key in keys:
            for block_num in range(len(hist)):
                for trial_num in range(len(hist[block_num])):
                    hist[block_num][trial_num].setdefault(key)


        sorted_keys = sorted(list(keys))
        # header (sorted)
        header = ['block_num', 'trial_num'] + sorted_keys
        # contents sorted by key so the columns are consistent
        contents = [ [block, trial] + [hist[block][trial][key] for key in sorted_keys] for block in range(len(hist)) for trial in range(len(hist[block])) ]


        # write everything to file
        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
            if not self.hide_info:
                csvwriter.writerow(top)
            csvwriter.writerow(header)
            csvwriter.writerows(contents)



    def get_current(self):
        """Returns the current block and trial nuber: tuple (block, trial)"""

        return self._iq[0]


    def save_to_json(self, filename):
        """Saves as much information about the current Session object as possible to filename in json format

        Parameters
        ----------
        filename : str        
        """

        with open(filename, 'w') as json_file:
            to_save = {key:value for key, value in self.__dict__.items() if not key.startswith('__') and not callable(key) and is_jsonable(value)}
            json_file.write(json.dumps(to_save))

