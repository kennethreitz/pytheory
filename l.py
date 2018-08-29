from pytuning.scales import create_edo_scale

edo_12_scale = create_edo_scale(12)
print((edo_12_scale[1] * 440).evalf(8))
