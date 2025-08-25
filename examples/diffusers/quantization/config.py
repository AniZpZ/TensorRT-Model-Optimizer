# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from calib.plugin_calib import PercentileCalibrator

FP8_DEFAULT_CONFIG = {
    "quant_cfg": {
        "*weight_quantizer": {"num_bits": (4, 3), "axis": None},
        "*input_quantizer": {"num_bits": (4, 3), "axis": None},
        "*output_quantizer": {"enable": False},
        "*[qkv]_bmm_quantizer": {"num_bits": (4, 3), "axis": None},
        "*softmax_quantizer": {
            "num_bits": (4, 3),
            "axis": None,
        },
        "default": {"enable": False},
    },
    "algorithm": "max",
}

INT8_DEFAULT_CONFIG = {
    "quant_cfg": {
        "*weight_quantizer": {"num_bits": 8, "axis": 0},
        "*input_quantizer": {"num_bits": 8, "axis": 0},
        "*output_quantizer": {"enable": False},
        "default": {"enable": False},
    },
    "algorithm": "max",
}

NVFP4_DEFAULT_CONFIG = {
    "quant_cfg": {
        "*weight_quantizer": {
            "num_bits": (2, 1),
            "block_sizes": {-1: 16, "type": "dynamic", "scale_bits": (4, 3)},
            "axis": None,
            "enable": True,
        },
        "*input_quantizer": {
            "num_bits": (2, 1),
            "block_sizes": {-1: 16, "type": "dynamic", "scale_bits": (4, 3)},
            "axis": None,
            "enable": True,
        },
        "*output_quantizer": {"enable": False},
        "*[qkv]_bmm_quantizer": {"num_bits": (4, 3), "axis": None},
        "*softmax_quantizer": {
            "num_bits": (4, 3),
            "axis": None,
        },
        "default": {"enable": False},
    },
    "algorithm": "max",
}

NVFP4_FP8_MHA_CONFIG = {
    "quant_cfg": {
        "**weight_quantizer": {
            "num_bits": (2, 1),
            "block_sizes": {-1: 16, "type": "dynamic", "scale_bits": (4, 3)},
            "axis": None,
            "enable": True,
        },
        "**input_quantizer": {
            "num_bits": (2, 1),
            "block_sizes": {-1: 16, "type": "dynamic", "scale_bits": (4, 3)},
            "axis": None,
            "enable": True,
        },
        "*output_quantizer": {"enable": False},
        "*[qkv]_bmm_quantizer": {
            "num_bits": (4, 3),
            "axis": None,
        },
        "*softmax_quantizer": {
            "num_bits": (4, 3),
            "axis": None,
        },
        "*bmm2_output_quantizer": {
            "num_bits": (4, 3),
            "axis": None,
        },
        "default": {"enable": False},
    },
    "algorithm": {"method": "svdquant", "lowrank": 32},
}


def set_quant_config_attr(quant_config, trt_high_precision_dtype, quant_algo, **kwargs):
    algo_cfg = {"method": quant_algo}

    if quant_algo == "smoothquant" and "alpha" in kwargs:
        algo_cfg["alpha"] = kwargs["alpha"]
    elif quant_algo == "svdquant" and "lowrank" in kwargs:
        algo_cfg["lowrank"] = kwargs["lowrank"]
    quant_config["algorithm"] = algo_cfg

    for p in quant_config["quant_cfg"].values():
        if "num_bits" in p and "trt_high_precision_dtype" not in p:
            p["trt_high_precision_dtype"] = trt_high_precision_dtype


def reset_set_int8_config(quant_config, percentile, n_steps, collect_method):
    for key in quant_config["quant_cfg"]:
        if "weight" not in key:
            quant_config["quant_cfg"][key] = {
                "num_bits": 8,
                "axis": None,
                "calibrator": (
                    PercentileCalibrator,
                    (),
                    {
                        "num_bits": 8,
                        "axis": None,
                        "percentile": percentile,
                        "total_step": n_steps,
                        "collect_method": collect_method,
                    },
                ),
            }
