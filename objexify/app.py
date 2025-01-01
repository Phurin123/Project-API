from flask import Flask, request, jsonify, send_from_directory
import uuid
import os
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from flask_cors import CORS

# การตั้งค่า Flask
app = Flask(__name__)
CORS(app)

# การตั้งค่าการอัปโหลดไฟล์
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# สร้างโฟลเดอร์สำหรับการอัปโหลดไฟล์หากไม่มี
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# โหลดโมเดล YOLO
try:
    model_path = r"C:\Users\lovew\OneDrive\เอกสาร\Project website คอมนี้เท่านั้น\best-porn.pt"  # เปลี่ยนเส้นทางหากจำเป็น
    model = YOLO(model_path)
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    model = None

# ฟังก์ชันตรวจสอบประเภทไฟล์
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# API สำหรับขอ API Key
@app.route('/request-api-key', methods=['POST'])
def request_api_key():
    data = request.get_json()
    email = data.get('email')
    if email:
        api_key = str(uuid.uuid4())
        return jsonify({'apiKey': api_key})
    return jsonify({'error': 'Email is required'}), 400

# API สำหรับการวิเคราะห์ภาพ
@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    if model is None:
        return jsonify({'error': 'Model not loaded successfully'}), 500

    # ตรวจสอบว่าไฟล์ภาพถูกส่งมาหรือไม่
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    
    # ตรวจสอบว่าไฟล์เป็นไฟล์ภาพที่อนุญาต
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        # ใช้โมเดล YOLO วิเคราะห์ภาพ
        results = model.predict(source=file_path)
        has_inappropriate_content = False  # ตรวจสอบเนื้อหาที่ไม่เหมาะสม
        detections = []

        for result in results:
            for box in result.boxes:
                label = model.names[int(box.cls)]
                confidence = float(box.conf)
                if label.lower() in ["inappropriate", "porn"]:  # ตัวอย่างคลาสที่ถือว่าไม่เหมาะสม
                    has_inappropriate_content = True

                detections.append({
                    "label": label,
                    "confidence": confidence,
                    "bbox": box.xywh.tolist()
                })

        # ลบไฟล์ที่อัปโหลดหลังจากการวิเคราะห์
        os.remove(file_path)

        # ส่งผลลัพธ์กลับ
        return jsonify({
            'status': 'failed' if has_inappropriate_content else 'passed',
            'detections': detections
        })

    except Exception as e:
        os.remove(file_path)  # ลบไฟล์ในกรณีที่เกิดข้อผิดพลาด
        return jsonify({'error': f'Error during analysis: {e}'}), 500

# การให้บริการไฟล์ที่อัปโหลด
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# API สำหรับรายงานปัญหา
@app.route('/report-issue', methods=['POST'])
def report_issue():
    try:
        data = request.get_json()
        issue_description = data.get('issue')

        if issue_description:
            with open('issues.txt', 'a') as file:
                file.write(issue_description + '\n')
            return jsonify({'success': True})
        return jsonify({'error': 'Issue description is required'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API สำหรับข้อเสนอแนะ
@app.route('/submit-suggestion', methods=['POST'])
def submit_suggestion():
    try:
        data = request.get_json()
        suggestion_description = data.get('suggestion')

        if suggestion_description:
            with open('suggestions.txt', 'a') as file:
                file.write(suggestion_description + '\n')
            return jsonify({'success': True})
        return jsonify({'error': 'Suggestion description is required'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API สำหรับดาวน์โหลดเอกสารคู่มือ
@app.route('/download-manual', methods=['GET'])
def download_manual():
    manual_path = r'C:\Users\lovew\OneDrive\เอกสาร\Project website\Project\backend\static\manual.pdf'  # เส้นทางไฟล์เอกสารคู่มือ
    if os.path.exists(manual_path):
        return send_from_directory(os.path.dirname(manual_path), os.path.basename(manual_path), as_attachment=True)
    return jsonify({'error': 'Manual file not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
































