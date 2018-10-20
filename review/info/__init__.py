import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config

# 初始化扩展对象,然后再去调用init_app方法初始化


db = SQLAlchemy()
redis_store = None  # type: StrictRedis


def setup_log(config_name):
    """设置日志信息"""

    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """创建app"""

    # 设置日志
    setup_log(config_name)
    # 创建app应用
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[config_name])
    # 初始化数据库
    db.init_app(app)
    # 初始化redis存储对象
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST,
                              port=config[config_name].REDIS_PORT)
    # 开启CSRF项目保护,只做服务器的验证
    CSRFProtect(app)
    # 设置session保存到指定位置
    Session(app)

    # 注册主页蓝图
    from review.info.modules.index import index_blu
    app.register_blueprint(index_blu)

    # 返回app对象
    return app
