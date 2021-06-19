
def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False



class Session():
    def __init__(self, info: dict, blocks: list, use_json=False):
        # verify input
        assert info == None or type(info) == dict
        assert info.keys()
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


        if info == None:
            raise UserWarning('No session info provided')


        self.info = info
        self.blocks = blocks
        self.use_json = use_json
        
        # make queue of indeces
        self._iq = [ (block, trial) for block in range(len(blocks)) for trial in range(len(blocks[block])) ]

        # make log history of same shape as blocks
        self.log_history = [ [{} for trial in block] for block in blocks ]


    def run(self):
        try:
            for block in self.blocks:
                for trial in block:
                    trial(self)
                    self._iq.pop(0)


        except Exception as e:
            self.log({'crashes': e})
            raise e



    def log(self, to_log: dict, save_to_file=True):
        self.log_history[self._iq[0]][self._iq[1]].update(to_log)
        if save_to_file:
            self.save()


    def discard_trial(self):
        '''Removes current trial from the log history'''
        self.log_history[self._iq[0]].pop([self._iq[1]])
        # remove any empty blocks
        self.log_history = [block for block in self.log_history if block]



    def save(self):
        # try to get a reasonable ilename
        if self.info:
            idkey = [key for key in self.info if 'id' in key.lower()]
            if idkey:
                if any('sess' in key for key in idkey.lower()):
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
        # write the contents of info at the top of the file
        top = [ item for pair in self.info.items() for item in pair ]

        # get all keys
        keys = { key for block in blocks for trial in block for key in trial.keys() }
        # normalize log_history so each trial has the same keys
        for key in keys:
            for block_num in range(len(self.log_history)):
                for trial_num in range(len(self.log_history[block_num])):
                    self.log_history[block_num][trial_num].setdefault(key)


        sorted_keys = sorted(list(keys))
        # header (sorted)
        header = ['block_num', 'trial_num'] + sorted_keys
        # contents sorted by key so the columns are consistent
        contents = [ [block, trial] + [self.log_history[block][trial][key] for key in sorted_keys] for block in range(len(blocks)) for trial in range(len(blocks[block])) ]


        # write everything to file
        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
            csvwriter.writerow(top)
            csvwriter.writerow(header)
            csvwriter.writerows(contents)



    def get_current(self):
        return self._iq


    def save_to_json(self, filename):
        with open(filename, 'w') as json_file:
            to_save = {key:value for key, value in self.__dict__.items() if not key.startswith('__') and not callable(key) and is_jsonable(value)}
            json_file.write(json.dumps(to_save))

