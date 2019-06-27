import re

import pythoncom
from win32com.client.dynamic import Dispatch

import config


class CreoWrapperError(Exception):
    def __init__(self, message):
        super(CreoWrapperError, self).__init__(message)


class PythonCreoConnection:

    def __init__(self, creo_exe_path, no_graphic_op=True, no_input_op=True):
        pythoncom.CoInitialize()
        self.model = None
        self.models = []
        self.creo_exe_path = creo_exe_path
        self.no_graphic_op = ' -g:no_graphics' if no_graphic_op else ''
        self.no_input_op = ' -i:rpc_input' if no_input_op else ''
        print("Trying to form connection")
        self.asyncconn = Dispatch('pfcls.pfcAsyncConnection')
        print("Asyncconn worked")
        self.conn = self.asyncconn.Start(f"{self.creo_exe_path}{self.no_graphic_op}{self.no_input_op}", ".")
        print("Connection formed")
        self.session = self.conn.Session
        print("Session started")
        self.session.SetConfigOption("mass_property_calculate", "automatic")
        print("Connection formed")

    def __enter__(self):
        return self

    def open_file(self, path):
        options = Dispatch('pfcls.pfcRetrieveModelOptions')
        o = options.Create()
        file = Dispatch('pfcls.pfcModelDescriptor')

        # VBAPI fails if it is given a creo file with the version number appended
        path = re.sub(r"\.prt(\.[0-9]+)", ".prt", path)

        f = file.CreateFromFilename(path)
        self.model = self.session.RetrieveModelWithOpts(f, o)
        self.models.append(self.model)
        self.session.SetConfigOption("regen_failure_handling", "no_resolve_mode")
        self.session.OpenFile(f)
        return self.model

    def activate_window(self, model_id):
        self.window = self.session.GetModelWindow(self.models[model_id])
        self.window.Activate()

    def close_window(self):
        self.window.Close()

    def set_parameter(self, mdl, param_name, value):
        param = self.get_param_obj(mdl, param_name)

        modelitem = Dispatch('pfcls.MpfcModelItem')
        # create boolean if param is not float
        if isinstance(value, bool):
            val = modelitem.CreateBoolParamValue(value)
        elif isinstance(value, (float, int)):
            val = modelitem.CreateDoubleParamValue(value)
        else:
            raise CreoWrapperError("Invalid value type")

        param.SetScaledValue(val, None)

    def assign_paramset(self, mdl, paramset):
        for param, value in paramset.items():
            self.set_parameter(mdl, param, value)

    def regenerate(self, mdl):
        try:
            self.session.SetConfigOption("regen_failure_handling", "resolve_mode")
            instrs = Dispatch('pfcls.pfcRegenInstructions')
            regen_instructions = instrs.Create(False, True, None)
            mdl.Regenerate(regen_instructions)
        except Exception:
            raise CreoWrapperError("Model failed to regenerate")

    @staticmethod
    def get_param_obj(mdl, param_name):
        param_obj = mdl.GetParam(param_name)
        try:
            paramvalue = param_obj.value
            return param_obj
        except AttributeError:
            raise CreoWrapperError(f"Parameter {param_name} not found")

    def get_param(self, mdl, param_name):
        param_obj = self.get_param_obj(mdl, param_name)
        return self._export_param(param_obj)

    @staticmethod
    def _export_param(param_obj):
        param_data_type = param_obj.Value.discr
        if param_data_type == 0:
            param_value = param_obj.Value.StringValue
        elif param_data_type == 1:
            param_value = param_obj.Value.IntValue
        elif param_data_type == 2:
            param_value = param_obj.Value.BoolValue
        elif param_data_type == 3:
            param_value = param_obj.Value.DoubleValue
        else:
            raise ValueError

        return {
            param_obj.Name: {
                'description': param_obj.Description,
                'value': param_value
            }
        }

    def get_param_list(self, mdl, skip_default=True):
        param_list = {}
        param_list_obj = mdl.ListParams()
        no_params = param_list_obj.Count
        for idx in range(no_params):
            param_item = self._export_param(param_list_obj.Item(idx))
            if skip_default and list(param_item.keys())[0] in ['DESCRIPTION', 'MODELED_BY', 'PTC_MATERIAL_NAME']:
                continue
            param_list.update(param_item)
        # param_list['DESCRIPTION'] = str(float(param_list['DESCRIPTION'])/2)
        return param_list

    @staticmethod
    def save_model(mdl, filepath):
        instrs = Dispatch('pfcls.pfcSTLASCIIExportInstructions')
        export_instructions = instrs.Create(None)
        mdl.Export(filepath, export_instructions)

    def close(self):
        self.conn.End()

    def __exit__(self, exc_type, exc_value, traceback):

        for i in range(len(self.models)):
            try:
                window = self.session.GetModelWindow(self.models[i])
                window.Activate()
                window.Close()
            except:
                pass

        self.close()
        print("Connection closed")


if __name__ == "__main__":
    creo_path = config.CREO_PATH
    test_file = config.TEST_INPUT_DIR
    output_file = config.TEST_OUTPUT_FILE
    with PythonCreoConnection(creo_path, no_graphic_op=True, no_input_op=True) as conn:
        conn.open_file(test_file)
        model = conn.models[0]
        print(conn.get_param(model, 'WIDTH'))
        print(conn.get_param_list(model))
        print(conn.get_param_list(model, skip_default=False))

        conn.assign_paramset(model, {'WIDTH': 5})
        conn.regenerate(model)
        conn.save_model(model, output_file)
