import random
import re

from flask import request, abort, current_app, make_response, json, jsonify

from info import redis_store, constants
from info.libs.yuntongxun.sms import CCP
from info.utils.response_code import RET
from . import passport_blu
from info.utils.captcha.captcha import captcha

@passport_blu.route('/sms_code',methods=["POST"])
def send_sms_code():
    """
    发送短信的逻辑
    1.获取参数:手机号,图片验证码内容,图片验证码的编号(随机值)
    2.校验参数(参数是否符合规则,判断是否有值)
    3.先从redis中取出真实的验证码内容
    4.与用户的验证码内容进行对比,如果对比不一致,那么返回验证码输入错误
    5.如果一致,生成验证码的内容(随机数据)
    6.发送短信验证码
    7.告知发送结果
    :return:
    """
    '{"mobiel":"18811111111","image_code":"AAAA","image_code_id":"jkhdhskfjvhsdkjv"}'
    # 1.获取参数:手机号,图片验证码内容,图片验证码的编号(随机值)
    # params_dict = json.loads(request.data)
    params_dict = request.json

    mobile = params_dict.get("mobile")
    image_code = params_dict.get("image_code")
    image_code_id = params_dict.get("image_code_id")


    # 2.校验参数(参数是否符合规则,判断是否有值)

    if not all(mobile,image_code,image_code_id):
        # {"errno":"4100","errmsg":"参数有误"}
        return jsonify(errno=RET.PARAMERR,errmsg="参数有误")
    # 校验手机号是否正确
    if not re.match('1[35678]\\d{9}'):
        return jsonify(errno=RET.PARAMERR,errmsg="手机号格式不正确")
    # 3.先从redis中取出真实的验证码内容
    try:
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据查询失败")

    if not real_image_code:
        return jsonify(errno=RET.DBERR,errmsg="图片验证码已过期")

    # 4.与用户的验证码内容进行对比,如果对比不一致,那么返回验证码输入错误
    if real_image_code.upper() !=image_code.upper():
        return jsonify(errno=RET.DATAERR,errmsg="验证码输入错误")

    # 5.如果一致,生成验证码的内容(随机数据)
    # 随机数字,保证数字长度为6位,不够不够在前面补0
    sms_code_str = "%06d" % random.randint(0,999999)
    current_app.logger.debug("短信验证码内容是:%s" % sms_code_str)
    # 发送短信验证码
    result = CCP().send_template_sms(mobile,[sms_code_str,constants.SMS_CODE_REDIS_EXPIRES/60],"1")
    if result != 0:
        # 代表发送不成功
        return jsonify(errno=RET.DBERR,errmsg="短信发送失败")

    try:
        redis_store.set("SMS" + mobile, sms_code_str)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 7.告知发送结果
    return jsonify(errno=RET.OK,errmsg="发送成功")

    # 保存验证码内容到redis







@passport_blu.route('/image_code')
def get_image_code():
    """
    生成图片验证码并返回
    1.取到参数
    2.判断参数是否有值
    3.生成图片验证码
    4.保存图片验证码文字到redis
    5.返回验证码图片
    :return:
    """

    # 1.取到参数
    # args:取到url中?后面的参数
    image_code_id = request.args.get("imageCodeId",None)
    # 2.判断参数是否有值
    if not image_code_id:
        return abort(403)
    # 3.生成图片验证码
    name,text,image = captcha.generate_captcha()

    # 4.保存图片验证码文字到redis
    try:
        redis_store.set("ImageCodeId" + image_code_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)


    # 5.返回验证码图片
    response = make_response(image)
    # 设置数据类型,以便浏览器更加智能识别其是什么类型
    response.headers["Content-Type"] = "image/jpg"
    return response






