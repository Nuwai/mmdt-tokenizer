from .types import Chunk
from .config import FUN_TAG, SPECIAL_ADJ, PUNCT_WT_ENDING
from typing import List, Tuple

Span = Tuple[int, int]

def collapse_to_phrase_chunks(chunks: List[List["Chunk"]]):
    """
    Returns: List of sentences, each sentence is a List[Chunk],
    where each Chunk is a collapsed "phrase".
    """
    out: List[List[Chunk]] = []
    tokens : List[List[str]] = []

    for sent in chunks:
        if not sent:
            out.append([])
            tokens.append([])
            continue

        phrase_chunks: List[Chunk] = []
        surface: List[str] = []
        buf_text = []
        buf_start= None
        buf_end = None

        def flush_buf():
            nonlocal buf_text, buf_start, buf_end
            if not buf_text or buf_start is None or buf_end is None:
                return
            phrase_text = "".join(buf_text)
            phrase_chunks.append(Chunk(span=(buf_start, buf_end), text=phrase_text, tag="RAW"))
            surface.append(phrase_text)

            buf_text = []
            buf_start = None
            buf_end = None

        for ch in sent:
            tag = ch.tag
            txt = ch.text
            s0, s1 = ch.span

            if tag == "PUNCT":
                if surface and txt == "။":
                    flush_buf()
                    phrase_chunks.append(Chunk(span=ch.span, text=txt, tag="PUNCT"))
                    surface.append(txt)
                else:
                    flush_buf()
                continue

            if tag in FUN_TAG:
                if txt in SPECIAL_ADJ:
                    # include in current phrase, then flush immediately
                    if buf_start is None: buf_start = s0
                    buf_end = s1
                    buf_text.append(txt)
                    flush_buf()
                else:
                    flush_buf()
                    phrase_chunks.append(Chunk(span=ch.span, text=txt, tag=tag))
                    surface.append(txt)
                continue

            # --- normal token: add to current phrase ---
            if buf_start is None:
                buf_start = s0
            buf_end = s1
            buf_text.append(txt)

        flush_buf()
        phrase_chunks = [pc for pc in phrase_chunks if pc.text not in PUNCT_WT_ENDING]
        
        out.append(phrase_chunks)
        all_tokens = [t for t in surface if t not in PUNCT_WT_ENDING]
        tokens.append(all_tokens)

    return out, tokens




# def collapse_to_phrases(chunks):
#     sentences = []
#     def flush():
#         if buf:
#             surface.append("".join(buf))
#             buf.clear()

#     for sent in chunks: 
#         surface: List[str] = []
#         buf: List[str] = []

#         for ch in sent:
#             tag = getattr(ch, "tag", None)
#             txt = getattr(ch, "text", "") 
            
#             if tag == "PUNCT":
#                 # skip punctuation except ။ (to mark the end of sentence)
#                 if surface and txt == "။": surface.append(txt)
#                 flush()
#                 continue

#             if tag in FUN_TAG:
#                 if txt in SPECIAL_ADJ: 
#                     buf.append(txt)
#                     flush()
#                 else:
#                     flush()
#                     surface.append(txt)
#                 continue
            
#             buf.append(txt) 

        
#         # push remaining one
#         flush()
#         PUNCT_WT_ENDING = {" ", "", ",", "?", "!"}
#         all_tokens = [t for t in surface if t not in PUNCT_WT_ENDING]
    
#         sentences.append(all_tokens)
#     return sentences
