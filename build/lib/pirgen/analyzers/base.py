# analyzers/base.py
from abc import ABC, abstractmethod
from ..core.project_model import ProjectModel

class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, file_path: str, unit_uid: str, model: ProjectModel):
        """
        分析单个文件，提取符号和依赖，填充到 model 中。
        """
        pass