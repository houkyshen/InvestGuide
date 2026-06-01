import os
import re
from docx import Document
from docx.shared import Inches
from lxml import etree

def docx_to_markdown(docx_path: str, md_path: str):
    """
    DOCX 转 Markdown（支持图片提取与嵌入）
    :param docx_path: 源docx文件路径
    :param md_path: 输出md文件路径
    """
    # 图片存放目录（和md同目录下的images文件夹）
    md_dir = os.path.dirname(md_path)
    img_dir = os.path.join(md_dir, "images")
    os.makedirs(img_dir, exist_ok=True)

    doc = Document(docx_path)
    md_content = []
    img_count = 0

    # 遍历文档段落
    for para in doc.paragraphs:
        para_text = para.text.strip()
        if not para_text:
            md_content.append("")
            continue

        # 简单标题判断（根据字号/样式，适配常规Word标题）
        style_name = para.style.name
        if style_name.startswith("Heading 1"):
            md_content.append(f"# {para_text}")
        elif style_name.startswith("Heading 2"):
            md_content.append(f"## {para_text}")
        elif style_name.startswith("Heading 3"):
            md_content.append(f"### {para_text}")
        else:
            md_content.append(para_text)

        # 提取段落中的内嵌图片
        for run in para.runs:
            # 注册命名空间
            nsmap = {
                'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
            }
            
            # 使用etree注册命名空间前缀
            for prefix, uri in nsmap.items():
                etree.register_namespace(prefix, uri)
            
            # 执行xpath查询
            blips = run.element.xpath(".//a:blip")
            
            for inline in blips:
                img_count += 1
                # 获取图片二进制数据
                r_ns = nsmap['r']
                blip_id = inline.attrib[f"{{{r_ns}}}embed"]
                image_part = doc.part.related_parts[blip_id]
                img_bytes = image_part.blob

                # 保存图片
                img_name = f"img_{img_count:03d}.png"
                img_save_path = os.path.join(img_dir, img_name)
                with open(img_save_path, "wb") as f:
                    f.write(img_bytes)

                # 写入MD图片语法（相对路径）
                md_content.append(f"![图片](images/{img_name})")

    # 处理表格（简易适配）
    for table in doc.tables:
        table_rows = []
        header_row = []
        for idx, row in enumerate(table.rows):
            row_cells = [cell.text.strip() for cell in row.cells]
            table_rows.append(row_cells)
            if idx == 0:
                header_row = row_cells

        if table_rows:
            md_content.append("")
            # 表头
            md_content.append("| " + " | ".join(header_row) + " |")
            # 分隔线
            md_content.append("| " + " | ".join(["---"] * len(header_row)) + " |")
            # 表格内容
            for row in table_rows[1:]:
                md_content.append("| " + " | ".join(row) + " |")
            md_content.append("")

    # 写入Markdown文件
    full_md = "\n".join(md_content)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(full_md)

    print(f"✅ 转换完成：{docx_path} -> {md_path}")
    print(f"🖼️  共提取 {img_count} 张图片，存放至：{img_dir}")

if __name__ == "__main__":
    # ========== 在这里修改你的文件路径 ==========
    SOURCE_DOCX = "9.如何分析公司业务 - 附图版本.docx"   # 你的docx文件名
    TARGET_MD = "9.如何分析公司业务 - 附图版本.md"     # 输出的md文件名
    # ===========================================

    if not os.path.exists(SOURCE_DOCX):
        print(f"❌ 错误：文件 {SOURCE_DOCX} 不存在")
    else:
        docx_to_markdown(SOURCE_DOCX, TARGET_MD)