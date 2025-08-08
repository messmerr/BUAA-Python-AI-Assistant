"""
AI服务模块 - 封装Google Gemini API调用
支持文本对话、系统提示词、流式响应和图片输入
"""

import os
import base64
import logging
from typing import List, Dict, Any, Optional, Union, Generator
from io import BytesIO
from PIL import Image

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

class GeminiAIService:
    """Gemini AI服务类"""
    
    def __init__(self):
        """初始化Gemini AI服务"""
        self.api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not self.api_key:
            raise ValueError("未找到GOOGLE_AI_API_KEY环境变量")
        
        # 配置API
        genai.configure(api_key=self.api_key)
        
        # 默认使用高性能flash模型
        self.model_name = "gemini-2.5-flash"
        
        # 安全设置 - 教育场景下不过滤内容
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        # 默认生成配置
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
    
    def _prepare_image(self, image_data: Union[str, bytes, Image.Image]) -> Dict[str, Any]:
        """
        准备图片数据用于API调用
        
        Args:
            image_data: 图片数据，可以是base64字符串、字节数据或PIL Image对象
            
        Returns:
            格式化的图片数据字典
        """
        try:
            if isinstance(image_data, str):
                # base64编码图片处理
                if image_data.startswith('data:image'):
                    # 移除MIME类型前缀
                    image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
            elif isinstance(image_data, bytes):
                image_bytes = image_data
            elif isinstance(image_data, Image.Image):
                # PIL Image转字节数据
                buffer = BytesIO()
                image_data.save(buffer, format='PNG')
                image_bytes = buffer.getvalue()
            else:
                raise ValueError("不支持的图片数据格式")
            
            return {
                "mime_type": "image/png",
                "data": image_bytes
            }
        except Exception as e:
            logger.error(f"图片数据准备失败: {e}")
            raise ValueError(f"图片数据处理错误: {e}")
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        images: Optional[List[Union[str, bytes, Image.Image]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        生成文本响应（非流式）
        
        Args:
            prompt: 用户输入的提示词
            system_prompt: 系统提示词（可选）
            images: 图片列表（可选）
            temperature: 温度参数（可选）
            max_tokens: 最大输出token数（可选）
            
        Returns:
            生成的文本响应
        """
        try:
            # 创建模型实例
            model = genai.GenerativeModel(
                model_name=self.model_name,
                safety_settings=self.safety_settings,
                system_instruction=system_prompt
            )
            
            # 准备生成配置
            config = self.generation_config.copy()
            if temperature is not None:
                config["temperature"] = temperature
            if max_tokens is not None:
                config["max_output_tokens"] = max_tokens
            
            # 准备内容
            content = [prompt]
            
            # 添加图片（如果有）
            if images:
                for image in images:
                    image_part = self._prepare_image(image)
                    content.append(image_part)
            
            # 生成响应
            response = model.generate_content(
                content,
                generation_config=config
            )
            
            if response.text:
                return response.text
            else:
                logger.warning("API返回空响应")
                return "抱歉，我无法生成响应。"
                
        except Exception as e:
            logger.error(f"文本生成失败: {e}")
            raise Exception(f"AI服务调用失败: {e}")
    
    def generate_text_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        images: Optional[List[Union[str, bytes, Image.Image]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Generator[str, None, None]:
        """
        生成流式文本响应
        
        Args:
            prompt: 用户输入的提示词
            system_prompt: 系统提示词（可选）
            images: 图片列表（可选）
            temperature: 温度参数（可选）
            max_tokens: 最大输出token数（可选）
            
        Yields:
            逐步生成的文本片段
        """
        try:
            # 创建模型实例
            model = genai.GenerativeModel(
                model_name=self.model_name,
                safety_settings=self.safety_settings,
                system_instruction=system_prompt
            )
            
            # 准备生成配置
            config = self.generation_config.copy()
            if temperature is not None:
                config["temperature"] = temperature
            if max_tokens is not None:
                config["max_output_tokens"] = max_tokens
            
            # 准备内容
            content = [prompt]
            
            # 添加图片（如果有）
            if images:
                for image in images:
                    image_part = self._prepare_image(image)
                    content.append(image_part)
            
            # 生成流式响应
            response = model.generate_content(
                content,
                generation_config=config,
                stream=True
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"流式文本生成失败: {e}")
            yield f"错误: AI服务调用失败: {e}"
    
    def chat_conversation(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        多轮对话
        
        Args:
            messages: 对话历史，格式为 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            system_prompt: 系统提示词（可选）
            temperature: 温度参数（可选）
            max_tokens: 最大输出token数（可选）
            
        Returns:
            AI的回复
        """
        try:
            # 创建模型实例
            model = genai.GenerativeModel(
                model_name=self.model_name,
                safety_settings=self.safety_settings,
                system_instruction=system_prompt
            )
            
            # 准备生成配置
            config = self.generation_config.copy()
            if temperature is not None:
                config["temperature"] = temperature
            if max_tokens is not None:
                config["max_output_tokens"] = max_tokens
            
            # 开始聊天会话
            chat = model.start_chat(history=[])
            
            # 构建对话历史
            for i, message in enumerate(messages[:-1]):
                if message["role"] == "user":
                    chat.send_message(message["content"])
            
            # 发送最新消息获取响应
            if messages and messages[-1]["role"] == "user":
                response = chat.send_message(
                    messages[-1]["content"],
                    generation_config=config
                )
                return response.text if response.text else "抱歉，我无法生成响应。"
            else:
                raise ValueError("最后一条消息必须是用户消息")
                
        except Exception as e:
            logger.error(f"对话生成失败: {e}")
            raise Exception(f"AI对话服务调用失败: {e}")


# 创建全局服务实例
try:
    gemini_service = GeminiAIService()
except Exception as e:
    logger.error(f"Gemini服务初始化失败: {e}")
    gemini_service = None


# 便捷函数
def ask_gemini(
    prompt: str,
    system_prompt: Optional[str] = None,
    images: Optional[List[Union[str, bytes, Image.Image]]] = None,
    stream: bool = False,
    **kwargs
) -> Union[str, Generator[str, None, None]]:
    """
    便捷的Gemini调用函数
    
    Args:
        prompt: 用户提示词
        system_prompt: 系统提示词
        images: 图片列表
        stream: 是否使用流式响应
        **kwargs: 其他参数（temperature, max_tokens等）
        
    Returns:
        文本响应或流式生成器
    """
    if not gemini_service:
        raise Exception("Gemini服务未正确初始化")
    
    if stream:
        return gemini_service.generate_text_stream(
            prompt=prompt,
            system_prompt=system_prompt,
            images=images,
            **kwargs
        )
    else:
        return gemini_service.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            images=images,
            **kwargs
        )
