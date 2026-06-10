
import base64
import io
import os

from dotenv import load_dotenv

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

vision_llm = ChatOpenAI(
    model=os.getenv(
        "OPENAI_CHAT_MODEL",
        "gpt-4o"
    ),
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_image_caption(
    image_b64: str
) -> str:

    try:

        msg = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": """
                    Describe this image in detail.

                    If it is:
                    - chart → explain chart
                    - graph → explain trend
                    - table → explain columns
                    - screenshot → explain contents

                    Keep response concise.
                    """
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url":
                        f"data:image/png;base64,{image_b64}"
                    }
                }
            ]
        )

        response = vision_llm.invoke([msg])

        return response.content

    except Exception as e:

        print(
            f"Caption Error: {e}"
        )

        return "Image detected"


def parse_document(
    file_path: str
):

    pipeline_options = PdfPipelineOptions(
        do_ocr=False,
        do_table_structure=True,
        generate_picture_images=True,
        accelerator_options=AcceleratorOptions(
            device=AcceleratorDevice.CPU
        )
    )

    converter = DocumentConverter(
        allowed_formats=[
            InputFormat.PDF
        ],
        format_options={
            InputFormat.PDF:
            PdfFormatOption(
                pipeline_options=pipeline_options
            )
        }
    )

    result = converter.convert(
        file_path
    )

    doc = result.document

    chunks = []

    current_section = None

    source_file = os.path.basename(
        file_path
    )

    for item in doc.iterate_items():

        if isinstance(item, tuple):
            node, _ = item
        else:
            node = item

        label = str(
            getattr(
                node,
                "label",
                ""
            )
        ).lower()

        prov = getattr(
            node,
            "prov",
            None
        )

        page_number = (
            prov[0].page_no
            if prov
            else None
        )
        #print(f"Label={label}, Page={page_number}")

        metadata = {
            "page_number":
            page_number,

            "source_file":
            source_file,

            "element_type":
            label,

            "section":
            current_section
        }

        # -------------------
        # HEADINGS
        # -------------------

        if (
            "section_header" in label
            or label == "title"
        ):

            text = getattr(
                node,
                "text",
                ""
            ).strip()

            if text:

                current_section = text

                chunks.append(
                    {
                        "content": text,
                        "content_type": "text",
                        "metadata": metadata
                    }
                )

        # -------------------
        # TABLES
        # -------------------

        elif "table" in label:

            table_text = ""

            try:

                if hasattr(
                    node,
                    "export_to_dataframe"
                ):

                    df = node.export_to_dataframe(doc)

                    if (
                        df is not None
                        and not df.empty
                    ):

                        table_text = (
                            df.to_string(
                                index=False
                            )
                        )

            except Exception:
                pass

            if table_text:

                chunks.append(
                    {
                        "content":
                        table_text,

                        "content_type":
                        "table",

                        "metadata":
                        metadata
                    }
                )

        # -------------------
        # IMAGES
        # -------------------

        elif (
            "picture" in label
            or "figure" in label
            or label == "chart"
        ):

            image_b64 = None

            try:

                if hasattr(
                    node,
                    "get_image"
                ):

                    img = node.get_image(
                        doc
                    )

                    if img:

                        buffer = io.BytesIO()

                        img.save(
                            buffer,
                            format="PNG"
                        )

                        image_b64 = (
                            base64
                            .b64encode(
                                buffer.getvalue()
                            )
                            .decode()
                        )

            except Exception:
                pass

            if image_b64:
                caption = (
                    generate_image_caption(
                        image_b64
                    )
                )

                # Skip images that are actually tables
                caption_lower = caption.lower()

                if (
                    "table" in caption_lower
                    or "row" in caption_lower
                    or "column" in caption_lower
                    or "rows" in caption_lower
                    or "columns" in caption_lower
                ):
                    continue

                metadata[
                    "image_base64"
                ] = image_b64

                chunks.append(
                    {
                        "content":
                        caption,

                        "content_type":
                        "image",

                        "metadata":
                        metadata
                    }
                )
                print(f"IMAGE DETECTED | Page={page_number}")
                print(f"CAPTION = {caption}")

        # -------------------
        # NORMAL TEXT
        # -------------------

        else:

            text = getattr(
                node,
                "text",
                ""
            )

            if (
                text
                and text.strip()
            ):

                chunks.append(
                    {
                        "content":
                        text.strip(),

                        "content_type":
                        "text",

                        "metadata":
                        metadata
                    }
                )

    return chunks