import itertools
import os
import sys

from tqdm import tqdm

import config
import utils

flags_given = False
if len(sys.argv) > 1:
    flags_given = True


class GenerateModel:
    def __init__(self, prt_file, conn):
        self.logger = logger.get_logger()
        self.conn = conn
        if flags_given:
            self.output_dir = sys.argv[2]
        else:
            self.output_dir = config.OUTPUT_DIR
        self.extension_step = config.EXPANSION_STEP
        self.prt_file = prt_file
        self.model = self.conn.open_file(self.prt_file)
        self.param_set = self.conn.get_param_list(self.model, skip_default=True)

        self.logger.info(self.prt_file)
        self.logger.info(self.param_set)

    def get_param_iter_set(self):
        param_range = []
        for param, meta in self.param_set.items():
            # For certain prt files where not all models are not Generate
            # arbitrarily shorten it
            # step_size = float(meta['description'])/10
            step_size = float(meta['description'])
            param_range.append([round(meta['value'] + step_size * i, 3) for i in range(config.EXPANSION_STEP)])
        param_iter_set = []
        for param_values in itertools.product(*param_range):
            iter_set = {}
            for i, param_name in enumerate(self.param_set.keys()):
                iter_set.update({param_name: param_values[i]})
            param_iter_set.append(iter_set)
        return param_iter_set

    def set_output_path(self, params):
        output_file_name = "_".join([f'{key}_{value}' for key, value in params.items()]) + '.stl'
        output_model_dir = os.path.join(self.output_dir, os.path.splitext(os.path.basename(self.prt_file))[0])
        utils.make_dir(output_model_dir)
        return os.path.join(output_model_dir, output_file_name)

    def expand_model(self, params, output_file):
        try:
            self.conn.assign_paramset(self.model, params)
            self.conn.regenerate(self.model)
            self.conn.save_model(self.model, output_file)
            return True
        except Exception as e:
            self.logger.debug(",".join([f'{key}:{value}' for key, value in params.items()]) + f'with error : {e}')
            return False

    def run(self):
        param_iter_set = self.get_param_iter_set()

        no_result = 0
        for params in tqdm(param_iter_set):
            output_file = self.set_output_path(params)
            gen_result = self.expand_model(params, output_file)
            if gen_result:
                no_result += 1
        self.logger.info(f"#{no_result} model was expanded")
        return no_result


if __name__ == "__main__":
    with PythonCreoConnection(config.CREO_PATH, no_graphic_op=True, no_input_op=True) as API_conn:
        if flags_given:
            data_dir = sys.argv[1]
        else:
            data_dir = config.INPUT_DIR
        for prt_file in os.listdir(data_dir):
            result = GenerateModel(os.path.join(data_dir, prt_file), API_conn).run()
