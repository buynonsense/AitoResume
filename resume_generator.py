import yaml
import os
import argparse
from datetime import datetime
import dotenv
import requests
import json
import re
import base64
from PIL import Image
from jinja2 import Template
from io import BytesIO

class ResumeGenerator:
    def __init__(self, personal_info_path='personal_info.yaml', 
                template_path='templates/resume_template.html',
                output_dir=None):
        """初始化简历生成器"""
        # 加载.env配置
        dotenv.load_dotenv()
        self.api_provider = os.getenv('AI_PROVIDER', 'openai').lower()  # 默认使用openai兼容API
        self.api_key = os.getenv('AI_API_KEY')
        self.model = os.getenv('AI_MODEL')
        
        # Ollama和OpenAI配置分开处理
        if self.api_provider == 'openai':
            self.api_base = os.getenv('AI_API_BASE')
            print(f"使用API提供商: OpenAI兼容")
            print(f"API基础URL: {self.api_base}")
        else:  # ollama
            # Ollama不使用api_base
            self.api_base = None
            print(f"使用API提供商: Ollama")
            print(f"使用模型: {self.model}")
        
        # 加载个人信息
        with open(personal_info_path, 'r', encoding='utf-8') as f:
            self.personal_info = yaml.safe_load(f)
        
        # 加载HTML模板
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template_html = f.read()
            
        # 创建Jinja2模板
        self.template = Template(self.template_html)
        
        # 设置输出目录
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join(os.getcwd(), "output")
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
    
    def call_ai_api(self, messages, temperature=0.7):
        """根据配置调用不同的AI API"""
        if self.api_provider == 'ollama':
            return self._call_ollama_api(messages, temperature)
        else:
            return self._call_openai_compatible_api(messages, temperature)

    def _call_openai_compatible_api(self, messages, temperature=0.7):
        """调用兼容OpenAI格式的API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }
        
        response = requests.post(
            f"{self.api_base}/chat/completions", 
            headers=headers,
            data=json.dumps(payload)
        )
        
        if response.status_code != 200:
            raise Exception(f"API调用失败: {response.text}")
        
        return response.json()

    def _call_ollama_api(self, messages, temperature=0.7):
        """调用Ollama API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        # 转换消息格式为Ollama格式
        prompt = self._convert_messages_to_ollama_format(messages)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }
        
        # 明确指定完整URL（不依赖self.api_base）
        api_url = f"http://localhost:11434/api/generate"
        
        print(f"正在调用Ollama API: {api_url}")
        print(f"请求数据: {payload}")
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload  # 使用json参数代替data，处理序列化
            )
            
            print(f"响应状态码: {response.status_code}")
            if response.status_code != 200:
                print(f"错误详情: {response.text}")
                raise Exception(f"Ollama API调用失败: {response.text}")
            
            # 转换Ollama返回格式为OpenAI格式以保持一致性
            result = response.json()
            return {
                "choices": [{
                    "message": {
                        "content": result.get('response', '')
                    }
                }]
            }
        except Exception as e:
            print(f"API调用异常: {str(e)}")
            raise e

    def _convert_messages_to_ollama_format(self, messages):
        """将OpenAI格式的消息转换为Ollama格式的提示"""
        prompt = ""
        for msg in messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            
            if role == 'system':
                prompt += f"<system>\n{content}\n</system>\n\n"
            elif role == 'user':
                prompt += f"<human>\n{content}\n</human>\n\n"
            elif role == 'assistant':
                prompt += f"<assistant>\n{content}\n</assistant>\n\n"
        
        # 添加最后的助手标记，表示等待模型回复
        prompt += "<assistant>\n"
        return prompt
    
    def generate_job_specific_content(self, job_description):
        """使用AI生成与岗位相关的简历内容"""
        
        # 修改提示词，明确不要为自我评价添加缩进
        prompt = f"""
        基于以下个人背景和岗位描述，生成匹配的简历内容。
        
        ## 个人背景
        教育经历: {self.personal_info['education']}
        证书: {self.personal_info['certificates']}
        
        ## 岗位描述
        {job_description}
        
        请生成以下内容（纯JSON格式，不要包含Markdown代码块标记）:
        {{
        "求职意向": "职位、工作地点、薪资范围",
        "主修课程": "课程1, 课程2, 课程3...", // 必须使用逗号分隔，不要使用HTML标签，不要换行
        "掌握技能": "<div class='skill-item'>技能1: 精通</div><div class='skill-item'>技能2: 熟练</div>...",
        "自我评价": "<p>评价段落1</p><p>评价段落2</p>..." // 不要添加缩进样式，保持左对齐
        }}
        
        请确保返回的是可直接解析的纯JSON，不要添加任何代码块标记如```json。
        对于主修课程，请提供逗号分隔的纯文本；对于掌握技能请提供带样式的HTML；对于自我评价提供不带缩进的HTML。
        """
        
        messages = [
            {"role": "system", "content": "你是一位专业的HR顾问，擅长针对特定岗位优化简历内容。你需要以纯JSON格式回答，不要添加任何代码块标记。"},
            {"role": "user", "content": prompt}
        ]
        
        response = self.call_ai_api(messages, temperature=0.7)
        content = response['choices'][0]['message']['content'].strip()
        
        # 清理可能的代码块标记
        content = re.sub(r'^```json\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        
        try:
            # 尝试用json解析而不是yaml
            return json.loads(content)
        except Exception as e:
            print(f"解析AI响应失败: {e}")
            print(f"原始响应: {content}")
            # 返回一个简单的默认结构
            return {
                "求职意向": "请检查AI响应格式并手动完成",
                "主修课程": "<div>计算机科学导论</div><div>数据结构</div><div>算法分析</div>",
                "掌握技能": "<div>编程语言: Python, Java, C++</div><div>框架: Flask, Django</div>", 
                "自我评价": "<p>具有扎实的理论基础和实践经验</p><p>良好的团队协作能力</p>"
            }
    
    def enhance_project_experience(self, job_description):
        """基于已有项目经验和岗位描述，增强项目经验部分"""
        
        projects = self.personal_info.get('projects', [])
        enhanced_projects = []
        
        for project in projects:
            # 修改提示词，明确表示不需要首行缩进
            prompt = f"""
            基于以下项目经验和目标岗位描述，优化项目经验描述，使其更符合岗位需求，并突出相关技能和成就。
            
            ## 原始项目描述
            项目名称: {project['name']}
            时间: {project['time_period']}
            描述: {project['description']}
            
            ## 目标岗位
            {job_description}
            
            请提供优化后的项目描述：
            1. 项目名称保持不变
            2. 时间保持不变
            3. 提供HTML格式的增强项目描述，突出与目标岗位相关的技能和成就
            4. 使用段落标签<p>包裹内容，不要为段落添加缩进样式
            5. 使用STAR法则(情境、任务、行动、结果)展开描述
            6. 描述控制在150-200字之间
            7. 重要：不要使用缩进，保持段落左对齐
            """
            
            messages = [
                {"role": "system", "content": "你是一位简历优化专家，擅长针对特定岗位优化项目经验描述。请返回HTML格式的描述。"},
                {"role": "user", "content": prompt}
            ]
            
            response = self.call_ai_api(messages, temperature=0.7)
            
            content = response['choices'][0]['message']['content'].strip()
            # 清理可能的标记
            content = re.sub(r'^```html\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            
            # 确保描述内容有HTML标签，如果没有，添加<p>标签
            if not content.strip().startswith("<"):
                content = f"<p>{content}</p>"
            
            enhanced_projects.append({
                'name': project['name'],
                'time_period': project['time_period'],
                'description': content
            })
            
        return enhanced_projects
    
    def process_photo(self, photo_data):
        """处理照片数据（可以是文件路径或base64数据）"""
        try:
            # 检查是否已经是base64数据
            if isinstance(photo_data, str) and photo_data.startswith('data:image/'):
                # 已经是裁剪好的base64数据，直接返回
                return photo_data
                
            # 否则，假设这是一个文件路径
            if not os.path.exists(photo_data):
                return None
                
            # 打开图片并编码为base64
            with open(photo_data, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                return f"data:image/jpeg;base64,{img_data}"
                
        except Exception as e:
            print(f"照片处理失败: {e}")
            return None
    
    def create_resume(self, job_description, output_basename=None, uploaded_photo=None):
        """生成HTML格式的简历"""
        # 生成岗位相关内容
        print("正在生成与岗位匹配的简历内容...")
        job_specific_content = self.generate_job_specific_content(job_description)
        
        # 处理主修课程格式 - 确保是逗号分隔的单行文本
        if "主修课程" in job_specific_content:
            courses = job_specific_content["主修课程"]
            # 移除任何HTML标签
            courses = re.sub(r'<[^>]+>', '', courses)
            # 确保使用逗号分隔且没有多余换行
            courses = re.sub(r'\s+', ' ', courses).strip()
            courses = re.sub(r'，', ', ', courses)  # 统一使用英文逗号
            job_specific_content["主修课程"] = courses
        
        # 自我评价格式 - 移除缩进样式
        if "自我评价" in job_specific_content:
            evaluation = job_specific_content["自我评价"]
            # 移除已添加的缩进类
            evaluation = re.sub(r'class=["\']indent["\']', '', evaluation)
            job_specific_content["自我评价"] = evaluation
        
        # 增强项目经验
        print("正在优化项目经验...")
        enhanced_projects = self.enhance_project_experience(job_description)

        # 处理手动置顶技能（如果有）并将其置于AI生成技能之前
        def _format_manual_skills(manual_skills):
            """将 manual_skills 规范化为 HTML 字符串，保证每项使用 .skill-item 包裹"""
            if not manual_skills:
                return ''

            # 如果是单个字符串，可能已经是HTML或逗号分隔的纯文本
            if isinstance(manual_skills, str):
                s = manual_skills.strip()
                # 简单判断是不是HTML（包含<div>或<span>)
                if re.search(r'<\s*div|<\s*span|<\s*ul', s):
                    return s
                # 否则按逗号或换行分割
                parts = re.split(r'[,，\n]+', s)
            elif isinstance(manual_skills, list):
                parts = [str(x).strip() for x in manual_skills if str(x).strip()]
            else:
                # 其他类型，转为字符串并作为一项
                parts = [str(manual_skills).strip()]

            items = []
            for p in parts:
                if not p:
                    continue
                # 如果已经包含 .skill-item 类，则直接保留
                if re.search(r"class=[\"']?skill-item[\"']?", p):
                    items.append(p)
                else:
                    # 转义 HTML 特殊字符简单处理
                    esc = (p.replace('&', '&amp;')
                           .replace('<', '&lt;')
                           .replace('>', '&gt;'))
                    items.append(f"<div class='skill-item'>{esc}</div>")

            return ''.join(items)

        manual_skills = self.personal_info.get('manual_skills')
        manual_html = _format_manual_skills(manual_skills)

        # 合并AI生成的掌握技能，手工技能放在前
        ai_skills_html = job_specific_content.get('掌握技能', '') or ''
        # 如果AI返回的是纯文本（无<div>），则尝试按逗号分割并包装
        if ai_skills_html and not re.search(r'<\s*div|<\s*span|<\s*ul', ai_skills_html):
            parts = re.split(r'[,，\n]+', ai_skills_html)
            wrapped = ''.join([f"<div class='skill-item'>{p.strip()}</div>" for p in parts if p.strip()])
            ai_skills_html = wrapped

        # 最终的掌握技能HTML：手动在前，AI在后。如果两者都有逗号分隔或原生HTML则保留
        if manual_html and ai_skills_html:
            job_specific_content['掌握技能'] = manual_html + ai_skills_html
        elif manual_html:
            job_specific_content['掌握技能'] = manual_html
        else:
            job_specific_content['掌握技能'] = ai_skills_html
        
        # 修改项目经验中的缩进
        for project in enhanced_projects:
            # 移除项目描述中的缩进
            content = project['description']
            content = re.sub(r'text-indent:\s*2em;', '', content)
            content = re.sub(r'class=["\']indent["\']', '', content)
            project['description'] = content
        
        # 设置输出文件名
        if not output_basename:
            date_str = datetime.now().strftime("%Y%m%d")
            job_type = job_description.split()[:2]
            if job_type:
                job_type = ''.join(job_type)
            else:
                job_type = "resume"
            output_basename = f"Resume_{date_str}_{job_type}"
        
        # 处理照片 - 可能是文件路径或已经裁剪好的base64数据
        photo_path = None
        if uploaded_photo:
            photo_path = self.process_photo(uploaded_photo)
        
        # 构建简历HTML内容
        print("正在构建简历HTML...")
        html_content = self.template.render(
            personal=self.personal_info,
            job_content=job_specific_content,
            projects=enhanced_projects,
            photo_path=photo_path
        )
        
        # 保存HTML文件
        html_output_path = os.path.join(self.output_dir, f"{output_basename}.html")
        with open(html_output_path, 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)
        
        print(f"简历已生成: {html_output_path}")
        return html_output_path

# 命令行功能如果需要单独使用
def main():
    parser = argparse.ArgumentParser(description="根据岗位描述生成定制简历")
    parser.add_argument("--job", "-j", help="岗位描述文件路径", required=True)
    parser.add_argument("--output", "-o", help="输出文件名基础名称(不含扩展名)", required=False)
    parser.add_argument("--photo", "-p", help="照片文件路径", required=False)
    args = parser.parse_args()
    
    # 读取岗位描述
    with open(args.job, 'r', encoding='utf-8') as f:
        job_description = f.read()
    
    # 生成简历
    resume_gen = ResumeGenerator()
    resume_gen.create_resume(job_description, args.output, uploaded_photo=args.photo)

if __name__ == "__main__":
    main()