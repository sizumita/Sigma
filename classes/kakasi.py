# coding: utf-8
from pykakasi import kakasi

kakasi = kakasi()

kakasi.setMode('H', 'a')
kakasi.setMode('K', 'a')
kakasi.setMode('J', 'a')
dat = {
    "大阪": 'Osaka'
}
conv = kakasi.getConverter()


def do_conv(stg):
    return conv.do(stg)


def do_conv2(stg):
    data = conv.do(stg)
    if stg in dat:
        return dat[stg]
    return data[0].upper() + data[1:]
