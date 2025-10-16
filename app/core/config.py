import os
import yaml
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_CONFIG_FILENAMES = ("config.local.yaml", "config.yaml")
ENV_CONFIG_FILE_VAR = "AGENT_CONFIG_FILE"
ENV_CONFIG_DIR_VAR = "AGENT_CONFIG_DIR"


class Settings(BaseSettings):
    """应用配置设置"""
    
    # Agent API 配置
    API_BASE_URL: str = Field(default="https://agent.bit.edu.cn", env="AGENT_API_BASE_URL")
    APP_ID: str = Field(env="AGENT_APP_ID")
    API_KEY: str = Field(env="AGENT_API_KEY")
    
    # 服务器配置
    SERVER_HOST: str = Field(default="0.0.0.0", env="SERVER_HOST")
    SERVER_PORT: int = Field(default=8000, env="SERVER_PORT")
    API_AUTH_KEY: Optional[str] = Field(default="", env="API_AUTH_KEY")
    
    # 会话管理配置
    MAX_CONVERSATIONS: int = Field(default=1000, env="MAX_CONVERSATIONS")
    CONVERSATION_TIMEOUT: int = Field(default=3600, env="CONVERSATION_TIMEOUT")
    
    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    VERBOSE_LOGGING: bool = Field(default=False, env="VERBOSE_LOGGING")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


class ConfigLoader:
    """配置文件加载器"""
    
    def __init__(self):
        self._config = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        candidate_files = self._build_candidate_paths()

        for config_path in candidate_files:
            if not config_path:
                continue

            try:
                with config_path.open('r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
                print(f"已加载配置文件: {config_path}")
                return
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"加载配置文件 {config_path} 失败: {e}")

        print("警告: 未找到配置文件，使用默认配置")
        self._config = self._get_default_config()

    def _build_candidate_paths(self):
        """构建配置文件搜索路径列表"""
        candidates = []

        # 环境变量指定的文件优先
        explicit_path = os.environ.get(ENV_CONFIG_FILE_VAR)
        if explicit_path:
            candidates.append(Path(explicit_path).expanduser())

        # 环境变量指定的目录
        explicit_dir = os.environ.get(ENV_CONFIG_DIR_VAR)
        if explicit_dir:
            dir_path = Path(explicit_dir).expanduser()
            candidates.extend(dir_path / name for name in DEFAULT_CONFIG_FILENAMES)

        # 项目根目录
        candidates.extend(PROJECT_ROOT / name for name in DEFAULT_CONFIG_FILENAMES)

        # 当前工作目录（兼容旧行为）
        cwd = Path.cwd()
        if cwd != PROJECT_ROOT:
            candidates.extend(cwd / name for name in DEFAULT_CONFIG_FILENAMES)

        # 去重并返回
        unique_candidates = []
        seen = set()
        for path in candidates:
            try:
                resolved = path.resolve()
            except FileNotFoundError:
                resolved = path
            if resolved not in seen:
                seen.add(resolved)
                unique_candidates.append(path)

        return unique_candidates
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            'agent': {
                'api_base_url': 'https://agent.bit.edu.cn',
                'app_id': '',
                'api_key': ''
            },
            'server': {
                'host': '0.0.0.0',
                'port': 8000,
                'auth_key': ''
            },
            'session': {
                'max_conversations': 1000,
                'timeout': 3600
            },
            'logging': {
                'level': 'INFO',
                'verbose': False
            }
        }
    
    def get(self, key_path, default=None):
        """获取配置值，支持点号分隔的路径"""
        keys = key_path.split('.')
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value


# 创建配置加载器实例
config_loader = ConfigLoader()

# 创建设置实例，优先使用配置文件中的值
settings = Settings(
    API_BASE_URL=config_loader.get("agent.api_base_url", "https://agent.bit.edu.cn"),
    APP_ID=config_loader.get("agent.app_id", ""),
    API_KEY=config_loader.get("agent.api_key", ""),
    SERVER_HOST=config_loader.get("server.host", "0.0.0.0"),
    SERVER_PORT=config_loader.get("server.port", 8000),
    API_AUTH_KEY=config_loader.get("server.auth_key", ""),
    MAX_CONVERSATIONS=config_loader.get("session.max_conversations", 1000),
    CONVERSATION_TIMEOUT=config_loader.get("session.timeout", 3600),
    LOG_LEVEL=config_loader.get("logging.level", "INFO"),
    VERBOSE_LOGGING=config_loader.get("logging.verbose", False)
)

# 验证必需的配置
if not settings.APP_ID:
    raise ValueError("APP_ID 未配置！请在 config.local.yaml 中设置 agent.app_id 或设置环境变量 AGENT_APP_ID")
if not settings.API_KEY:
    raise ValueError("API_KEY 未配置！请在 config.local.yaml 中设置 agent.api_key 或设置环境变量 AGENT_API_KEY")

print(f"配置加载完成:")
print(f"  API Base URL: {settings.API_BASE_URL}")
print(f"  APP ID: {settings.APP_ID[:8]}..." if settings.APP_ID else "  APP ID: 未配置")
print(f"  API Key: {'已配置' if settings.API_KEY else '未配置'}")
print(f"  服务器: {settings.SERVER_HOST}:{settings.SERVER_PORT}")
print(f"  认证: {'已启用' if settings.API_AUTH_KEY else '未启用'}") 
