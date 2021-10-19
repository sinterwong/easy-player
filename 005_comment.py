# 网易云音乐评论
#   1. 内容不在网页源代码和框架源代码中，因此断定是客户端渲染
#   2. 利用抓包工具，看数据内容是通过哪个脚本传递出来的
#   3. 找到了请求数据内容的链接，但是发现是一个post请求，并且携带的数据是加密的
#   4. 我们可以通过某种途径找到原始的参数，但是原始的参数是不行的，因此需要破解其加密方式
#   5. 通过调试其前端的代码，试图寻找加密的代码，然后利用python复现即可
#   6. 利用 initiator 工具查看调用过程，并定位到最后发出的那一步，然后向前追溯直至找到加密数据的代码
import requests
from lxml import etree
from Crypto.Cipher import AES
from base64 import b64encode
import json


def to_16(data):
    pad = 16 - len(data) % 16
    data += chr(pad) * pad
    return data


def get_encSecKey():
    # i 为 "0y9ax3MYS6q3GQF5" 时生成的加密码
    return "9776486a730d27d17ba01225d5af4b0f0eb03789212eaec3e7bd1974177e0145fd38a30a9c074344dd33bbabf7a2d43d8e1742404da70a45c57bdcaa7bb009b5c984ad61849206b24b90a9f0fc231dc7f31a0920a83bd0e448056c9db12c71e43dd3b34274d69b8232c6181c44b83760ad64ff5c28605f28b9bfd6c1f889f9d7"


def enc_params(d, g, iv):
    data = to_16(d)
    obj = AES.new(key=g.encode("utf-8"),
                  IV=iv.encode("utf-8"), mode=AES.MODE_CBC)
    bs = obj.encrypt(data.encode("utf-8"))
    return str(b64encode(bs), "utf-8")


def get_params(d, g, i):
    iv = "0102030405060708"
    first = enc_params(d, g, iv)
    second = enc_params(first, i, iv)
    return second


"""
前端加密代码
!function() {
    function a(a) {
        var d, e, b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", c = "";
        for (d = 0; a > d; d += 1)
            e = Math.random() * b.length,
            e = Math.floor(e),
            c += b.charAt(e);
        return c
    }
    function b(a, b) {
        var c = CryptoJS.enc.Utf8.parse(b)
        var d = CryptoJS.enc.Utf8.parse("0102030405060708")
        var e = CryptoJS.enc.Utf8.parse(a)
        var f = CryptoJS.AES.encrypt(e, c, {iv: d, mode: CryptoJS.mode.CBC});
        return f.toString()
    }
    function c(a, b, c) {
        var d, e;
        return setMaxDigits(131),
        d = new RSAKeyPair(b,"",c),
        e = encryptedString(d, a)
    }
    function d(d, e, f, g) {
        var h = {};
        var i = a(16);

        h.encText = b(d, g)
        h.encText = b(h.encText, i)
        # i是通过a()生成的，a()需要使用随机数，而c()除了i其余都是固定的数，所以只要把a()的结果固定，那么c的结果就可以固定了
        h.encSecKey = c(i, e, f)
        return h
    }
    function e(a, b, d, e) {
        var f = {};
        return f.encText = c(a + e, b, d),
        f
    }
    window.asrsea = d,
    window.ecnonasr = e
}();
"""
"""
加密时候的参数说明
window.asrsea(JSON.stringify(i3x), bva9R(["流泪", "强"]), bva9R(Tu4y.md), bva9R(["爱心", "女孩", "惊恐", "大笑"]))
param1: 将数据利用 JSON.stringify() 转成 json 字符串，其实就是我们的数据
param2: 利用传入的字符list获取对应编码的函数，可以在chrome提供的console中执行获取。此处为："010001"
param3: 同上，此处为："00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
param4: 同上，此处为："0CoJUm6Qyw8W8jud"
"""


def main():
    # 未进行加密时的数据
    d = {
        "csrf_token": "806464a8db6831a6452dd292856a72c7",
        "cursor": "-1",
        "offset": "0",
        "orderType": "1",
        "pageNo": "2",
        "pageSize": "20",
        "rid": "R_SO_4_506196018",
        "threadId": "R_SO_4_506196018"
    }

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "cookie": "_ntes_nnid=f32a876607c2e60388a0f17841b06169,1621825437666; _ntes_nuid=f32a876607c2e60388a0f17841b06169; _iuqxldmzr_=32; NMTID=00OMb9hie-8kNSr6EjPhaikhYgTNHEAAAF8fX9cFA; WEVNSM=1.0.0; WNMCID=yhdozs.1634193071746.01.0; WM_TID=PHRZPj5UE9RAABFVVQN6oSv2au4oGFbg; WM_NI=AoW1ZTM6u1m3aJ75aNVOU8v%2B%2FdBDaQ24Ng3AbD1mtPATV9lUDRC4VZ%2BpgDqmAiDgUKJRkq5pXEbvlSjPMak0xsAfC1sg%2F5R2%2F4z%2BckggXmjKZqk9wJzQ%2BRhqGqV8SUWNSFQ%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee82e94b9aa8b9d7f279b69e8eb7c84b929b9f84f5408e96bcabd14385bdb687e92af0fea7c3b92a83b199d2d9608feabbd2f039a396f9d6e44696919bd9f521edbc8ea5e45bf2ec8288b24ba29cff8ef75c838c9adaef5f888e8dd5d552e9b0a9a5f46783b78c88d8418a8ea592b87c9c9bae97ef59aa908382ea3cbcad8f87c23bb1b9e1d6d13aedecb6cce261a5b9988ee9419aafa5daf642ba8fe5b3eb7b85af9ad9d25f95929da7d437e2a3; __csrf=806464a8db6831a6452dd292856a72c7; MUSIC_U=0feb389158dffb4e31cfce9bec7190842722bd4a793616dd70342d2a0cf85438993166e004087dd3d78b6050a17a35e705925a4e6992f61dfe3f0151024f9e31; MUSIC_A_T=1524453093144; MUSIC_R_T=1524453183093; ntes_kaola_ad=1; JSESSIONID-WYYY=E%5CZm2aSliXsmsgxYSCvkO4qzefXA8nqYGmynn2Vn4D18%2FXoJxaKWqI%2Fzs%2F8nVvJEG6ShCePV0%5CS1hSOf%5CB4c2Y44fMCp7XUYYsQE307N8r5YmRRjR%5CVY3z3Fh9KAkCFgj8gfQqaS6dKoxqs3p8r9djY%2FYGsUQf0nzlOjhg4VV2YX37MJ%3A1634631441369",
        "referer": "https://music.163.com/song?id=506196018"
    }

    e = "010001"
    f = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
    g = "0CoJUm6Qyw8W8jud"
    i = "0y9ax3MYS6q3GQF5"

    url = "https://music.163.com/weapi/comment/resource/comments/get?csrf_token=806464a8db6831a6452dd292856a72c7"
    data = {
        "params": get_params(json.dumps(d), g, i),
        "encSecKey": get_encSecKey()
    }
    response = requests.post(url, data=data, headers=headers)

    print(response.text)
    response.close()


if __name__ == "__main__":
    main()
