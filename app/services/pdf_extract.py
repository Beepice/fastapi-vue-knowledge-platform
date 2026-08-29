import pdfplumber
import pymupdf
import re
from loguru import logger
from pathlib import Path
from collections import Counter

from app.models.domain.rag import  FigureModel

FIGURE_PATTERN = re.compile(
    r'(图|Figure|Fig|Example\.?)\s*(\d+[-.]\d+)(.*)',
    re.IGNORECASE
)
class PDFParser:
    """主要使用pymupdf提取内容，pdfplumber完成表格提取"""
    def __init__(
            self
    ):
        self.document_id: int
        self.plumber_pf: pdfplumber.PDF
        self.pymu_pf: pymupdf.Document
        self.handled_pdf_path: Path
        self.page_height:int | float
        self.page_width:int | float
        """内容解析"""
        self.pages: list[list[dict]]
        self.style: dict={}
        self.heading_level:int
        self.chunks:list[list[dict]]
        self.figure_models:list[FigureModel]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_pdf()
        return False

    def open_pdf(
            self,
            document_id: int,
            pdf_path:Path
    ):
        self.document_id = document_id
        self.plumber_pf = pdfplumber.open(pdf_path)
        self.pymu_pf = pymupdf.open(pdf_path)

        self.handled_pdf_path = pdf_path
        self.page_height = self.pymu_pf[0].rect.height
        self.page_width = self.pymu_pf[0].rect.width


    def close_pdf(
            self
    ):
        logger.debug("完成文件解析，回收内存")
        self.plumber_pf.close()
        self.pymu_pf.close()
        self.document_id = None
        self.handled_pdf_path =None
        self.page_height =None
        self.page_width = None
        self.pages = None
        self.style = None
        self.heading_level = None
        self.chunks =None
        self.figure_models = None

    def _order_content(
            self,
            page: pymupdf.Page,
            page_number: int
    )->list[dict]:
        blocks = page.get_text("dict")["blocks"]
        all_lines = [block["lines"]for block in blocks if block["type"]==0]
        #每个span内容以第一个span为准，拼接为line
        flat_lines = [[span for span in line] for line in all_lines if line]
        flat_lines.sort(key=lambda line: line[0]["bbox"][1])
        results = []
        for line in flat_lines:
            text = " ".join(span["text"].strip() for spans in line for span in spans["spans"] if span)
            x_start, y_start, = line[0]["spans"][0]["bbox"][0],line[0]["spans"][0]["bbox"][1]
            size = line[0]["spans"][0]["size"]
            char_flags = line[0]["spans"][0]["char_flags"]
            color = line[0]["spans"][0]["color"]
            results.append({
                "text": text,
                "x_start": x_start,
                "y_start": y_start,
                "size": round(size),
                "char_flags": char_flags,
                "color": color,
                "level":0,
                "figure_ref":None,
                "page_number": page_number,
            })
        return results

    def _all_order_pages(
            self
    )->list[list[dict]]:
        results = []
        for i,page in enumerate(self.pymu_pf.pages()):
            order_content = self._order_content(page,page_number=i+1)
            results.append(order_content)
        self.pages = results
        return results

    def _remove_header_rooter(
            self,
            header_ratio:float=0.1,
            footer_ratio:float=0.9,
            filter_ratio:float=0.8,
    )->list[list[dict]]:
        """过滤页眉页脚"""
        flat_pages = self.pages
        header_occurrence = Counter()
        footer_occurrence = Counter()
        total_pages = len(flat_pages)
        for page in flat_pages:
            for line in page :
                if line["y_start"] < self.page_height * header_ratio:
                    key = round(line["y_start"])
                    header_occurrence[key] += 1
                elif line["y_start"] > self.page_height * footer_ratio:
                    key = round(line["y_start"])
                    footer_occurrence[key] += 1

        header_noise_set = [
            _y for _y, count in header_occurrence.items()
            if count > total_pages * filter_ratio
        ]
        footer_noise_set = [
            _y for _y, count in footer_occurrence.items()
            if count > total_pages * filter_ratio
        ]
        header_noise_set.sort()
        header_noise_set = header_noise_set[:3]
        footer_noise_set.sort()
        footer_noise_set = footer_noise_set[:3]
        for page in flat_pages:
            page[:] = [line for line in page
                       if round(line["y_start"]) not in header_noise_set and
                       round(line["y_start"]) not in footer_noise_set
            ]
        self.pages = flat_pages
        return flat_pages

    def _check_main_text_font(
            self
    )->int:
        flat_pages = self.pages
        occurrence = Counter()
        for page in flat_pages:
            for line in page :
                size = line["size"]
                occurrence[round(size)] += 1
        font_list = [ {"size":size,"count":count}  for size,count in occurrence.items()]
        font_list.sort(key=lambda key:key["count"], reverse=True)
        logger.debug(f"解析到正文文本字号大小为{font_list[0]["size"]}")
        self.style[0]={"size":font_list[0]["size"]}
        return font_list[0]["size"]

    def _check_style_for_line(
            self,
            level:int,
            line:dict
    ):
        if len(self.style) <= 1:
            return True
        else:
            if self.style[level]["size"] == line["size"]:
                return True
            else:
                return False

    def _match_heading(
            self,
            *,
            pattern:str,
            page_number:int | None,
            level:int,
            debug = False
    )->bool:
        if page_number:
            remember_line = []
            for _i in range(len(self.pages[page_number - 1])):
                if remember_line:
                    break
                idx,pdx = 0,0
                if debug:
                    print(self.pages[page_number - 1][_i]["text"])
                while (
                    self._check_style_for_line(level, self.pages[page_number - 1][_i]) and
                    idx < len(self.pages[page_number - 1][_i]["text"]) and
                    pdx < len(pattern)
                ):
                    if debug:
                        print(
                            f"{idx}:{len(self.pages[page_number - 1][_i]["text"])-1},{self.pages[page_number - 1][_i]["text"][idx]};"
                            f"{pdx}:{len(pattern)-1},{pattern[pdx]}"
                        )
                    if self.pages[page_number - 1][_i]["text"][idx] == " ":
                        idx += 1
                    elif pattern[pdx] == " ":
                        pdx += 1
                    elif self.pages[page_number - 1][_i]["text"][idx] != pattern[pdx]:
                        remember_line = []
                        break
                    elif self.pages[page_number - 1][_i]["text"][idx] == pattern[pdx]:
                        if (
                            idx == len(self.pages[page_number - 1][_i]["text"]) - 1 and
                            pdx == len(pattern) - 1
                        ):
                            remember_line.append(_i)
                            break
                        elif (
                            idx == len(self.pages[page_number - 1][_i]["text"]) - 1 and
                            pdx < len(pattern) - 1
                        ):
                            remember_line.append(_i)
                            _i+=1
                            idx = 0
                            pdx += 1
                            continue
                        else:
                            idx += 1
                            pdx += 1
                            continue
            if remember_line:
                if len(remember_line) > 1:
                    self.pages[page_number - 1][remember_line[0]]["text"]=(
                    " ".join([ self.pages[page_number -1][number]["text"] for number in remember_line])
                    )
                    self.pages[page_number - 1][remember_line[0]]["level"] = level
                    del self.pages[page_number - 1][remember_line[1]]
                elif len(remember_line) == 1:
                    self.pages[page_number - 1][remember_line[0]]["level"] = level
                return True
            else:
                return False
        else:
            return True
    def _clean_level(
            self
    ):
        for page in self.pages:
            for line in page:
                line["level"] = 0

    def _add_style(
            self,
            debug=False
    ):
        """根据已获取level等级独立添加样式表"""
        for level in range(self.heading_level):
            occurrence = Counter()
            for page in self.pages:
                for line in page:
                    if line["level"] == level+1:
                        size = line["size"]
                        occurrence[round(size)] += 1
            occurrence_list = sorted(occurrence.items(), key=lambda item:item[1], reverse=True)
            if debug:
                logger.debug(f"检测对应level:{level+1};style:{occurrence_list}")
            if occurrence_list:
                self.style[level+1]={
                    "size":occurrence_list[0][0]
                }
        if debug:
            logger.debug(f"建立样式表{self.style}")

    def _classify_toc(
            self,
            debug = False,
            hint=False
    ):
        toc = self.pymu_pf.get_toc()
        self.heading_level = 1
        for item in toc:
            if item[0] > self.heading_level:
                self.heading_level = item[0]
        toc_signal = 0
        for item in toc:
            page_number:int | None = item[2] if item[2] > 1 else None
            if self._match_heading(
            pattern=item[1],
            page_number=page_number,
            level=item[0]):
                toc_signal += 1
            else:
                if debug:
                    logger.debug(f"未命中toc:{item},已命中数量:{toc_signal}")
        if hint:
            logger.debug(f"标题捕获命中率{toc_signal/len(toc)*100}%")

    def style_classify(
            self,
            debug = False
    ):
        self._check_main_text_font()
        self._classify_toc()
        self._add_style()
        self._clean_level()
        self._classify_toc(debug=debug,hint=True)
        self._add_style(debug=debug)

    """标题切分->格式软切分->大块硬切分"""
    def smart_chunk(
            self,
            debug = False
    ):
        flat_lines = [ line for page in self.pages for line in page]
        cut_chunk = []
        results = []
        for line in flat_lines:
            if line["level"] > 0:
                if len(cut_chunk) == 0:
                    cut_chunk.append(line)
                elif len(cut_chunk) > 0:
                    results.append(cut_chunk)
                    cut_chunk = []
            elif len(cut_chunk) > 0 and line["level"] == 0:
                cut_chunk.append(line)
        return results

    def classify_chunks(
            self,
            debug=False
    ):
        def split_large_chunk_by_font(
                chunk:list,
                split_point:int = 0,
                depth:int = 0
        )->list[list]:
            while split_point < len(chunk):
                if chunk[split_point]["size"] > self.style[0]["size"]:
                    small_chunk: list = chunk[:split_point]
                    text = "\n".join([line["text"] for line in small_chunk])
                    if depth >= 50:
                        return [chunk]
                    if len(text) > 2500:
                        depth += 1
                        chunk = chunk[split_point:]
                        return [small_chunk]+split_large_chunk_by_font(chunk, 0, depth)
                    split_point += 1
                else:
                    split_point += 1
                    continue
            return [chunk]

        len_occurrence = Counter()
        results = self.smart_chunk()
        new_results = []
        for i1,chunk in enumerate(results):
            text = "\n".join([line["text"] for line in chunk])
            if len(text) > 5000:
                split_chunks = split_large_chunk_by_font(chunk=chunk)
                split_chunks = [
                    split_chunks[0][:len(chunk)//2]
                    ,split_chunks[0][len(chunk)//2:]
                ] if len(split_chunks) == 1 else split_chunks

                new_results.extend(split_chunks)
            else:
                new_results.append(chunk)
        self.chunks = new_results
        if debug:
            for chunk in new_results:
                text = "\n".join([line["text"] for line in chunk])
                len_occurrence[len(text)]+=1
            len_occurrence_list = sorted(len_occurrence.items(), key=lambda item:item[0], reverse=True)
            print(len_occurrence_list)

    """plumber获得图片信息-->
        与文本内容进行匹配,并标记-->
        信息交付给pymupdf进行导出
    """
    def _get_imgs(
            self,
            page_number: int
    ) -> dict:
        page = self.plumber_pf.pages[page_number]
        real_images = [img for img in page.images if (img["x1"]-img["x0"])>50 and (img["bottom"]-img["top"]) > 50]
        self.plumber_pf._pages[page_number] = None
        return {
            "images": real_images,
            "page_num": page.page_number,
        }

    def get_fig_info(
            self,
            page_number: int
    ) -> dict:
        imgs = self._get_imgs(page_number)
        caption_results = self._find_caption_for_image(self.pages[page_number], imgs["images"])
        image_refs = []
        for i, img in enumerate(imgs["images"]):
            cr = caption_results[i] if (caption_results and i < len(caption_results)) else None
            image_refs.append({
                "id": cr["image_id"] if cr and cr["image_id"] else f"page{page_number+1}_img{i}",
                "bbox": (img["x0"], img["top"], img["x1"], img["bottom"]),
                "caption": cr["caption"] if cr else "",
                "page_num": page_number+1,
            })
        return {
            "page_num": page_number,
            "image_refs": image_refs
        }

    def _find_caption_for_image(
            self,
            lines: list[dict],
            images: list[dict]
    ) -> list[dict | None]:
        results = []
        for img in images:
            img_top = img["top"]
            candidates = []

            for idx, line in enumerate(lines):
                if not line["y_start"] < img_top:
                    continue
                distance = img_top - line["y_start"]
                candidates.append((idx, distance, line))

            candidates.sort(key=lambda x: x[1])

            matched = None
            for idx, dist, line in candidates:
                img_id = FIGURE_PATTERN.match(line["text"])
                if img_id:
                    matched = {
                        "image_id": "img_" + img_id.group(2) if img_id.group(1) != "Example" else "exm_" + img_id.group(
                            2),
                        "image": img,
                        "caption": line["text"],
                        "caption_idx": idx,
                    }
                    break
                matched = {
                    "image_id": None,
                    "image": img,
                    "caption": None,
                    "caption_idx": idx,
                }
            results.append(matched)
        return results

    def _save_fig(
            self,
            document_id: int,
            doc_name: str,
            all_page_imgs: list[dict],
            save_path: Path
    ) -> list[FigureModel] | None:
        root_dir: Path = Path(__file__).resolve().parent.parent.parent
        doc = self.pymu_pf
        all_image_refs = [image_ref for page_imgs in all_page_imgs  for image_ref in page_imgs["image_refs"]]
        figuremodels = []
        fig_dir: Path = root_dir / save_path / doc_name
        fig_dir.mkdir(parents=True, exist_ok=True)
        for image_ref in all_image_refs:
            fig_path = fig_dir / f"{image_ref['id']}.jpg"
            page_num = image_ref.get("page_num", 1)
            bbox = image_ref["bbox"]
            page = doc[page_num]
            rect = pymupdf.Rect(bbox[0], bbox[1], bbox[2], bbox[3])
            pix = page.get_pixmap(clip=rect, dpi=150)
            pix.save(fig_path)
            #释放内存
            pix= None
            figuremodels.append(
                FigureModel(
                    document_id=document_id,
                    img_path=str(fig_path),
                    figure_content=None
                )
            )
        return figuremodels

    def analyze_figures_stream(
            self,
            document_id: int,
            fig_save_path: Path
    ) -> list[FigureModel] | None:
        """为了避免内存爆炸，必须改成流式处理.
        plumber_pdf存在缓存机制，占用很高内存
        """
        handled_pages = [self.get_fig_info(number) for number in range(len(self.plumber_pf.pages))]
        figure_models = self._save_fig(
            document_id,
            self.handled_pdf_path.name,
            handled_pages,
            fig_save_path
        )
        logger.debug(f"存储图片数量: {len(figure_models)}")
        self.figure_models = figure_models
        return figure_models

    """表格转换文本逻辑，实现每页表格提取与文本转换"""
    def _table_to_markdown(
        self,
        page_number: int,
    ) -> list[str]:
        def _table_iter(
                width:int,
                row:list
        )->str:
            table_lines = str("|")
            remnants_table = []
            for cell in row:
                if cell is None:
                    cell = ""
                cell = str(cell).replace("\n"," ")
                remnants=cell[width:]
                remnants_table.append(remnants) if len(remnants) > 0 else remnants_table.append("")
                table_lines+=cell[:width]+" "*(width-len(cell[:width]))+"|" if cell != "" else " "*width+"|"
            if any(cell for cell in remnants_table):
                table_lines+= "\n"+_table_iter(width,remnants_table)
            return table_lines

        def table_format(
                header:list,
                table:list,
                max_width:int=30,
        )->str | None:
            try:
                width =  max([len(h) for h in header])
                width = max_width if width > max_width else width
                if width < 1:
                    return None
                header_line = _table_iter(width,header)
                mid_line = "|"+"|".join(["="*width for _ in header])+"|"
                table_lines = []
                for row in table:
                    table_lines.append(_table_iter(width,row))
                return "\n".join([header_line,mid_line,*table_lines])
            except Exception as e:
                return None

        table_datas = self.plumber_pf.pages[page_number].extract_tables()
        self.plumber_pf._pages[page_number] = None
        if not table_datas:
            return ""
        results = []
        for table_data in table_datas:
            if isinstance(table_data, list) and len(table_data) > 0:
                if isinstance(table_data[0], list):
                    headers = table_data[0]
                    rows = table_data[1:]
                elif isinstance(table_data[0], dict):
                    headers = list(table_data[0].keys())
                    rows = [[row.get(h, "") for h in headers] for row in table_data]
                else:
                    header,rows = None,None
            elif hasattr(table_data, "headers") and hasattr(table_data, "data"):
                headers = table_data.headers
                rows = table_data.data
            else:
                header,rows = None,None
            res_table = table_format(headers,rows) if headers and rows else None
            results.append(res_table) if res_table else results.append(None)
        return results

    def _merge_table_text(
            self,
    )->bool:
        for page_number in range(len(self.pages)):
            tables = self.plumber_pf.pages[page_number].find_tables() or []
            md_lines = self._table_to_markdown(page_number)
            for table in tables:
                md_line = md_lines.pop(0)
                line_number = 0
                while line_number < len(self.pages[page_number]):
                    if table.bbox[1] < self.pages[page_number][line_number]["y_start"] < table.bbox[3]:
                        del self.pages[page_number][line_number]
                        continue
                    line_number += 1
                if md_line:
                    self.pages[page_number].append({
                        "text": md_line,
                        "x_start": 0,
                        "y_start": table.bbox[1],
                        "size": 12,
                        "char_flags": 0,
                        "color": 255,
                        "level":0,
                        "figure_ref":None,
                        "page_number": page_number,
                    })
            self.pages[page_number].sort(key = lambda t: t["y_start"])
        return True

    def _merge_img_text(
            self
    )->bool:
        for page_number in range(len(self.pages)):
            for line_number in range(len(self.pages[page_number])):
                match = re.match(
                        FIGURE_PATTERN,
                        self.pages[page_number][line_number]["text"]
                )
                if match:
                    img_id = "img_" + match.group(2) if match.group(1) != "Example" else "exm_" + match.group(
                        2)
                    self.pages[page_number][line_number]["figure_ref"]=img_id
                    self.pages[page_number][line_number]["text"] = re.sub(
                    FIGURE_PATTERN,
                    lambda x: f"[img_{x.group(2)}]{x.group(3)}" if x.group(1)
                        != "Example" else f"[exm_{x.group(2)}]{x.group(3)}",
                    self.pages[page_number][line_number]['text']
            )
        return True

    def run_parse(
        self,
        document_id:int,
        document_path:Path,
        save_fig_path:Path
    ):
        self.open_pdf(document_id,document_path)
        self._all_order_pages()
        self._remove_header_rooter()
        self.style_classify()
        self.analyze_figures_stream(document_id,save_fig_path)
        del self.plumber_pf._pages  # 避免清理懒加载后对象失效
        self._merge_table_text()
        self._merge_img_text()
        self.smart_chunk()
        self.classify_chunks()

    def extract_chunks(
            self,
    )->list[dict]:
        results = []
        chunk_idx = 0
        if self.chunks:
            for chunk in self.chunks:
                chunk_idx+=1
                text = "\n".join(line["text"] for line in chunk)
                page_start = chunk[0]["page_number"]
                page_end = chunk[-1]["page_number"]
                document_id = self.document_id
                figure_refs:list[str] = [line["figure_ref"] for line in chunk if line["figure_ref"]]
                results.append({
                    "document_id": document_id,
                    "chunk_idx": chunk_idx,
                    "page_start": page_start,
                    "page_end": page_end,
                    "context": text,
                    "figure_refs": figure_refs
                })
            return results
        else:
            return []

    def extract_figures(
            self
    )->list[FigureModel]:
        if self.figure_models:
            return self.figure_models
        else:
            return []

