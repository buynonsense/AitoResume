from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import uuid
from datetime import datetime
from resume_generator import ResumeGenerator
import werkzeug.utils

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join('static', 'resumes')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制

# 确保上传和输出目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_resume():
    try:
        # 获取表单数据
        job_description = request.form.get('job_description', '')
        
        if not job_description:
            return jsonify({'success': False, 'error': '请提供岗位描述'}), 400
        
        # 处理裁剪后的照片数据
        uploaded_photo = None
        cropped_photo_data = request.form.get('cropped_photo')
        
        if cropped_photo_data and cropped_photo_data.startswith('data:image/'):
            # 直接使用裁剪好的base64数据
            uploaded_photo = cropped_photo_data
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        output_basename = f"resume_{timestamp}_{unique_id}"
        
        # 初始化简历生成器
        resume_gen = ResumeGenerator(
            output_dir=app.config['OUTPUT_FOLDER'],
            template_path='templates/resume_template.html'
        )
        
        # 生成简历 - 传入base64图片数据
        html_path = resume_gen.create_resume(
            job_description, 
            output_basename,
            uploaded_photo=uploaded_photo
        )
        
        # 构建响应
        filename = os.path.basename(html_path)
        file_url = f"/resumes/{filename}"
        
        return jsonify({
            'success': True, 
            'file_url': file_url,
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/resumes/<filename>')
def serve_resume(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/resumes/assets/<filename>')
def serve_resume_assets(filename):
    assets_dir = os.path.join(app.config['OUTPUT_FOLDER'], 'assets')
    return send_from_directory(assets_dir, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)