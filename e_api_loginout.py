# -*- coding: utf-8 -*-

# 2021.06.24
# Python 3.6.8 / centos7.4
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# ログインして、ログアウトするだけです。

import urllib3
import datetime
import json


def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate




print('-- login -----------------------------------------------------')
## 「ｅ支店・ＡＰＩ、ブラウザからの利用方法」に記載のログイン例
## 'https://demo-kabuka.e-shiten.jp/e_api_v4r1/auth/?{"p_no":"1","p_sd_date":"2020.11.07-13:46:35.000",'
## '"sCLMID":"CLMAuthLoginRequest","sPassword":"xxxxxx","sUserId":"xxxxxxxx","sJsonOfmt":"5"}'
##
# 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/43 No.1 引数名:CLMAuthLoginRequest を参照してください。


int_p_no = 1
my_sCLMID = 'CLMAuthLoginRequest'

my_userid = 'MY_USERID' # 自分のuseridに書き換える
my_passwd = 'MY_PASSWD' # 自分のpasswordに書き換える
my_2passwd = 'MY_2PASSWD'     # 自分の第２パスワードに書き換える

# システム時刻を所定の書式で取得
my_p_sd_date = func_p_sd_date(datetime.datetime.now())

# 返り値の表示形式指定
my_sJsonOfmt = '5'    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定


# デモ環境（新バージョンになった場合、適宜変更）
url_base = 'https://demo-kabuka.e-shiten.jp/e_api_v4r1/'
# 本番環境（新バージョンになった場合、適宜変更）
# url_base = 'https://kabuka.e-shiten.jp/e_api_v4r1/'


my_url = url_base + 'auth/?{'
my_url = my_url + '"p_no":"' + str(int_p_no) + '"'
my_url = my_url + ',' + '"p_sd_date":"' + my_p_sd_date + '"'
my_url = my_url + ',' + '"sCLMID":"' + my_sCLMID + '"'
my_url = my_url + ',' + '"sUserId":"' + my_userid + '"'
my_url = my_url + ',' + '"sPassword":"' + my_passwd + '"'
my_url = my_url + ',' + '"sJsonOfmt":"' + my_sJsonOfmt + '"'
my_url = my_url + '}'

print('送信文字列＝')
print(my_url)  # 送信する文字列


# APIに接続
http = urllib3.PoolManager()
req = http.request('GET', my_url)
print("req.status= ", req.status )

# 取得したデータがbytes型なので、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
bytes_reqdata = req.data
str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

print('返ってきたデータ＝')
print(str_shiftjis)

# JSON形式の文字列を辞書型で取り出す
json_req = json.loads(str_shiftjis)

print()
print('p_no= ', json_req.get('p_no'))
print('p_errno= ', json_req.get('p_errno'))
print('p_err= ', json_req.get('p_err'))
print('sCLMID= ', json_req.get('sCLMID'))

my_p_error = int(json_req.get('p_errno'))
if my_p_error ==  0 :    # ログインエラーでない場合
    
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.2 引数名:CLMAuthLoginAck を参照してください。

    int_p_no = int(json_req.get('p_no'))

    # 暗証番号省略有無C     この値にかかわらずAPIの注文等では第２暗証番号が必須
    print('sSecondPasswordOmit= ', json_req.get('sSecondPasswordOmit'))
    
    # 譲渡益課税区分   1:特定、3:一般、5:NISA
    print('sZyoutoekiKazeiC= ', json_req.get('sZyoutoekiKazeiC'))
    
    my_sUrlRequest = json_req.get('sUrlRequest')    # request用仮想URL
    my_sUrlEvent = json_req.get('sUrlEvent')        # event用仮想URL
    print('sUrlRequest= ')
    print(json_req.get('sUrlRequest'))
    print('sUrlEvent= ')
    print(json_req.get('sUrlEvent'))



else :  # ログインに問題があった場合
    my_sUrlRequest = ''    # request用仮想URL
    my_sUrlEvent = ''        # event用仮想URL


print()
print('-- logout -------------------------------------------------------------')

if len(my_sUrlRequest) > 0 and len(my_sUrlEvent) > 0 :
    ## マニュアルの解説「（２）ログアウト」
    ##        {
    ##　　　　　"p_no":"2",
    ##　　　　　"p_sd_date":"2020.07.01-10:00:00.100",
    ##　　　　　"sCLMID":"CLMAuthLogoutRequest"
    ##　　　　}
    ##
    ##　　　要求例：
    ##　　　　仮想ＵＲＬ（REQUEST）/?{"p_no":"2","p_sd_date":"2020.07.01-10:00:00.100","sCLMID":"CLMAuthLogoutRequest"}
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # 3/43 No.3 引数名:CLMAuthLogoutRequest を参照してください。

    
    int_p_no += int_p_no    # p_noは、カウントアップする

    # システムデイトを所定の書式で取得
    int_systime = datetime.datetime.now()
    my_p_sd_date = int_systime.strftime('%Y.%m.%d-%H:%M:%S.%f')[:-3]

    my_sCLMID = 'CLMAuthLogoutRequest'  # logoutを指示。注文等はここ以下を変更する。

    # 返り値の表示形式指定
    my_sJsonOfmt = '5'    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定


    my_request = my_sUrlRequest     # ログインで取得した"sUrlRequest"の値がrequest用仮想URL
    my_request = my_request + '?{'
    my_request = my_request + '"p_no":' + '"' + str(int_p_no) + '"'
    my_request = my_request + ',' + '"p_sd_date":"' + my_p_sd_date + '"'
    my_request = my_request + ',' + '"sCLMID":' + '"' + my_sCLMID + '"'
    my_request = my_request + ',' + '"sJsonOfmt":"' + my_sJsonOfmt + '"'
    my_request = my_request + '}'

    print()
    print('my_request= ')
    print(my_request)


    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', my_request)
    print("req.status= ", req.status )
    
    # 戻り値がbytes型なので、json.loadsを利用できるようにstr型に変換する。文字コードはshift-jis。
    str_shiftjis = req.data.decode("shift-jis", errors="ignore")
    print('返ってきたデータ＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # 3/43 No.4 引数名:CLMAuthLogoutAck を参照してください。
    print('p_no= ', json_req.get("p_no"))
    print('sCLMID= ', json_req.get("sCLMID"))
    
else :
    print('ログインに失敗しました')
