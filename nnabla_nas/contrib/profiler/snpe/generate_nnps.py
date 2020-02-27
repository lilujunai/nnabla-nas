import argparse
import os
import shutil
import logging
import json

import nnabla as nn


from nnabla_nas.contrib.profiler.helpers import (create_parameters, nnp_save,
                                                 get_unique_modules, get_search_net)


def main(args):
    nn.logger.setLevel(logging.ERROR)

    # SearchNet
    with open(args.search_net_config) as fp:
        config = json.load(fp)
    net_config = config['network'].copy()
    net = get_search_net(net_config, "full")
    inp = nn.Variable([1] + config["input_shape"])
    out = net(inp)
    unique_mods = get_unique_modules(net)

    if os.path.exists(args.nnp_dir):
        shutil.rmtree(args.nnp_dir)
    os.makedirs(args.nnp_dir)

    # Generate NNPs
    for mod_name, umod in unique_mods.items():
        path = "{}/{}.nnp".format(args.nnp_dir, mod_name)
        inp = [nn.Variable(shape) for shape in umod.input_shapes]
        out = umod(*inp)
        if out.parent is None:
            continue
        nn.parameter.clear_parameters()
        create_parameters(out)
        nnp_save(path, mod_name, inp, out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="NNP Files Generation for NAS.")
    parser.add_argument('--search-net-config', type=str, required=True,
                        help='Path to SearchNet jsonconfig file.')
    parser.add_argument('--nnp-dir', type=str, required=True, help='Directory for NNP input files.')

    args = parser.parse_args()

    main(args)
