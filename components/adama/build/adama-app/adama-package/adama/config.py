"""Read config files from /adama-package/conf.yml """

from typing import List, Dict, cast, Union, typevar

import yaml

from .exceptions import AdamaError


ConfigDict = typevar(
    'ConfigDict',
    values=(Dict[str, Dict[str, Union[str, int, float, List]]],))


def read() -> ConfigDict:
    conf_file = open('/adama-package/conf.yml')
    try:
        conf_yaml = yaml.load(conf_file)
        assert isinstance(conf_yaml, dict)
        return cast(Dict, conf_yaml)
    except yaml.error.YAMLError as exc:
        raise AdamaError(
            'wrong yaml in /adama-package/conf.yml\n'
            '{}'.format(exc))
    except AssertionError:
        raise AdamaError(
            'config file /adama-package/conf.yml should be an object, '
            'not string, number, or list')


Config = read()
