from fastapi import HTTPException, UploadFile, File, APIRouter, Depends
from docx import Document
import pdfplumber
from db.crud import save_resume
from utils.auth import verify_token
router=APIRouter()
@router.post("")
async def upload_resume(file:UploadFile=File(...),user=Depends(verify_token)):
    """上传简历接口：解析 PDF、DOCX 或 TXT，并保存简历文本。"""
     # 判断文件类型
    file_name = file.filename or ""
    lower_file_name = file_name.lower()

    if not lower_file_name.endswith((".pdf", ".docx", ".txt")):
        raise HTTPException(status_code=400, detail="仅支持 PDF、DOCX、TXT 格式的简历")

    if lower_file_name.endswith(".pdf"):
        # 直接用 pdfplumber 处理字节流
        import io
        pdf_file = io.BytesIO(await file.read())
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
    elif lower_file_name.endswith(".docx"):
        # python-docx 也可以处理文件对象
        import io
        doc_file = io.BytesIO(await file.read())
        doc = Document(doc_file)
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        # txt
        text = (await file.read()).decode("utf-8")

    if not text.strip():
        raise HTTPException(status_code=400, detail="简历内容不能为空")
    
    resume = save_resume(user['user_id'],file_name,text)
    

    return {"resume_id": resume.id}  
