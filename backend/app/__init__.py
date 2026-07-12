"""
MiroFish Backend - Flask应用工厂
"""

import os
import warnings

# 抑制 multiprocessing resource_tracker 的警告（来自第三方库如 transformers）
# 需要在所有其他导入之前设置
warnings.filterwarnings("ignore", message=".*resource_tracker.*")

from flask import Flask, request
from flask_cors import CORS

from .config import Config
from .utils.logger import setup_logger, get_logger


def create_app(config_class=Config):
    """Flask应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 设置JSON编码：确保中文直接显示（而不是 \uXXXX 格式）
    # Flask >= 2.3 使用 app.json.ensure_ascii，旧版本使用 JSON_AS_ASCII 配置
    if hasattr(app, 'json') and hasattr(app.json, 'ensure_ascii'):
        app.json.ensure_ascii = False
    
    # 设置日志
    logger = setup_logger('mirofish')
    
    # 只在 reloader 子进程中打印启动信息（避免 debug 模式下打印两次）
    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    debug_mode = app.config.get('DEBUG', False)
    should_log_startup = not debug_mode or is_reloader_process
    
    if should_log_startup:
        logger.info("=" * 50)
        logger.info("MiroFish Backend 启动中...")
        logger.info("=" * 50)
    
    # 启用CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 注册模拟进程清理函数（确保服务器关闭时终止所有模拟进程）
    from .services.simulation_runner import SimulationRunner
    SimulationRunner.register_cleanup()
    if should_log_startup:
        logger.info("已注册模拟进程清理函数")
    
    # 请求日志中间件
    @app.before_request
    def log_request():
        logger = get_logger('mirofish.request')
        logger.debug(f"请求: {request.method} {request.path}")
        if request.content_type and 'json' in request.content_type:
            logger.debug(f"请求体: {request.get_json(silent=True)}")
    
    @app.after_request
    def log_response(response):
        logger = get_logger('mirofish.request')
        logger.debug(f"响应: {response.status_code}")
        return response
    
    # 注册蓝图
    from .api import graph_bp, simulation_bp, report_bp
    app.register_blueprint(graph_bp, url_prefix='/api/graph')
    app.register_blueprint(simulation_bp, url_prefix='/api/simulation')
    app.register_blueprint(report_bp, url_prefix='/api/report')
    
    # 健康检查
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'MiroFish Backend'}

    # Настройки, изменяемые из интерфейса: текущая LLM-модель
    from .utils import runtime_config

    @app.route('/api/config/model', methods=['GET'])
    def get_active_model():
        return {
            'success': True,
            'model': runtime_config.get_model() or Config.LLM_MODEL_NAME,
            'base_url': Config.LLM_BASE_URL,
            'source': 'ui' if runtime_config.get_model() else 'env',
        }

    @app.route('/api/config/model', methods=['POST'])
    def set_active_model():
        data = request.get_json(silent=True) or {}
        model = (data.get('model') or '').strip()
        if not model:
            return {'success': False, 'error': 'model is required'}, 400
        runtime_config.set_model(model)
        get_logger('mirofish').info(f"LLM-модель переключена на: {model}")
        return {'success': True, 'model': model}

    # Вычислительный режим: v100 | lmstudio | both
    @app.route('/api/config/compute', methods=['GET'])
    def get_compute():
        return {
            'success': True,
            'mode': runtime_config.get_mode(),
            'ollama_model': runtime_config.get_model() or runtime_config.DEFAULT_OLLAMA_MODEL,
            'lmstudio_model': runtime_config.get_lmstudio_model(),
            'ollama_base': runtime_config.OLLAMA_BASE,
            'lmstudio_base': runtime_config.LMSTUDIO_BASE,
            'heavy': runtime_config.resolve_endpoint('heavy'),
            'light': runtime_config.resolve_endpoint('light'),
        }

    @app.route('/api/config/compute', methods=['POST'])
    def set_compute():
        data = request.get_json(silent=True) or {}
        mode = (data.get('mode') or '').strip()
        if mode not in ('v100', 'lmstudio', 'both'):
            return {'success': False, 'error': 'mode must be v100 | lmstudio | both'}, 400
        runtime_config.set_mode(mode)
        if data.get('ollama_model'):
            runtime_config.set_model(data['ollama_model'].strip())
        if data.get('lmstudio_model'):
            runtime_config.set_lmstudio_model(data['lmstudio_model'].strip())
        get_logger('mirofish').info(f"Вычислительный режим: {mode}")
        return {'success': True, 'mode': mode}
    
    if should_log_startup:
        logger.info("MiroFish Backend 启动完成")
    
    return app

